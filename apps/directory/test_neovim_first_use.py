from datetime import UTC, datetime

from django.test import TestCase

from .editorial import NEOVIM_FIRST_USE_REPOSITORY
from .models import Category, Project
from .sitemaps import ProjectSitemap


class NeovimFirstUseTests(TestCase):
    def test_source_bound_setup_does_not_leak_to_repurposed_listings(self):
        project = Project.objects.create(
            slug="bend-2-for-neovim",
            title="Bend 2 for Neovim",
            description="Native Lua editing support for Bend 2.",
            canonical_url=NEOVIM_FIRST_USE_REPOSITORY,
            repository_url=NEOVIM_FIRST_USE_REPOSITORY,
            category=Category.TOOL,
            status=Project.Status.PUBLISHED,
            published_at=datetime(2026, 9, 28, tzinfo=UTC),
        )
        response = self.client.get(project.get_absolute_url())
        self.assertContains(response, 'id="neovim-first-use-heading"')
        self.assertContains(response, "#native-package-layout")
        self.assertContains(response, "#neovim-vimpack")
        self.assertContains(response, "not installed or run this plugin")
        self.assertContains(response, ":Bend2CheckWorkspace")
        self.assertContains(response, 'data-posthog-outbound="repository"')
        self.assertEqual(
            response.context["posthog_public_content_path"], project.get_absolute_url()
        )
        self.assertLess(
            response.content.index(b'class="sources"'),
            response.content.index(b'id="neovim-first-use-heading"'),
        )
        self.assertEqual(ProjectSitemap().lastmod(project), datetime(2026, 10, 31, tzinfo=UTC))
        self.assertEqual(
            ProjectSitemap().content_lastmod(project), datetime(2026, 10, 27, tzinfo=UTC)
        )
        project.refresh_from_db()
        self.assertEqual(project.published_at, datetime(2026, 9, 28, tzinfo=UTC))
        for changes in (
            {"repository_url": "https://example.com/repurposed"},
            {"slug": "another-neovim", "repository_url": NEOVIM_FIRST_USE_REPOSITORY},
        ):
            with self.subTest(changes=changes):
                Project.objects.filter(pk=project.pk).update(**changes)
                project.refresh_from_db()
                self.assertNotContains(
                    self.client.get(project.get_absolute_url()), "neovim-first-use-heading"
                )
                self.assertEqual(ProjectSitemap().lastmod(project), project.published_at)
