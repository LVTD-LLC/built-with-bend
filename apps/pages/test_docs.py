from html.parser import HTMLParser
from urllib.parse import urlsplit

import pytest
from django.urls import reverse

from apps.core.choices import ProfileStates
from apps.pages.views import get_docs_navigation, get_flat_page_list

DOCS_PAGES = get_flat_page_list(get_docs_navigation())


class LinkCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.extend(value for key, value in attrs if key == "href")


@pytest.mark.django_db
def test_docs_home_is_public(client):
    response = client.get(reverse("docs_home"), follow=True)
    assert response.status_code == 200
    assert response.redirect_chain == [("/docs/getting-started/introduction/", 302)]


@pytest.mark.django_db
@pytest.mark.parametrize("page", DOCS_PAGES, ids=lambda page: page["url"])
@pytest.mark.parametrize(
    "reader_state",
    [
        None,
        ProfileStates.FREE,
        ProfileStates.TRIAL_ENDED,
        ProfileStates.CHURNED,
        ProfileStates.SUBSCRIBED,
    ],
    ids=[
        "anonymous",
        "free",
        "trial-ended",
        "churned",
        "subscribed",
    ],
)
def test_docs_pages_and_links_are_public(client, django_user_model, settings, page, reader_state):
    settings.SITE_URL = "https://docs.example.test"
    if reader_state is not None:
        user = django_user_model.objects.create_user(
            username="docs-reader", email="private-reader@example.com"
        )
        profile = user.profile
        profile.state = reader_state
        profile.save(update_fields=["state"])
        assert profile.has_active_subscription == (reader_state == ProfileStates.SUBSCRIBED)
        client.force_login(user)

    response = client.get(page["url"])
    assert response.status_code == 200
    content = response.content.decode()
    assert 'content="index, follow"' in content
    assert f'href="https://docs.example.test{page["url"]}"' in content
    assert "data-docs-page" in content
    assert "private-reader@example.com" not in content
    assert "Deployment" not in content
    assert "Example Feature" not in content
    assert "{{" not in response.context["content"]
    if reader_state is None:
        assert 'href="/submit/"' in content
        assert 'href="/accounts/signup/"' not in content
        assert 'href="/accounts/logout/"' not in content
        # Operator access may be documented, but public signup is not advertised.

    links = LinkCollector()
    links.feed(content)
    for link in links.links:
        if link.startswith("/docs/"):
            assert client.get(urlsplit(link).path, follow=True).status_code == 200, link


@pytest.mark.django_db
@pytest.mark.parametrize(
    "path",
    [
        "/docs/deployment/environment-variables/",
        "/docs/deployment/render-deployment/",
        "/docs/getting-started/local-terminal-development/",
        "/docs/getting-started/design-system/",
        "/docs/features/example_feature/",
        "/docs/missing/page/",
        "/docs/api-reference/missing/",
    ],
)
def test_retired_and_unknown_docs_are_not_served(client, path):
    assert client.get(path).status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,path",
    [
        ("get", "/home"),
        ("get", "/settings"),
        ("post", "/settings/api-key/rotate/"),
        ("post", "/delete-account/"),
    ],
)
def test_public_docs_do_not_open_protected_website_actions(client, method, path):
    response = getattr(client, method)(path)
    assert response.status_code == 302
    assert "/accounts/login/" in response["Location"]


@pytest.mark.django_db
@pytest.mark.parametrize("path", ["/api/user", "/api/user/settings"])
def test_public_docs_do_not_open_authenticated_api(client, path):
    assert client.get(path).status_code == 401


@pytest.mark.django_db
def test_all_public_docs_are_in_sitemap(client, settings):
    settings.SITE_URL = "https://docs.example.test"
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    content = response.content.decode()
    assert DOCS_PAGES
    for page in DOCS_PAGES:
        assert f"<loc>https://docs.example.test{page['url']}</loc>" in content
    assert "/docs/deployment/" not in content


def test_docs_navigation_uses_product_guides_and_frontmatter_titles():
    navigation = get_docs_navigation()
    assert [section["category_slug"] for section in navigation] == [
        "getting-started",
        "features",
        "api-reference",
    ]
    assert navigation[0]["pages"][0]["title"] == "Start here"
    assert navigation[-1]["category"] == "API Reference"
