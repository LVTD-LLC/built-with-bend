from datetime import UTC, datetime

from django.test import TestCase

from .editorial import KNOT_FIRST_USE_REPOSITORY
from .models import Category, Project
from .sitemaps import ProjectSitemap


class KnotFirstUseTests(TestCase):
    def test_observed_binary_limit_follows_reviewed_identity_not_category(self):
        published = datetime(2026, 9, 28, tzinfo=UTC)
        project = Project.objects.create(
            slug="knot",
            title="Knot",
            description="An early native JavaScript toolchain written in Bend 2.",
            canonical_url=KNOT_FIRST_USE_REPOSITORY,
            repository_url=KNOT_FIRST_USE_REPOSITORY,
            category=Category.TOOL,
            status=Project.Status.PUBLISHED,
            published_at=published,
        )
        response = self.client.get(project.get_absolute_url())
        self.assertContains(response, "failed before Knot started")
        self.assertContains(response, 'data-posthog-outbound="repository"')
        self.assertEqual(
            response.context["posthog_public_content_path"], project.get_absolute_url()
        )
        self.assertLess(
            response.content.index(b'class="sources"'),
            response.content.index(b'id="knot-first-use-heading"'),
        )
        self.assertEqual(ProjectSitemap().lastmod(project), datetime(2026, 10, 31, tzinfo=UTC))
        self.assertEqual(
            ProjectSitemap().content_lastmod(project), datetime(2026, 10, 28, tzinfo=UTC)
        )
        project.refresh_from_db()
        self.assertEqual(project.published_at, published)
        self.assertEqual(
            project.description, "An early native JavaScript toolchain written in Bend 2."
        )
        for changes in (
            {"repository_url": "https://example.com/repurposed"},
            {"slug": "unrelated-tool", "repository_url": KNOT_FIRST_USE_REPOSITORY},
        ):
            with self.subTest(changes=changes):
                Project.objects.filter(pk=project.pk).update(**changes)
                project.refresh_from_db()
                self.assertNotContains(
                    self.client.get(project.get_absolute_url()), "knot-first-use-heading"
                )
                self.assertNotEqual(
                    ProjectSitemap().lastmod(project), datetime(2026, 10, 28, tzinfo=UTC)
                )
