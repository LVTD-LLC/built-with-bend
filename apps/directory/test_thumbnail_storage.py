"""R2 imports: network boundaries, raster validation, moderation, and reconciliation."""

import io
import socket
from datetime import timedelta
from unittest.mock import Mock

import pytest
from botocore.exceptions import ClientError
from django.core.cache import cache
from django.core.management import call_command
from django.utils import timezone
from PIL import Image

from . import thumbnail_storage as storage
from .models import Project
from .services import create_project

SOURCE = "https://images.example.com/example.png"


@pytest.fixture
def r2(settings):
    settings.THUMBNAIL_R2_ENABLED = True
    settings.THUMBNAIL_R2_PUBLIC_URL = "https://images.builtwithbend.example"
    settings.THUMBNAIL_R2_BUCKET = "test-thumbnails"
    cache.clear()


@pytest.fixture
def png():
    output = io.BytesIO()
    Image.new("RGB", (2000, 1000), "red").save(output, format="PNG")
    return output.getvalue()


@pytest.fixture
def project(db):
    return create_project(
        title="R2 example",
        description="A Bend visual example.",
        website_url="https://example.com/r2",
        thumbnail_url=SOURCE,
        publish=True,
    )


@pytest.fixture
def transport(monkeypatch, png):
    fetch = Mock(return_value=png)
    client = Mock()
    monkeypatch.setattr(storage, "fetch_image", fetch)
    monkeypatch.setattr(storage, "r2_client", lambda: client)
    return fetch, client


def test_normalize_image_is_bounded_static_webp(png):
    data = storage.normalize_image(png)
    with Image.open(io.BytesIO(data)) as image:
        assert image.format == "WEBP"
        assert image.size == (1600, 800)
        assert not image.getexif()
        assert not image.info.get("icc_profile")
        assert not getattr(image, "is_animated", False)


@pytest.mark.parametrize(
    "data",
    [
        b"<svg><script>alert(1)</script></svg>",
        b"<html>Not image</html>",
        b"",
        b"x" * (storage.MAX_BYTES + 1),
    ],
)
def test_reject_non_images_and_oversized_payloads(data):
    with pytest.raises(storage.ThumbnailImportError):
        storage.normalize_image(data)


def test_reject_large_dimensions(monkeypatch, png):
    monkeypatch.setattr(storage, "MAX_PIXELS", 100)
    with pytest.raises(storage.ThumbnailImportError, match="too_many_pixels"):
        storage.normalize_image(png)


@pytest.mark.parametrize(
    "ip",
    [
        "127.0.0.1",
        "10.0.0.1",
        "169.254.169.254",
        "::1",
        "fe80::1",
        "224.0.0.1",
        "::ffff:127.0.0.1",
        "64:ff9b::7f00:1",
    ],
)
def test_private_mixed_dns_answers_are_rejected(monkeypatch, ip):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *a, **k: [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 443)),
        ],
    )
    with pytest.raises(storage.ThumbnailImportError, match="private_address"):
        storage.public_addresses("images.example.com")


def test_tls_connection_pins_ip_but_preserves_hostname(monkeypatch):
    raw = Mock()
    connect = Mock(return_value=raw)
    monkeypatch.setattr(socket, "create_connection", connect)
    connection = storage.PinnedHTTPSConnection("images.example.com", "93.184.216.34", 3)
    context = Mock()
    connection._context = context
    connection.connect()
    connect.assert_called_once_with(("93.184.216.34", 443), 3)
    context.wrap_socket.assert_called_once_with(raw, server_hostname="images.example.com")


def response(status=200, headers=None, body=b"image"):
    result = Mock(status=status)
    result.getheader.side_effect = lambda name, default=None: (headers or {}).get(name, default)
    result.read1.side_effect = [body, b""]
    return result


def test_fetch_revalidates_redirect_before_connecting(monkeypatch):
    addresses = Mock(
        side_effect=[["93.184.216.34"], storage.ThumbnailImportError("private_address")]
    )
    connection = Mock()
    connection.getresponse.return_value = response(
        302, {"Location": "https://internal.example.com/image"}
    )
    factory = Mock(return_value=connection)
    monkeypatch.setattr(storage, "public_addresses", addresses)
    monkeypatch.setattr(storage, "PinnedHTTPSConnection", factory)
    with pytest.raises(storage.ThumbnailImportError, match="private_address"):
        storage.fetch_image(SOURCE)
    assert factory.call_count == 1
    assert addresses.call_count == 2
    connection.close.assert_called_once()


@pytest.mark.parametrize(
    "location",
    [
        "http://example.com/a.png",
        "https://user:pass@example.com/a.png",
        "https://example.com:8080/a.png",
    ],
)
def test_fetch_rejects_redirect_to_insecure_credentialed_or_nonstandard_port(monkeypatch, location):
    from django.core.exceptions import ValidationError

    connection = Mock()
    connection.getresponse.return_value = response(302, {"Location": location})
    factory = Mock(return_value=connection)
    monkeypatch.setattr(storage, "public_addresses", lambda host: ["93.184.216.34"])
    monkeypatch.setattr(storage, "PinnedHTTPSConnection", factory)
    with pytest.raises((storage.ThumbnailImportError, ValidationError)):
        storage.fetch_image(SOURCE)
    assert factory.call_count == 1


@pytest.mark.parametrize(
    "headers,body,error",
    [
        ({"Content-Length": str(storage.MAX_BYTES + 1)}, b"", "image_too_large"),
        ({"Content-Encoding": "gzip"}, b"", "unsupported_encoding"),
        ({}, b"x" * (storage.MAX_BYTES + 1), "image_too_large"),
    ],
)
def test_fetch_body_limits(monkeypatch, headers, body, error):
    connection = Mock()
    connection.getresponse.return_value = response(headers=headers, body=body)
    monkeypatch.setattr(storage, "public_addresses", lambda host: ["93.184.216.34"])
    monkeypatch.setattr(storage, "PinnedHTTPSConnection", lambda *args: connection)
    with pytest.raises(storage.ThumbnailImportError, match=error):
        storage.fetch_image(SOURCE)
    connection.close.assert_called_once()


def test_fetch_success_preserves_query_and_does_not_forward_auth(monkeypatch):
    connection = Mock()
    connection.getresponse.return_value = response(body=b"test-image")
    monkeypatch.setattr(storage, "public_addresses", lambda host: ["93.184.216.34"])
    monkeypatch.setattr(storage, "PinnedHTTPSConnection", lambda *args: connection)
    assert storage.fetch_image(SOURCE + "?size=20") == b"test-image"
    args, kwargs = connection.request.call_args
    assert args == ("GET", "/example.png?size=20")
    assert set(kwargs["headers"]) == {"User-Agent", "Accept", "Accept-Encoding"}
    connection.close.assert_called_once()


def test_r2_import_retains_source_and_publishes_hosted_image(r2, project, transport, client):
    fetch, s3 = transport
    assert project.display_thumbnail_url == ""
    assert storage.import_project_thumbnail(project.pk) == "ready"
    project.refresh_from_db()
    assert project.thumbnail_url == SOURCE
    assert project.thumbnail_status == "ready"
    assert project.display_thumbnail_url.startswith(
        "https://images.builtwithbend.example/projects/"
    )
    assert project.display_thumbnail_url.endswith(".webp")
    uploaded = s3.put_object.call_args.kwargs
    assert uploaded["Bucket"] == "test-thumbnails"
    assert uploaded["ContentType"] == "image/webp"
    assert uploaded["Key"] == project.thumbnail_key
    assert storage.import_project_thumbnail(project.pk) == "unchanged"
    fetch.assert_called_once()
    assert s3.put_object.call_count == 1
    for path in ["/", project.get_absolute_url()]:
        html = client.get(path).content.decode()
        assert project.display_thumbnail_url in html
        assert SOURCE not in html


@pytest.mark.parametrize("state", [Project.Status.DRAFT, Project.Status.ARCHIVED])
def test_unpublished_images_are_not_fetched_or_uploaded(r2, project, transport, state):
    project.status = state
    project.save()
    assert storage.import_project_thumbnail(project.pk) == "skipped"
    transport[0].assert_not_called()
    transport[1].put_object.assert_not_called()


def test_disabled_storage_does_not_fetch(project, transport, settings):
    settings.THUMBNAIL_R2_ENABLED = False
    assert storage.import_project_thumbnail(project.pk) == "disabled"
    transport[0].assert_not_called()


@pytest.mark.parametrize(
    "changes",
    [
        {"status": Project.Status.ARCHIVED},
        {"thumbnail_url": ""},
        {"thumbnail_url": "https://example.com/new.png"},
    ],
)
def test_edit_during_download_prevents_stale_upload(r2, project, transport, png, changes):
    def change(_):
        Project.objects.filter(pk=project.pk).update(**changes)
        return png

    transport[0].side_effect = change
    assert storage.import_project_thumbnail(project.pk) == "stale"
    transport[1].put_object.assert_not_called()


def test_storage_failure_does_not_mark_image_ready_and_retries(r2, project, transport):
    transport[1].put_object.side_effect = ClientError(
        {"Error": {"Code": "AccessDenied"}}, "PutObject"
    )
    assert storage.refresh_thumbnails() == {"ready": 0, "failed": 1, "skipped": 0}
    project.refresh_from_db()
    assert project.thumbnail_status == "failed"
    assert project.thumbnail_error == "storage_unavailable"
    assert project.display_thumbnail_url == ""
    storage.refresh_thumbnails()
    assert transport[0].call_count == 1
    Project.objects.filter(pk=project.pk).update(
        thumbnail_attempted_at=timezone.now() - timedelta(minutes=16)
    )
    transport[1].put_object.side_effect = None
    assert storage.refresh_thumbnails()["ready"] == 1


def test_changed_or_cleared_source_never_shows_previous_image(r2, project, transport):
    storage.import_project_thumbnail(project.pk)
    project.refresh_from_db()
    project.thumbnail_url = "https://example.com/replacement.png"
    project.save()
    assert project.display_thumbnail_url == ""
    assert storage.refresh_thumbnails()["ready"] == 1
    project.refresh_from_db()
    assert project.thumbnail_imported_source == project.thumbnail_url
    project.thumbnail_url = ""
    assert project.display_thumbnail_url == ""
    assert project.thumbnail_status == "none"


def test_reconciliation_is_bounded_and_schedule_idempotent(r2, project, transport):
    from django_q.models import Schedule

    for number in range(6):
        create_project(
            title=f"Build {number}",
            description="Example",
            publish=True,
            website_url=f"https://example.com/{number}",
            thumbnail_url=SOURCE,
        )
    assert storage.refresh_thumbnails(limit=99)["ready"] == 5
    call_command("refresh_thumbnails", "--schedule")
    call_command("refresh_thumbnails", "--schedule")
    assert Schedule.objects.filter(name="Import project thumbnails to R2").count() == 1


def test_r2_api_keeps_source_and_returns_hosted_status(r2, project, transport, client):
    from django.contrib.auth import get_user_model

    curator = get_user_model().objects.create_superuser("r2-curator", "curator@example.com", "test")
    client.force_login(curator)
    pending = client.get(f"/api/v1/projects/{project.pk}").json()
    assert pending["thumbnail_url"] == SOURCE
    assert pending["hosted_thumbnail_url"] == ""
    assert pending["thumbnail_status"] == "pending"
    storage.import_project_thumbnail(project.pk)
    ready = client.get(f"/api/v1/projects/{project.pk}").json()
    assert ready["thumbnail_url"] == SOURCE
    assert ready["hosted_thumbnail_url"].startswith("https://images.builtwithbend.example/")
    assert ready["thumbnail_status"] == "ready"


def test_sdk_configuration_and_put_contract(r2, settings, png, monkeypatch, project):
    from botocore.stub import ANY, Stubber

    settings.THUMBNAIL_R2_ENDPOINT_URL = "https://test-account.r2.cloudflarestorage.com"
    settings.THUMBNAIL_R2_ACCESS_KEY_ID = "unit-test-id"
    settings.THUMBNAIL_R2_SECRET_ACCESS_KEY = "unit-test-secret"
    client = storage.r2_client()
    assert client.meta.region_name == "auto"
    assert client.meta.config.signature_version == "s3v4"
    with Stubber(client) as stub:
        stub.add_response(
            "put_object",
            {"ETag": '"test"'},
            {
                "Bucket": "test-thumbnails",
                "Key": ANY,
                "Body": ANY,
                "ContentType": "image/webp",
                "CacheControl": "public, max-age=31536000, immutable",
            },
        )
        monkeypatch.setattr(storage, "r2_client", lambda: client)
        monkeypatch.setattr(storage, "fetch_image", lambda url: png)
        assert storage.import_project_thumbnail(project.pk) == "ready"
        stub.assert_no_pending_responses()
    client.close()


@pytest.mark.parametrize("ip", ["93.184.216.34", "::ffff:93.184.216.34", "2606:4700:4700::1111"])
def test_public_and_ipv4_mapped_public_dns_answers_are_accepted(monkeypatch, ip):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *a, **k: [
            (
                socket.AF_INET6 if ":" in ip else socket.AF_INET,
                socket.SOCK_STREAM,
                6,
                "",
                (ip, 443),
            ),
        ],
    )
    assert storage.public_addresses("images.example.com") == [ip]
