from unittest.mock import Mock, patch

import pytest
import requests
from django.test import Client

from .models import Category, Project

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def newsletter_settings(settings):
    settings.NEWSLETTER_LISTMONK_URL = "http://listmonk:9000"
    settings.NEWSLETTER_LIST_UUID = "list-uuid"


def test_landing_signup_and_filtered_catalog(client):
    html = client.get("/").content.decode()
    assert 'action="/newsletter/"' in html
    assert "weekly email" in html
    assert 'type="email"' in html
    assert 'action="/newsletter/"' not in client.get("/?q=compiler").content.decode()


@patch("apps.directory.newsletter.requests.post")
def test_signup_uses_public_double_optin_not_admin_api(post, client):
    post.return_value = Mock(status_code=200)
    post.return_value.json.return_value = {"data": {"has_optin": True}}
    response = client.post("/newsletter/", {"email": "reader@example.com"})
    assert response.status_code == 302
    assert response.url == "/newsletter/thanks/"
    post.assert_called_once_with(
        "http://listmonk:9000/api/public/subscription",
        json={"email": "reader@example.com", "list_uuids": ["list-uuid"]},
        timeout=(3, 10),
        allow_redirects=False,
    )


@patch("apps.directory.newsletter.requests.post")
def test_invalid_email_and_honeypot_do_not_send(post, client):
    assert client.post("/newsletter/", {"email": "invalid"}).status_code == 400
    assert (
        client.post("/newsletter/", {"email": "bot@example.com", "company": "spam"}).status_code
        == 302
    )
    post.assert_not_called()


@patch("apps.directory.newsletter.requests.post")
@pytest.mark.parametrize("failure", [requests.Timeout(), "http", "json", "shape"])
def test_provider_failures_do_not_claim_success(post, client, failure):
    post.return_value = Mock(status_code=200)
    if isinstance(failure, Exception):
        post.side_effect = failure
    elif failure == "http":
        post.return_value.status_code = 503
    elif failure == "json":
        post.return_value.json.side_effect = ValueError()
    else:
        post.return_value.json.return_value = {"data": False}
    response = client.post("/newsletter/", {"email": "reader@example.com"})
    assert response.status_code == 503
    assert b"try again" in response.content


@patch("apps.directory.newsletter.requests.post")
def test_repeat_signup_has_same_response(post, client):
    post.return_value = Mock(status_code=200)
    post.return_value.json.return_value = {"data": {"has_optin": False}}
    assert client.post("/newsletter/", {"email": "reader@example.com"}).status_code == 302


@patch("apps.directory.newsletter.requests.post")
def test_rate_limit_is_bounded(post, client):
    post.return_value = Mock(status_code=200)
    post.return_value.json.return_value = {"data": {"has_optin": True}}
    for _ in range(10):
        assert client.post("/newsletter/", {"email": "reader@example.com"}).status_code == 302
    response = client.post("/newsletter/", {"email": "reader@example.com"})
    assert response.status_code == 429
    assert response["Retry-After"] == "3600"
    assert post.call_count == 10


def test_disabled_newsletter_hides_form_and_rejects_post(client, settings):
    settings.NEWSLETTER_LIST_UUID = ""
    assert b'action="/newsletter/"' not in client.get("/").content
    assert client.post("/newsletter/", {"email": "reader@example.com"}).status_code == 503


def test_csrf_required():
    assert (
        Client(enforce_csrf_checks=True)
        .post("/newsletter/", {"email": "reader@example.com"})
        .status_code
        == 403
    )


@pytest.mark.parametrize("category", Category.values)
@pytest.mark.parametrize("configured", [True, False])
def test_project_signup_respects_configuration(client, settings, category, configured):
    project = Project.objects.create(
        title="A Bend build",
        slug="bend-build",
        description="A useful project.",
        canonical_url="https://example.com/build",
        category=category,
        status=Project.Status.PUBLISHED,
    )
    if not configured:
        settings.NEWSLETTER_LIST_UUID = ""
    response = client.get(project.get_absolute_url())
    assert response.status_code == 200
    html = response.content.decode()
    assert ('action="/newsletter/"' in html) is configured
    if configured:
        assert html.count('class="newsletter-form"') == 1
        assert 'type="email"' in html
        assert 'name="csrfmiddlewaretoken"' in html
        assert "The latest Bend news and projects" in html
        assert "Confirm by email to subscribe" in html
