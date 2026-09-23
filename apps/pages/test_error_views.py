import asyncio
from unittest.mock import patch

import pytest
from asgiref.testing import ApplicationCommunicator
from django.db import OperationalError


@pytest.fixture(autouse=True)
def error_page_settings(settings):
    settings.DEBUG = False
    settings.STORAGES["staticfiles"]["BACKEND"] = (
        "django.contrib.staticfiles.storage.StaticFilesStorage"
    )


@pytest.mark.parametrize(
    ("path", "destination"),
    [
        ("/blog", "/blog/"),
        ("/docs", "/docs/"),
        ("/docs/getting-started/introduction", "/docs/getting-started/introduction/"),
        ("/accounts/login?next=/settings", "/accounts/login/?next=/settings"),
    ],
)
def test_slash_redirect_survives_unavailable_banner_database(client, path, destination):
    with patch(
        "apps.pages.context_processors.referrer_banner",
        side_effect=OperationalError("the connection is closed"),
    ) as banner:
        response = client.get(path)

    assert response.status_code == 301
    assert response["Location"] == destination
    banner.assert_not_called()


def test_deployed_asgi_error_path_does_not_query_banner_database():
    from built_with_bend.asgi import application

    async def request_route(path, query=b""):
        communicator = ApplicationCommunicator(
            application,
            {
                "type": "http",
                "http_version": "1.1",
                "method": "GET",
                "scheme": "https",
                "path": path,
                "query_string": query,
                "headers": [(b"host", b"testserver")],
                "server": ("testserver", 443),
                "client": ("127.0.0.1", 1234),
            },
        )
        await communicator.send_input({"type": "http.request", "body": b""})
        start = await communicator.receive_output(timeout=5)
        body = b""
        while True:
            message = await communicator.receive_output(timeout=5)
            body += message.get("body", b"")
            if not message.get("more_body", False):
                break
        await communicator.wait(timeout=5)
        return start, body

    async def request_routes():
        return (
            await request_route("/accounts/login", b"next=/settings"),
            await request_route("/not-a-real-page"),
        )

    with patch(
        "apps.pages.context_processors.referrer_banner",
        side_effect=OperationalError("the connection is closed"),
    ) as banner:
        redirect, missing = asyncio.run(request_routes())

    assert redirect[0]["status"] == 301
    assert dict(redirect[0]["headers"])[b"Location"] == b"/accounts/login/?next=/settings"
    assert missing[0]["status"] == 404
    assert b"Page not found" in missing[1]
    banner.assert_not_called()


def test_missing_page_renders_without_database_or_request_context(client):
    with patch(
        "apps.pages.context_processors.referrer_banner",
        side_effect=OperationalError("the connection is closed"),
    ) as banner:
        response = client.get("/not-a-real-page?ref=private-probe")

    assert response.status_code == 404
    assert response["X-Robots-Tag"] == "noindex, follow"
    content = response.content.decode()
    assert "Page not found" in content
    assert 'href="/"' in content
    assert "private-probe" not in content
    assert "SoftwareApplication" not in content
    assert "application/ld+json" not in content
    assert "posthog" not in content.lower()
    assert "chatwoot" not in content.lower()
    assert 'name="robots" content="noindex, follow"' in content
    banner.assert_not_called()
