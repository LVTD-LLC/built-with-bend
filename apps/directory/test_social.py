from io import BytesIO

import pytest
from django.urls import reverse
from PIL import Image

from .models import Project
from .social import (
    font,
    project_card_content,
    project_card_version,
    render_project_card,
    text_lines,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def project():
    return Project.objects.create(
        title="Bend SVG Editor",
        description="A vector editor built with Bend 2. Draw, edit, and export SVG graphics.",
        author="Community builder",
        category="tools",
        canonical_url="https://example.com/editor",
        status=Project.Status.PUBLISHED,
    )


def test_project_card_is_png_and_supports_conditional_requests(client, project):
    url = reverse("directory:project_image", args=[project.slug])
    response = client.get(url)
    assert response.status_code == 200
    assert response["Content-Type"] == "image/png"
    image = Image.open(BytesIO(response.content))
    assert image.size == (1200, 630)
    assert image.getpixel((0, 0)) == (251, 248, 244)
    assert len(response.content) < 300_000
    assert "must-revalidate" in response["Cache-Control"]
    assert client.get(url, HTTP_IF_NONE_MATCH=response["ETag"]).status_code == 304
    assert client.get(url, HTTP_IF_NONE_MATCH="W/" + response["ETag"]).status_code == 304
    assert client.head(url).status_code == 200
    assert client.post(url).status_code == 405


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("title", "A new project"),
        ("description", "A new description"),
        ("author", "Another builder"),
        ("category", "games"),
    ],
)
def test_project_edits_change_image_version_and_cached_render(client, project, field, value):
    url = reverse("directory:project_image", args=[project.slug])
    previous = client.get(url)
    old_version = project_card_version(project_card_content(project))
    setattr(project, field, value)
    project.save()
    updated = client.get(url, HTTP_IF_NONE_MATCH=previous["ETag"])
    assert updated.status_code == 200
    assert updated.content != previous.content
    assert updated["ETag"] != previous["ETag"]
    html = client.get(project.get_absolute_url()).content.decode()
    assert f"?v={old_version}" not in html
    assert f"?v={project_card_version(project_card_content(project))}" in html


@pytest.mark.parametrize("status", [Project.Status.DRAFT, Project.Status.ARCHIVED])
def test_unpublishing_hides_images_even_after_cache_warmup(client, project, status):
    url = reverse("directory:project_image", args=[project.slug])
    response = client.get(url)
    project.status = status
    project.save()
    assert client.get(url).status_code == 404
    assert client.get(url, HTTP_IF_NONE_MATCH=response["ETag"]).status_code == 404
    project.delete()
    assert client.get(url).status_code == 404


@pytest.mark.parametrize(
    "text", ["W" * 120, "Long project title " * 20, "Éditeur λ — Привет " * 15]
)
def test_long_text_stays_inside_pixel_budget(text):
    face = font(48, "bold")
    lines = text_lines(text, face, 800, 3)
    assert 1 <= len(lines) <= 3
    assert all(face.getlength(line) <= 800 for line in lines)
    assert Image.open(
        BytesIO(render_project_card((text[:120], text * 8, text[:120], "Tools")))
    ).size == (1200, 630)


def test_empty_description_and_author_render(project):
    project.description = ""
    project.author = ""
    content = project_card_content(project)
    assert Image.open(BytesIO(render_project_card(content))).size == (1200, 630)
