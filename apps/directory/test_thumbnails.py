"""Thumbnail ingestion, moderation, validation, and public display contracts."""

import json
from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core import signing
from django.utils import timezone

from .forms import SubmissionForm
from .models import AdminAPIKey, Project, Submission
from .services import approve_submission, create_project

IMAGE = "https://raw.githubusercontent.com/example/game/main/screenshot.png"


@pytest.fixture
def curator(db):
    return get_user_model().objects.create_superuser("image-curator", "curator@example.com", "test")


@pytest.fixture
def headers(curator):
    token = "thumbnail-test-key-not-production"
    AdminAPIKey.objects.create(name="images", user=curator, digest=AdminAPIKey.hash_token(token))
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


def payload(**overrides):
    return {
        "title": "Image example",
        "description": "A Bend game with a screenshot.",
        "website_url": "https://example.com/game",
        **overrides,
    }


def submission_data(**overrides):
    return {
        **payload(),
        "source_url": "https://github.com/example/game",
        "category": "games",
        "confirm": "on",
        "started": signing.dumps(
            {"time": (timezone.now() - timedelta(seconds=5)).timestamp()}, salt="submission"
        ),
        **overrides,
    }


def post_project(client, headers, **overrides):
    return client.post(
        "/api/v1/projects",
        json.dumps(payload(**overrides)),
        content_type="application/json",
        **headers,
    )


@pytest.mark.django_db
@pytest.mark.parametrize("extra", [{}, {"thumbnail_url": ""}, {"thumbnail_url": IMAGE}])
def test_api_optional_thumbnail_round_trip(client, headers, extra):
    response = post_project(client, headers, **extra)
    assert response.status_code == 201
    project = Project.objects.get()
    expected = extra.get("thumbnail_url", "")
    assert project.thumbnail_url == response.json()["thumbnail_url"] == expected
    assert (
        client.get(f"/api/v1/projects/{project.pk}", **headers).json()["thumbnail_url"] == expected
    )
    assert project.status == Project.Status.DRAFT
    assert client.get(project.get_absolute_url()).status_code == 404
    if expected:
        assert expected not in client.get("/").content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "image",
    [
        "javascript:alert(1)",
        "data:image/png;base64,abcd",
        "file:///tmp/image.png",
        "http://example.com/image.png",
        "https://user:password@example.com/image.png",
        "https://127.0.0.1/image.png",
        "https://[::1]/image.png",
        "https://10.0.0.1/image.png",
        "https://169.254.169.254/image.png",
        "https://localhost/image.png",
        "https://host.local/image.png",
        "https://example.com/" + "a" * 2000,
    ],
)
def test_api_and_form_reject_invalid_images(client, headers, image):
    assert post_project(client, headers, thumbnail_url=image).status_code == 422
    form = SubmissionForm(submission_data(thumbnail_url=image))
    assert not form.is_valid()
    assert "thumbnail_url" in form.errors
    assert not Project.objects.exists()


@pytest.mark.django_db
def test_api_null_is_not_an_image(client, headers):
    assert post_project(client, headers, thumbnail_url=None).status_code == 422


@pytest.mark.django_db
@pytest.mark.parametrize("image", ["", IMAGE])
def test_submission_image_stays_private_until_review(client, curator, image):
    response = client.post("/submit/", submission_data(thumbnail_url=image))
    assert response.status_code == 302
    submission = Submission.objects.get()
    assert submission.thumbnail_url == image
    assert submission.status == Submission.Status.PENDING
    assert not Project.objects.exists()
    if image:
        assert image not in client.get("/").content.decode()
    project = approve_submission(submission.pk, curator)
    assert project.thumbnail_url == image
    assert approve_submission(submission.pk, curator).pk == project.pk
    for path in ["/", project.get_absolute_url()]:
        html = client.get(path).content.decode()
        assert ("data-project-thumbnail" in html) == bool(image)
        if image:
            assert image in html
            assert 'referrerpolicy="no-referrer"' in html


@pytest.mark.django_db
@pytest.mark.parametrize(
    "existing,incoming,expected",
    [("", IMAGE, IMAGE), (IMAGE, "", IMAGE), (IMAGE, "https://example.com/other.png", IMAGE)],
)
def test_review_duplicate_fills_missing_image_without_overwriting(
    curator, existing, incoming, expected
):
    project = create_project(**payload(thumbnail_url=existing))
    submission = Submission.objects.create(
        **payload(thumbnail_url=incoming), source_url="https://github.com/example/game"
    )
    assert approve_submission(submission.pk, curator).pk == project.pk
    project.refresh_from_db()
    assert project.thumbnail_url == expected
    assert project.status == Project.Status.PUBLISHED
    assert Project.objects.count() == 1


@pytest.mark.django_db
def test_submission_form_exposes_optional_image_and_admin_can_edit(client, curator):
    assert not SubmissionForm().fields["thumbnail_url"].required
    assert 'name="thumbnail_url"' in client.get("/submit/").content.decode()
    project = create_project(**payload())
    client.force_login(curator)
    response = client.get(f"/admin/directory/project/{project.pk}/change/")
    assert 'name="thumbnail_url"' in response.content.decode()


@pytest.mark.django_db
def test_image_attribute_is_escaped(client):
    image = 'https://example.com/image.png?label="quoted"&width=640'
    project = create_project(**payload(thumbnail_url=image), publish=True)
    html = client.get(project.get_absolute_url()).content.decode()
    assert "label=&quot;quoted&quot;&amp;width=640" in html
    assert 'label="quoted"&width=640' not in html
