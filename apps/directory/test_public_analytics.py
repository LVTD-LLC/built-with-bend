import pytest
from django.urls import reverse

from apps.directory.models import Project

pytestmark = pytest.mark.django_db


def test_only_published_project_view_emits_approved_identity(client, settings):
    settings.POSTHOG_API_KEY = "test-ingestion-token"
    first = Project.objects.create(
        title="First",
        slug="first",
        description="A Bend project",
        canonical_url="https://example.org/first",
        status="published",
    )
    second = Project.objects.create(
        title="Second",
        slug="second",
        description="Another Bend project",
        canonical_url="https://example.org/second",
        status="published",
    )
    for project in (first, second):
        response = client.get(project.get_absolute_url() + "?token=private@example.com")
        assert response.status_code == 200
        assert response.context["posthog_public_content_path"] == project.get_absolute_url()
        assert response.context["posthog_public_content_type"] == "project"
        assert f'data-posthog-public-content-path="{project.get_absolute_url()}"' in response.text
        assert 'data-posthog-route="/projects/:slug/"' in response.text
    first.status = "draft"
    first.save()
    response = client.get(first.get_absolute_url())
    assert response.status_code == 404
    assert "data-posthog-public-content-path" not in response.text


def test_aliases_hubs_and_private_routes_never_emit_public_identity(client, settings):
    settings.POSTHOG_API_KEY = "test-ingestion-token"
    project = Project.objects.create(title="Build", slug="build", status="published")
    alias = client.get(f"/projects/{project.pk}/")
    assert alias.status_code == 301
    for path in ("/", "/submit/", "/admin/login/", "/accounts/login/", "/projects/missing/"):
        response = client.get(path)
        assert "data-posthog-public-content-path" not in response.text


def test_published_article_uses_slashless_identity(client, settings):
    settings.POSTHOG_API_KEY = "test-ingestion-token"
    path = reverse("blog_post", kwargs={"slug": "bend-programming-language"})
    response = client.get(path + "?q=private")
    assert response.status_code == 200
    assert response.context["posthog_public_content_path"] == path
    assert response.context["posthog_public_content_type"] == "article"
    assert f'data-posthog-public-content-path="{path}"' in response.text
    assert 'data-posthog-route="/blog/:slug"' in response.text
    assert "disable_session_recording: true" in response.text
    assert "data-posthog-public-content-path" not in client.get("/blog/missing").text
