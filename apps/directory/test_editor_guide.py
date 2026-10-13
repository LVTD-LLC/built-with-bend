from datetime import UTC, datetime
from urllib.parse import urlsplit
from xml.etree import ElementTree

from django.test import TestCase
from django.urls import reverse

from .models import Category, Project


class EditorGuideTests(TestCase):
    def project(self, slug, **overrides):
        return Project.objects.create(
            slug=slug,
            title=slug.title(),
            description="A Bend editor tool.",
            canonical_url=f"https://example.com/{slug}",
            **{
                "category": Category.TOOL,
                "status": Project.Status.PUBLISHED,
                "published_at": datetime(2026, 9, 24, tzinfo=UTC),
                **overrides,
            },
        )

    def test_only_covered_listings_link_to_the_live_guide_after_sources(self):
        guide = reverse("blog_post", kwargs={"slug": "bend-2-editor-tools"})
        self.assertEqual(self.client.get(guide).status_code, 200)
        for slug in ("bend2-lsp", "bend-2-for-vs-code-nuxyel"):
            with self.subTest(slug=slug):
                project = self.project(slug)
                response = self.client.get(project.get_absolute_url())
                self.assertContains(response, f'href="{guide}"', count=1)
                self.assertContains(response, "Choosing a Bend 2 editor?")
                self.assertLess(
                    response.content.index(b'class="sources"'),
                    response.content.index(b'class="project-guide"'),
                )
                self.assertContains(response, 'data-posthog-outbound="source"')
        unrelated = self.project("bend-2-language-support-caiowing")
        self.assertNotContains(self.client.get(unrelated.get_absolute_url()), f'href="{guide}"')
        Project.objects.filter(slug="bend2-lsp").update(status=Project.Status.DRAFT)
        self.assertEqual(self.client.get("/projects/bend2-lsp/").status_code, 404)

    def test_sitemap_dates_reflect_editorial_change_without_redating_other_projects(self):
        older = self.project("bend2-lsp")
        newer = self.project(
            "bend-2-for-vs-code-nuxyel", published_at=datetime(2026, 10, 14, tzinfo=UTC)
        )
        unrelated = self.project("another-tool")
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = {
            urlsplit(row.find("s:loc", ns).text).path: row.find("s:lastmod", ns).text
            for row in ElementTree.fromstring(response.content).findall("s:url", ns)
            if row.find("s:lastmod", ns) is not None
        }
        for project, expected in (
            (older, "2026-10-13"),
            (newer, "2026-10-14"),
            (unrelated, "2026-09-24"),
        ):
            self.assertEqual(urls[project.get_absolute_url()], expected)
