from datetime import UTC, datetime
from importlib import import_module
from types import SimpleNamespace

from django.apps import apps
from django.db import connection
from django.test import TestCase

from .models import Project, SourceLink
from .sitemaps import ProjectSitemap

repair = import_module("apps.directory.migrations.0007_restore_jendhub_destinations")


class JendHubDestinationTests(TestCase):
    def setUp(self):
        self.editor = SimpleNamespace(connection=connection)

    def fixture(self, **overrides):
        project = Project.objects.create(
            **{
                "id": repair.PROJECT_ID,
                "slug": "jendhub",
                "title": "JendHub",
                "description": "Search Bend definitions.",
                "repository_url": repair.REPOSITORY,
                "canonical_url": repair.REPOSITORY,
                "status": Project.Status.PUBLISHED,
                "published_at": datetime(2026, 10, 9, tzinfo=UTC),
                **overrides,
            }
        )
        source = SourceLink.objects.create(
            id=repair.SOURCE_ID, project=project, url=repair.OLD_SOURCE, kind="github"
        )
        return project, source

    def test_restored_actions_are_idempotent_reversible_and_preserve_other_fields(self):
        project, source = self.fixture()
        project.refresh_from_db()
        original = {f.attname: getattr(project, f.attname) for f in project._meta.fields}
        repair.forwards(apps, self.editor)
        repair.forwards(apps, self.editor)
        project.refresh_from_db()
        source.refresh_from_db()
        self.assertEqual(project.website_url, repair.WEBSITE)
        self.assertEqual(source.url, repair.NEW_SOURCE)
        for field, value in original.items():
            if field != "website_url":
                self.assertEqual(getattr(project, field), value)
        response = self.client.get(project.get_absolute_url())
        self.assertContains(response, f'href="{repair.WEBSITE}"')
        self.assertContains(response, 'data-posthog-outbound="website"')
        self.assertContains(response, f'href="{repair.NEW_SOURCE}"')
        self.assertNotContains(response, repair.OLD_SOURCE)
        self.assertEqual(ProjectSitemap().lastmod(project).date().isoformat(), "2026-10-31")
        repair.backwards(apps, self.editor)
        repair.backwards(apps, self.editor)
        project.refresh_from_db()
        source.refresh_from_db()
        self.assertEqual(project.website_url, "")
        self.assertEqual(source.url, repair.OLD_SOURCE)
        self.assertEqual(ProjectSitemap().lastmod(project).date().isoformat(), "2026-10-31")

    def test_newer_destination_or_changed_identity_is_preserved_before_any_write(self):
        project, source = self.fixture()
        for changes in (
            {"website_url": "https://example.com/new-site"},
            {"repository_url": "https://github.com/example/new-project"},
        ):
            with self.subTest(changes=changes):
                Project.objects.filter(pk=project.pk).update(**changes)
                with self.assertRaises(RuntimeError):
                    repair.forwards(apps, self.editor)
                source.refresh_from_db()
                self.assertEqual(source.url, repair.OLD_SOURCE)
                Project.objects.filter(pk=project.pk).update(
                    website_url="", repository_url=repair.REPOSITORY
                )
        SourceLink.objects.filter(pk=source.pk).update(url="https://example.com/new-source")
        with self.assertRaisesMessage(RuntimeError, "destinations changed"):
            repair.forwards(apps, self.editor)
        project.refresh_from_db()
        self.assertEqual(project.website_url, "")

    def test_missing_record_is_safe_and_drafts_stay_private(self):
        repair.forwards(apps, self.editor)
        repair.backwards(apps, self.editor)
        project, _ = self.fixture(status=Project.Status.DRAFT)
        repair.forwards(apps, self.editor)
        self.assertEqual(self.client.get(project.get_absolute_url()).status_code, 404)
        self.assertNotIn(project, ProjectSitemap().items())

    def test_lastmod_requires_identity_and_preserves_later_publication(self):
        project, _ = self.fixture(website_url=repair.WEBSITE)
        project.published_at = datetime(2026, 11, 2, tzinfo=UTC)
        self.assertEqual(ProjectSitemap().lastmod(project), project.published_at)
        for field, value in (
            ("slug", "another-project"),
            ("repository_url", "https://example.com/other"),
        ):
            original = getattr(project, field)
            setattr(project, field, value)
            project.published_at = datetime(2026, 10, 9, tzinfo=UTC)
            self.assertEqual(ProjectSitemap().lastmod(project), project.published_at)
            setattr(project, field, original)
