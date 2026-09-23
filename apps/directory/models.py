import hashlib
import uuid
from urllib.parse import urlsplit

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django.utils import timezone


def validate_public_url(value):
    URLValidator(schemes=["https", "http"])(value)
    parsed = urlsplit(value)
    if parsed.username or parsed.password:
        raise ValidationError("Use a public URL without embedded credentials.")


class Category(models.TextChoices):
    APP = "apps", "Apps & websites"
    GAME = "games", "Games"
    TOOL = "tools", "Developer tools"
    LIBRARY = "libraries", "Libraries"
    RESEARCH = "research", "Research & experiments"
    OTHER = "other", "Other"


class SourceKind(models.TextChoices):
    GITHUB = "github", "GitHub"
    X = "x", "X"
    REDDIT = "reddit", "Reddit"
    WEBSITE = "website", "Website"
    VIDEO = "video", "Video"
    OTHER = "other", "Other"


def source_kind(url):
    host = (urlsplit(url).hostname or "").lower().removeprefix("www.")
    for kind, hosts in [
        ("github", ("github.com",)),
        ("x", ("x.com", "twitter.com")),
        ("reddit", ("reddit.com", "old.reddit.com")),
        ("video", ("youtube.com", "youtu.be", "vimeo.com")),
    ]:
        if host in hosts:
            return kind
    return "website"


class Project(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=120)
    description = models.TextField(max_length=3000)
    author = models.CharField(max_length=120, blank=True)
    category = models.CharField(max_length=20, choices=Category, default=Category.OTHER)
    website_url = models.URLField(max_length=1000, blank=True, validators=[validate_public_url])
    repository_url = models.URLField(max_length=1000, blank=True, validators=[validate_public_url])
    canonical_url = models.URLField(max_length=1000, unique=True, validators=[validate_public_url])
    status = models.CharField(max_length=20, choices=Status, default=Status.DRAFT, db_index=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-featured", "-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("directory:project", args=[self.pk])

    def clean(self):
        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()


class SourceLink(models.Model):
    project = models.ForeignKey(Project, related_name="sources", on_delete=models.CASCADE)
    url = models.URLField(max_length=1000, validators=[validate_public_url])
    kind = models.CharField(max_length=20, choices=SourceKind)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["project", "url"], name="unique_project_source")
        ]

    def __str__(self):
        return self.url


class Submission(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    title = models.CharField(max_length=120)
    description = models.TextField(max_length=3000)
    author = models.CharField(max_length=120, blank=True)
    category = models.CharField(max_length=20, choices=Category, default=Category.OTHER)
    source_url = models.URLField(max_length=1000, validators=[validate_public_url])
    website_url = models.URLField(max_length=1000, blank=True, validators=[validate_public_url])
    repository_url = models.URLField(max_length=1000, blank=True, validators=[validate_public_url])
    contact = models.CharField(
        max_length=250, blank=True, help_text="Private. Never displayed publicly."
    )
    status = models.CharField(max_length=20, choices=Status, default=Status.PENDING, db_index=True)
    review_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    project = models.ForeignKey(Project, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class AdminAPIKey(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    digest = models.CharField(max_length=64, unique=True, editable=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @staticmethod
    def hash_token(token):
        return hashlib.sha256(token.encode()).hexdigest()


class SubmissionLimit(models.Model):
    key = models.CharField(max_length=64, primary_key=True)
    count = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Submission limit until {self.expires_at}"
