import json
from datetime import timedelta
from unittest.mock import patch

import httpx
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from django_q.models import Schedule

from . import tests as directory_tests
from .models import Project
from .popularity import github_repository, refresh_github_stars
from .services import create_project


class CatalogTests(TestCase):
    def build(self, title="Small game", **kwargs):
        return create_project(
            title=title,
            description="Bend project.",
            publish=True,
            repository_url=f"https://github.com/maker/{Project.objects.count()}",
            **kwargs,
        )

    def test_slugs_are_readable_unique_and_stable_with_legacy_redirects(self):
        first = self.build("Hello, Bend!")
        second = self.build("Hello, Bend!")
        self.assertEqual(first.slug, "hello-bend")
        self.assertTrue(second.slug.startswith("hello-bend-"))
        first.title = "New name"
        first.save()
        self.assertEqual(first.slug, "hello-bend")
        self.assertRedirects(
            self.client.get(f"/projects/{first.pk}/"), "/projects/hello-bend/", status_code=301
        )
        first.status = Project.Status.DRAFT
        first.save()
        for url in (first.get_absolute_url(), f"/projects/{first.pk}/"):
            self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(self.client.get("/projects/missing/ ").status_code, 404)

    def test_unicode_and_uuid_titles_produce_working_links(self):
        for title in ("λ", "!!!", "da0436a2-5c40-49dc-be60-bf20592e4b5f"):
            project = self.build(title)
            self.assertTrue(project.slug)
            self.assertEqual(self.client.get(project.get_absolute_url()).status_code, 200)

    def test_popularity_filters_sort_and_null_semantics(self):
        unknown = self.build("Unknown", category="games")
        zero = self.build("Zero", github_stars=0, x_likes=0, category="games")
        popular = self.build("Popular", github_stars=100, x_likes=20, category="games")
        other = self.build("Other", github_stars=10, x_likes=30, category="tools")
        page = self.client.get("/?source=github&category=games&min_stars=0")
        self.assertEqual(list(page.context["page"]), [popular, zero])
        self.assertEqual(
            list(self.client.get("/?sort=stars").context["page"]), [popular, other, zero, unknown]
        )
        self.assertEqual(
            list(self.client.get("/?sort=likes").context["page"]), [other, popular, zero, unknown]
        )
        self.assertEqual(
            list(self.client.get("/?min_stars=10&min_likes=25").context["page"]), [other]
        )
        self.assertEqual(
            self.client.get("/?min_stars=bad&min_likes=9e100&sort=bad").status_code, 200
        )
        self.assertContains(page, "min_stars=0")
        self.assertContains(page, "Rowset")
        self.assertContains(page, "CiteGuild")
        self.assertContains(page, "TastefulKit")
        self.assertContains(page, "Djass")

    def test_source_only_filters_and_deduplicates_repeated_sources(self):
        project = self.build(sources=["https://github.com/maker/a", "https://github.com/maker/b"])
        page = self.client.get("/?source=github")
        self.assertEqual(list(page.context["page"]), [project])
        self.assertEqual(project.source_kinds, [("github", "GitHub")])

    def test_schedule_setup_is_idempotent(self):
        call_command("refresh_github_stars", "--schedule")
        call_command("refresh_github_stars", "--schedule")
        self.assertEqual(Schedule.objects.filter(name="directory-github-stars").count(), 1)

    def test_refresh_targets_github_only_and_preserves_counts_on_failure(self):
        project = self.build(github_stars=12)
        stale = timezone.now() - timedelta(days=2)
        Project.objects.filter(pk=project.pk).update(github_stars_checked_at=stale)
        with patch("apps.directory.popularity.httpx.Client") as client:
            client.return_value.__enter__.return_value.get.return_value = httpx.Response(
                200,
                json={"stargazers_count": 27},
                request=httpx.Request("GET", "https://api.github.com"),
            )
            self.assertEqual(refresh_github_stars()["updated"], 1)
            client.return_value.__enter__.return_value.get.assert_called_once_with(
                "https://api.github.com/repos/maker/0"
            )
            project.refresh_from_db()
            self.assertEqual(project.github_stars, 27)
            self.assertEqual(refresh_github_stars()["updated"], 0)
            Project.objects.filter(pk=project.pk).update(github_stars_checked_at=stale)
            client.return_value.__enter__.return_value.get.return_value = httpx.Response(
                429,
                request=httpx.Request("GET", "https://api.github.com"),
            )
            self.assertEqual(refresh_github_stars()["failed"], 1)
            project.refresh_from_db()
            self.assertEqual(project.github_stars, 27)
            self.assertEqual(project.github_stars_checked_at, stale)
        project.repository_url = "https://github.com.evil.example/maker/repo"
        project.canonical_url = "https://127.0.0.1/private"
        self.assertIsNone(github_repository(project))
        project.repository_url = "https://github.com/../repo"
        self.assertIsNone(github_repository(project))
        cache.delete("directory:github-refresh")


class PopularityAPITests(TestCase):
    setUp = directory_tests.DirectoryTests.setUp
    token = directory_tests.DirectoryTests.token
    post_api = directory_tests.DirectoryTests.post_api

    def test_create_and_update_popularity_requires_admin_and_valid_counts(self):
        self.payload.update(github_stars=17, x_likes=0)
        headers = self.token()
        result = self.post_api(**headers)
        self.assertEqual(result.status_code, 201)
        self.assertEqual(result.json()["github_stars"], 17)
        project = Project.objects.get()
        endpoint = f"/api/v1/projects/{project.pk}/popularity"
        self.assertEqual(
            self.client.patch(
                endpoint, '{"x_likes":5}', content_type="application/json"
            ).status_code,
            401,
        )
        for value, expected in ((-1, 422), (25, 200), (None, 200)):
            response = self.client.patch(
                endpoint, json.dumps({"x_likes": value}), content_type="application/json", **headers
            )
            self.assertEqual(response.status_code, expected)
        project.refresh_from_db()
        self.assertIsNone(project.x_likes)
        self.assertEqual(project.github_stars, 17)


class SlugBackfillTests(TestCase):
    def test_migration_backfills_duplicate_empty_and_uuid_titles_without_losing_rows(self):
        import importlib

        from django.apps import apps
        from django.db import connection

        migration = importlib.import_module(
            "apps.directory.migrations.0002_project_github_stars_project_github_stars_checked_at_and_more"
        )
        titles = ["Same name", "Same name", "!!!", "λ", "da0436a2-5c40-49dc-be60-bf20592e4b5f"]
        for index, title in enumerate(titles):
            create_project(
                title=title,
                description="Preserved description",
                website_url=f"https://example.com/{index}",
            )
        # Exercise the exact historical data function with already distinct slugs;
        # it must preserve every project while normalizing the original titles.
        migration.populate_slugs(apps, connection.schema_editor(atomic=False))
        self.assertEqual(Project.objects.count(), len(titles))
        self.assertEqual(Project.objects.values("slug").distinct().count(), len(titles))
        self.assertTrue(Project.objects.filter(slug="same-name").exists())
        self.assertTrue(Project.objects.filter(slug__startswith="build-da0436a2").exists())
        self.assertEqual(Project.objects.filter(status="draft").count(), len(titles))
