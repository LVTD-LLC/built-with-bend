from uuid import UUID

from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from ninja import NinjaAPI, Schema
from ninja.errors import HttpError
from ninja.security import HttpBearer, django_auth_superuser
from pydantic import Field

from apps.directory.models import AdminAPIKey, Category, Project
from apps.directory.services import create_project


class AdminBearer(HttpBearer):
    def authenticate(self, request, token):
        key = (
            AdminAPIKey.objects.select_related("user")
            .filter(
                digest=AdminAPIKey.hash_token(token),
                active=True,
                user__is_active=True,
                user__is_superuser=True,
            )
            .first()
        )
        return key.user if key else None


api = NinjaAPI(
    title="Built with Bend · Admin API",
    version="1.0",
    urls_namespace="directory_api",
    auth=[AdminBearer(), django_auth_superuser],
    docs_decorator=staff_member_required,
)


class ProjectIn(Schema):
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=3000)
    author: str = Field(default="", max_length=120)
    category: Category = Category.OTHER
    website_url: str = Field(default="", max_length=1000)
    repository_url: str = Field(default="", max_length=1000)
    sources: list[str] = Field(default_factory=list, max_length=20)
    github_stars: int | None = Field(default=None, ge=0, le=2147483647)
    x_likes: int | None = Field(default=None, ge=0, le=2147483647)
    publish: bool = False


class ProjectOut(Schema):
    id: UUID
    title: str
    slug: str
    github_stars: int | None
    x_likes: int | None
    status: str
    website_url: str
    repository_url: str


@api.post("/projects", response={201: ProjectOut})
def add_project(request, payload: ProjectIn):
    """Create a draft by default. Set publish=true only after editorial review."""
    try:
        project = create_project(**payload.model_dump())
    except ValidationError as exc:
        raise HttpError(422, "; ".join(exc.messages)) from None
    except IntegrityError:
        raise HttpError(409, "A project with that primary URL already exists.") from None
    return 201, project


@api.get("/projects/{project_id}", response=ProjectOut)
def get_project(request, project_id: UUID):
    from django.shortcuts import get_object_or_404

    return get_object_or_404(Project, pk=project_id)


class PopularityIn(Schema):
    x_likes: int | None = Field(default=None, ge=0, le=2147483647)


@api.patch("/projects/{project_id}/popularity", response=ProjectOut)
def update_popularity(request, project_id: UUID, payload: PopularityIn):
    """Record observed X likes, or explicitly clear an unknown count with null."""
    from django.shortcuts import get_object_or_404

    project = get_object_or_404(Project, pk=project_id)
    if "x_likes" in payload.model_fields_set:
        project.x_likes = payload.x_likes
        project.save(update_fields=["x_likes"])
    return project
