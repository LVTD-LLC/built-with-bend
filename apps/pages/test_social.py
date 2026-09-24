"""Regression coverage for public share previews and bundled artwork."""

from html.parser import HTMLParser
from pathlib import Path
from struct import unpack
from urllib.parse import urlsplit

import pytest
from django.conf import settings
from django.contrib.staticfiles import finders

from apps.directory.models import Project
from apps.pages.services import list_blog_posts
from apps.pages.views import get_docs_navigation

pytestmark = pytest.mark.django_db


class HeadParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.metadata = {}
        self.titles = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.titles += 1
        if tag == "meta":
            key = attrs.get("property") or attrs.get("name")
            self.metadata.setdefault(key, []).append(attrs.get("content"))


def assert_preview(response, origin, card):
    assert response.status_code == 200
    head = HeadParser()
    head.feed(response.content.decode())
    assert head.titles == 1
    assert len(head.metadata["description"]) == 1
    for key in (
        "og:title",
        "og:description",
        "og:url",
        "og:image",
        "og:image:alt",
        "og:site_name",
        "og:type",
        "twitter:card",
        "twitter:title",
        "twitter:description",
        "twitter:image",
        "twitter:image:alt",
    ):
        assert len(head.metadata[key]) == 1, key
        assert head.metadata[key][0], key
    assert head.metadata["twitter:card"] == ["summary_large_image"]
    assert head.metadata["og:image"] == [f"{origin}/static/social/{card}.png"]
    assert head.metadata["twitter:image"] == head.metadata["og:image"]
    assert head.metadata["og:url"][0].startswith(origin + "/")
    assert "?" not in head.metadata["og:url"][0]
    assert head.metadata["og:image:width"] == ["1200"]
    assert head.metadata["og:image:height"] == ["630"]
    assert "osig.app" not in response.content.decode()
    return head.metadata


@pytest.mark.parametrize(
    ("url", "card"),
    [
        ("/?source=github&q=example", "directory"),
        ("/submit/", "submit"),
        ("/submitted/", "submit"),
        ("/pricing", "directory"),
        ("/privacy-policy", "directory"),
        ("/terms-of-service", "directory"),
        ("/blog/", "blog"),
    ],
)
def test_public_page_previews(client, settings, url, card):
    settings.SITE_URL = "https://canonical.example/"
    settings.STRIPE_SECRET_KEY = ""
    assert_preview(client.get(url), "https://canonical.example", card)


def test_all_published_guides_and_posts_have_previews(client):
    origin = settings.SITE_URL.rstrip("/")
    for category in get_docs_navigation():
        for page in category["pages"]:
            metadata = assert_preview(client.get(page["url"]), origin, "guides")
            assert page["title"] in metadata["og:title"][0]
    for post in list_blog_posts():
        card = Path(urlsplit(post.image_url).path).stem
        metadata = assert_preview(client.get(post.get_absolute_url()), origin, card)
        assert metadata["og:title"] == [post.title]
        assert metadata["og:type"] == ["article"]


def test_project_preview_escapes_content_and_hides_drafts(client, settings):
    settings.SITE_URL = "https://canonical.example"
    project = Project.objects.create(
        title='A "long" title & <markup>',
        description='A description with "quotes" & <tags>. ' * 20,
        canonical_url="https://example.com/build",
        status=Project.Status.PUBLISHED,
    )
    metadata = assert_preview(
        client.get(project.get_absolute_url()), settings.SITE_URL, "directory"
    )
    assert metadata["og:title"] == [f"{project.title} — Built with Bend"]
    assert len(metadata["og:description"][0]) <= 200
    assert metadata["og:url"] == [settings.SITE_URL + project.get_absolute_url()]
    project.status = Project.Status.DRAFT
    project.save()
    assert client.get(project.get_absolute_url()).status_code == 404


def test_bundled_social_artwork_is_available_to_staticfiles():
    for name in ("directory", "blog", "guides", "submit", "bend-2-projects"):
        source = Path(settings.BASE_DIR) / "frontend" / "src" / "social" / f"{name}.png"
        image = source.read_bytes()
        assert image[:8] == b"\x89PNG\r\n\x1a\n"
        assert unpack(">II", image[16:24]) == (1200, 630)
        assert len(image) < 1_000_000
        built = finders.find(f"social/{name}.png")
        assert built and Path(built).read_bytes() == image
