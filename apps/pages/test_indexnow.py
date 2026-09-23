import io
import json
import re
from urllib.error import HTTPError, URLError

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.urls import reverse

from apps.pages import indexnow

SITE = "https://example.com"
KEY = "a" * 64


class Response(io.BytesIO):
    def __init__(self, body=b"", status=200, headers=None):
        super().__init__(body)
        self.status = status
        self.headers = headers or {}


def transport(monkeypatch, urls, statuses=(200,), revisions=("new",)):
    posts = []
    codes = iter(statuses)
    deployed = iter(revisions)
    xml = '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    xml += "".join(f"<url><loc>{url}</loc></url>" for url in urls) + "</urlset>"

    def send(req, timeout):
        assert timeout > 0
        if req.full_url == SITE + indexnow.KEY_PATH:
            return Response(KEY.encode(), headers={"X-Deployment-Revision": next(deployed)})
        if req.full_url == SITE + "/sitemap.xml":
            return Response(xml.encode())
        assert req.full_url == indexnow.ENDPOINT
        posts.append(json.loads(req.data))
        code = next(codes)
        if code >= 400:
            raise HTTPError(req.full_url, code, "failure", {}, None)
        return Response(status=code)

    monkeypatch.setattr(indexnow, "urlopen", send)
    monkeypatch.setattr(indexnow.time, "sleep", lambda _: None)
    return posts


@override_settings(SITE_URL=SITE, SECRET_KEY="test-only", DEPLOYMENT_REVISION="new")
def test_public_key_route_is_stable_across_settings_changes(client, settings):
    response = client.get(reverse("indexnow_key"))
    assert response.status_code == 200
    assert re.fullmatch(rb"[a-f0-9]{64}", response.content)
    assert response["Content-Type"] == "text/plain; charset=utf-8"
    assert response["Cache-Control"] == "no-store"
    assert response["X-Deployment-Revision"] == "new"
    assert client.get(reverse("indexnow_key")).content == response.content
    assert response.content.decode() == settings.INDEXNOW_KEY
    settings.SECRET_KEY = "rotated-test-only"
    settings.SITE_URL = "https://another.example.com"
    assert client.get(reverse("indexnow_key")).content == response.content


@pytest.mark.parametrize("status", [200, 202])
@override_settings(SITE_URL=SITE)
def test_command_submits_current_and_removed_urls(monkeypatch, tmp_path, status):
    posts = transport(monkeypatch, [SITE + "/", SITE + "/docs/new/"], statuses=(status,))
    previous = tmp_path / "before.json"
    previous.write_text(json.dumps([SITE + "/", SITE + "/docs/removed/"]))
    output = io.StringIO()
    call_command("submit_indexnow", previous=previous, stdout=output)
    assert posts == [
        {
            "host": "example.com",
            "key": KEY,
            "keyLocation": SITE + indexnow.KEY_PATH,
            "urlList": [SITE + "/", SITE + "/docs/new/", SITE + "/docs/removed/"],
        }
    ]
    assert ("validation pending" in output.getvalue()) == (status == 202)


def test_revision_wait_dry_run_and_protocol_batch_limit(monkeypatch):
    urls = [f"{SITE}/docs/{i}/" for i in range(10_001)]
    posts = transport(monkeypatch, urls, statuses=(200, 202), revisions=("old", "new", "new"))
    assert "Dry run" in indexnow.submit(SITE, expected_revision="new", dry_run=True)
    assert not posts
    indexnow.submit(SITE, expected_revision="new")
    assert [len(post["urlList"]) for post in posts] == [10_000, 1]


@pytest.mark.parametrize(
    "url",
    [
        "https://other.test/",
        SITE + "/?token=private",
        SITE + "/#part",
        "http://example.com/",
        SITE + "/bad\npath",
    ],
)
def test_invalid_sitemap_never_submits(monkeypatch, url):
    posts = transport(monkeypatch, [url])
    with pytest.raises(indexnow.IndexNowError):
        indexnow.submit(SITE)
    assert not posts


@pytest.mark.parametrize("status", [400, 403, 422, 429])
def test_permanent_or_unspecified_rate_limit_stops(monkeypatch, status):
    posts = transport(monkeypatch, [SITE + "/"], statuses=(status,))
    with pytest.raises(indexnow.IndexNowError):
        indexnow.submit(SITE)
    assert len(posts) == 1


def test_transient_failure_retries_and_exhaustion_is_visible(monkeypatch):
    posts = transport(monkeypatch, [SITE + "/"], statuses=(503, 200))
    assert "HTTP 200" in indexnow.submit(SITE)
    assert len(posts) == 2
    attempts = []

    def unavailable(req, timeout):
        attempts.append(req)
        raise URLError("offline")

    monkeypatch.setattr(indexnow, "urlopen", unavailable)
    with pytest.raises(indexnow.IndexNowError, match="four attempts"):
        indexnow.submit(SITE)
    assert len(attempts) == 4


def test_snapshot_cli_is_read_only(monkeypatch, tmp_path):
    posts = transport(monkeypatch, [SITE + "/"])
    snapshot = tmp_path / "before.json"
    monkeypatch.setattr("sys.argv", ["indexnow", "--site-url", SITE, "--snapshot", str(snapshot)])
    indexnow.main()
    assert json.loads(snapshot.read_text()) == [SITE + "/"]
    assert not posts


def test_unfinished_rollout_never_submits(monkeypatch):
    posts = transport(monkeypatch, [SITE + "/"], revisions=("old",) * 30)
    with pytest.raises(indexnow.IndexNowError, match="revision"):
        indexnow.submit(SITE, expected_revision="new")
    assert not posts


def test_short_rate_limit_respects_retry_after(monkeypatch):
    responses = iter(
        [HTTPError(indexnow.ENDPOINT, 429, "rate limit", {"Retry-After": "12"}, None), Response()]
    )
    delays = []

    def send(req, timeout):
        result = next(responses)
        if isinstance(result, HTTPError):
            raise result
        return result

    monkeypatch.setattr(indexnow, "urlopen", send)
    monkeypatch.setattr(indexnow.time, "sleep", delays.append)
    assert indexnow.request(indexnow.ENDPOINT, {"urlList": [SITE + "/"]})[0] == 200
    assert delays == [12]
