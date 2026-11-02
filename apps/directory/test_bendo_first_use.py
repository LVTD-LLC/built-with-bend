from datetime import UTC, datetime

from django.test import TestCase

from .editorial import BENDO_FIRST_USE_REPOSITORY
from .models import Category, Project
from .sitemaps import ProjectSitemap


class BendoFirstUseTests(TestCase):
    def test_checked_path_is_source_bound_and_preserves_publication(self):
        published = datetime(2026, 9, 28, tzinfo=UTC)
        project = Project.objects.create(
            slug="bendo",
            title="Bendo",
            description="A pre-alpha Bend 2 web framework.",
            canonical_url=BENDO_FIRST_USE_REPOSITORY,
            repository_url=BENDO_FIRST_USE_REPOSITORY,
            category=Category.LIBRARY,
            status=Project.Status.PUBLISHED,
            published_at=published,
        )
        response = self.client.get(project.get_absolute_url())
        self.assertContains(response, 'id="bendo-first-use-heading"')
        self.assertContains(response, "Hello from Bendo! You asked for /todos/42")
        self.assertContains(response, "not a benchmark, proof-kernel check")
        self.assertLess(
            response.content.index(b'class="sources"'),
            response.content.index(b'id="bendo-first-use-heading"'),
        )
        self.assertEqual(
            response.context["posthog_public_content_path"], project.get_absolute_url()
        )
        self.assertEqual(ProjectSitemap().lastmod(project), datetime(2026, 11, 2, tzinfo=UTC))
        project.refresh_from_db()
        self.assertEqual(project.published_at, published)
        for changes in (
            {"repository_url": "https://example.com/repurposed"},
            {"slug": "another-bendo", "repository_url": BENDO_FIRST_USE_REPOSITORY},
        ):
            with self.subTest(changes=changes):
                Project.objects.filter(pk=project.pk).update(**changes)
                project.refresh_from_db()
                self.assertNotContains(
                    self.client.get(project.get_absolute_url()), "bendo-first-use-heading"
                )
                self.assertEqual(ProjectSitemap().lastmod(project), published)
