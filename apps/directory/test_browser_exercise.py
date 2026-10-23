from datetime import UTC, datetime

from django.test import TestCase
from django.urls import reverse

from .editorial import BROWSER_EXERCISE_REPOSITORY
from .models import Category, Project
from .sitemaps import ProjectSitemap


class BrowserExerciseTests(TestCase):
    def test_exercise_is_source_bound_and_preserves_original_project_identity(self):
        project = Project.objects.create(
            slug="bend-explained",
            title="Bend, Explained",
            description="An interactive language explainer.",
            canonical_url=BROWSER_EXERCISE_REPOSITORY,
            repository_url=BROWSER_EXERCISE_REPOSITORY,
            category=Category.APP,
            status=Project.Status.PUBLISHED,
            published_at=datetime(2026, 10, 1, tzinfo=UTC),
        )
        response = self.client.get(project.get_absolute_url())
        self.assertContains(response, "Try your first proof check in the browser")
        self.assertContains(response, "not the independent")
        self.assertContains(response, "ordinary checker")
        self.assertContains(response, "#works-play")
        guide = reverse("blog_post", kwargs={"slug": "bend-programming-language"})
        self.assertContains(response, f'href="{guide}"')
        self.assertContains(response, 'data-posthog-outbound="repository"')
        self.assertLess(
            response.content.index(b'class="sources"'),
            response.content.index(b'id="browser-exercise-heading"'),
        )
        self.assertEqual(
            response.context["posthog_public_content_path"], project.get_absolute_url()
        )
        self.assertEqual(ProjectSitemap().lastmod(project), datetime(2026, 10, 23, tzinfo=UTC))
        project.refresh_from_db()
        self.assertEqual(project.published_at, datetime(2026, 10, 1, tzinfo=UTC))
        for changes in (
            {"repository_url": "https://example.com/repurposed"},
            {"slug": "different-explainer", "repository_url": BROWSER_EXERCISE_REPOSITORY},
        ):
            with self.subTest(changes=changes):
                Project.objects.filter(pk=project.pk).update(**changes)
                project.refresh_from_db()
                self.assertNotContains(
                    self.client.get(project.get_absolute_url()), "browser-exercise-heading"
                )
                self.assertEqual(ProjectSitemap().lastmod(project), project.published_at)
