from datetime import UTC, datetime

from django.test import TestCase

from .editorial import EZMCP_FIRST_USE_REPOSITORY
from .models import Category, Project
from .sitemaps import ProjectSitemap


class EzmcpFirstUseTests(TestCase):
    def test_checked_setup_and_dates_follow_reviewed_identity(self):
        published = datetime(2026, 10, 29, tzinfo=UTC)
        project = Project.objects.create(
            slug="ezmcp",
            title="ezmcp",
            description="A Model Context Protocol library for Bend 2.",
            canonical_url=EZMCP_FIRST_USE_REPOSITORY,
            repository_url=EZMCP_FIRST_USE_REPOSITORY,
            category=Category.LIBRARY,
            status=Project.Status.PUBLISHED,
            published_at=published,
        )
        response = self.client.get(project.get_absolute_url())
        self.assertContains(response, "Try the ezmcp stdio demo")
        self.assertContains(response, 'data-posthog-outbound="repository"')
        self.assertEqual(
            response.context["posthog_public_content_path"], project.get_absolute_url()
        )
        self.assertLess(
            response.content.index(b'class="sources"'),
            response.content.index(b'id="ezmcp-first-use-heading"'),
        )
        self.assertEqual(ProjectSitemap().lastmod(project), datetime(2026, 11, 5, tzinfo=UTC))
        self.assertEqual(
            ProjectSitemap().content_lastmod(project), datetime(2026, 11, 5, tzinfo=UTC)
        )
        project.refresh_from_db()
        self.assertEqual(project.published_at, published)
        self.assertEqual(project.description, "A Model Context Protocol library for Bend 2.")
        for changes in (
            {"repository_url": "https://example.com/repurposed"},
            {"slug": "unrelated-tool", "repository_url": EZMCP_FIRST_USE_REPOSITORY},
        ):
            with self.subTest(changes=changes):
                Project.objects.filter(pk=project.pk).update(**changes)
                project.refresh_from_db()
                self.assertNotContains(
                    self.client.get(project.get_absolute_url()), "ezmcp-first-use-heading"
                )
                self.assertNotEqual(
                    ProjectSitemap().lastmod(project), datetime(2026, 11, 5, tzinfo=UTC)
                )
