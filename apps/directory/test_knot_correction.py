from datetime import UTC, datetime
from importlib import import_module
from types import SimpleNamespace

from django.apps import apps
from django.db import connection
from django.test import TestCase

from .models import Project
from .sitemaps import ProjectSitemap

correction = import_module("apps.directory.migrations.0006_correct_knot_release_status")


class KnotCorrectionTests(TestCase):
    def setUp(self):
        self.editor = SimpleNamespace(connection=connection)

    def project(self, **overrides):
        return Project.objects.create(
            **{
                "id": correction.PROJECT_ID,
                "slug": "knot",
                "title": "Knot",
                "description": correction.BEFORE,
                "repository_url": correction.REPOSITORY,
                "canonical_url": correction.REPOSITORY,
                "status": Project.Status.PUBLISHED,
                "published_at": datetime(2026, 9, 23, tzinfo=UTC),
                **overrides,
            }
        )

    def test_correction_is_idempotent_reversible_and_preserves_catalog_metadata(self):
        project = self.project()
        project.refresh_from_db()
        original = {
            field.attname: getattr(project, field.attname) for field in project._meta.fields
        }
        correction.forwards(apps, self.editor)
        correction.forwards(apps, self.editor)
        project.refresh_from_db()
        self.assertEqual(project.description, correction.AFTER)
        for field, value in original.items():
            if field != "description":
                self.assertEqual(getattr(project, field), value)
        response = self.client.get(project.get_absolute_url())
        self.assertContains(response, "@matheusbbarni/knot")
        self.assertContains(response, "Transpilation is not type-checking")
        self.assertNotContains(response, "no installable release")
        self.assertEqual(ProjectSitemap().lastmod(project).date().isoformat(), "2026-10-28")
        correction.backwards(apps, self.editor)
        project.refresh_from_db()
        self.assertEqual(project.description, correction.BEFORE)

    def test_newer_editorial_copy_is_never_overwritten_in_either_direction(self):
        project = self.project(description="A later editor has updated this description.")
        for operation in (correction.forwards, correction.backwards):
            with self.assertRaisesMessage(RuntimeError, "description changed"):
                operation(apps, self.editor)
        project.refresh_from_db()
        self.assertEqual(project.description, "A later editor has updated this description.")

    def test_changed_identity_is_not_modified(self):
        project = self.project(repository_url="https://example.com/different-knot")
        with self.assertRaisesMessage(RuntimeError, "identity changed"):
            correction.forwards(apps, self.editor)
        project.refresh_from_db()
        self.assertEqual(project.description, correction.BEFORE)

    def test_missing_curated_record_is_safe_on_fresh_installs(self):
        correction.forwards(apps, self.editor)
        correction.backwards(apps, self.editor)
        self.assertFalse(Project.objects.exists())

    def test_content_date_preserves_later_publication_and_unrelated_projects(self):
        later = self.project(published_at=datetime(2026, 10, 30, tzinfo=UTC))
        self.assertEqual(ProjectSitemap().lastmod(later), later.published_at)
        unrelated = self.project(
            id="902a58cf-9de8-46f5-8c3c-e25abc5fed90",
            slug="another-project",
            canonical_url="https://example.com/another",
        )
        self.assertEqual(ProjectSitemap().lastmod(unrelated), unrelated.published_at)
