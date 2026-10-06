from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from .models import Category, Project


class RelatedProjectTests(TestCase):
    def project(self, slug, **overrides):
        return Project.objects.create(
            slug=slug,
            title=slug.title(),
            description=f"Explore {slug} in Bend.",
            canonical_url=f"https://example.com/{slug}",
            **{
                "category": Category.LIBRARY,
                "status": Project.Status.PUBLISHED,
                "published_at": timezone.now(),
                **overrides,
            },
        )

    def test_category_links_cover_every_published_sibling_and_wrap(self):
        projects = [self.project(slug) for slug in ("alpha", "bravo", "charlie", "delta", "echo")]
        hidden = [
            self.project("draft", status=Project.Status.DRAFT),
            self.project("archived", status=Project.Status.ARCHIVED),
            self.project("game", category=Category.GAME),
        ]
        incoming = {project.slug: 0 for project in projects}
        for index, project in enumerate(projects):
            response = self.client.get(project.get_absolute_url())
            expected = (projects[index + 1 :] + projects[:index])[:3]
            self.assertEqual(response.context["related_projects"], expected)
            for sibling in expected:
                self.assertContains(response, f'href="{sibling.get_absolute_url()}"')
                incoming[sibling.slug] += 1
            for sibling in hidden:
                self.assertNotContains(response, sibling.get_absolute_url())
            self.assertContains(response, 'id="related-projects-heading"')
            self.assertContains(
                response, f'href="{settings.SITE_URL.rstrip("/")}{project.get_absolute_url()}"'
            )
            self.assertEqual(response.content.count(b"<h1>"), 1)
        self.assertEqual(set(incoming.values()), {3})

    def test_singleton_hides_section_and_pair_never_duplicates_or_links_self(self):
        first = self.project("first")
        response = self.client.get(first.get_absolute_url())
        self.assertEqual(response.context["related_projects"], [])
        self.assertNotContains(response, 'id="related-projects-heading"')
        second = self.project("second")
        for project, sibling in ((first, second), (second, first)):
            response = self.client.get(project.get_absolute_url())
            self.assertEqual(response.context["related_projects"], [sibling])
            self.assertContains(response, f'href="{sibling.get_absolute_url()}"', count=1)

    def test_unpublished_detail_stays_private(self):
        project = self.project("private", status=Project.Status.DRAFT)
        self.assertEqual(self.client.get(project.get_absolute_url()).status_code, 404)
