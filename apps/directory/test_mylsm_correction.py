from datetime import UTC, datetime
from importlib import import_module
from types import SimpleNamespace

from django.apps import apps
from django.db import connection
from django.test import TestCase

from .models import Project
from .sitemaps import ProjectSitemap

correction = import_module("apps.directory.migrations.0008_correct_mylsm_durable_api")


class MyLSMCorrectionTests(TestCase):
    def fixture(self, **overrides):
        return Project.objects.create(
            **{
                "id": correction.PROJECT_ID,
                "slug": "mylsm",
                "title": "MyLSM",
                "description": correction.BEFORE,
                "repository_url": correction.REPOSITORY,
                "canonical_url": correction.REPOSITORY,
                "status": Project.Status.PUBLISHED,
                "published_at": datetime(2026, 9, 23, tzinfo=UTC),
                **overrides,
            }
        )

    def test_corrected_public_api_renders_and_other_catalog_fields_are_preserved(self):
        project = self.fixture()
        project.refresh_from_db()
        original = {
            field.attname: getattr(project, field.attname) for field in project._meta.fields
        }
        editor = SimpleNamespace(connection=connection)
        correction.forwards(apps, editor)
        correction.forwards(apps, editor)
        project.refresh_from_db()
        self.assertEqual(project.description, correction.AFTER)
        for field, value in original.items():
            if field != "description":
                self.assertEqual(getattr(project, field), value)
        response = self.client.get(project.get_absolute_url())
        for text in ("MyLSM.Bytes", "MyLSM.Utf8", "no automatic flush or levelled compaction"):
            self.assertContains(response, text)
        self.assertNotContains(response, "in-memory hub facade")
        self.assertEqual(ProjectSitemap().lastmod(project), datetime(2026, 11, 9, tzinfo=UTC))
        correction.backwards(apps, editor)
        correction.backwards(apps, editor)
        project.refresh_from_db()
        self.assertEqual(project.description, correction.BEFORE)

    def test_editorial_drift_is_preserved_in_both_directions(self):
        project = self.fixture(description="A later editorial revision.")
        for operation in (correction.forwards, correction.backwards):
            with self.assertRaisesMessage(RuntimeError, "description changed"):
                operation(apps, SimpleNamespace(connection=connection))
        project.refresh_from_db()
        self.assertEqual(project.description, "A later editorial revision.")

    def test_changed_repository_identity_is_not_rewritten_or_given_the_content_date(self):
        project = self.fixture(repository_url="https://github.com/example/other")
        with self.assertRaisesMessage(RuntimeError, "identity changed"):
            correction.forwards(apps, SimpleNamespace(connection=connection))
        project.refresh_from_db()
        self.assertEqual(project.description, correction.BEFORE)
        self.assertEqual(ProjectSitemap().lastmod(project), project.published_at)

    def test_missing_record_and_later_publication_are_preserved(self):
        editor = SimpleNamespace(connection=connection)
        correction.forwards(apps, editor)
        correction.backwards(apps, editor)
        self.assertFalse(Project.objects.exists())
        project = self.fixture(published_at=datetime(2026, 11, 12, tzinfo=UTC))
        self.assertEqual(ProjectSitemap().lastmod(project), project.published_at)
