from datetime import UTC, datetime
from urllib.parse import urlsplit
from xml.etree import ElementTree

from django.test import TestCase
from django.urls import reverse

from .models import Category, Project


class PackageGuideTests(TestCase):
    def project(self, slug, repository, **overrides):
        return Project.objects.create(
            **{
                "slug": slug,
                "title": slug.title(),
                "description": "A package discovery tool.",
                "repository_url": repository,
                "canonical_url": f"https://example.com/{slug}",
                "category": Category.TOOL,
                "status": Project.Status.PUBLISHED,
                "published_at": datetime(2026, 10, 9, tzinfo=UTC),
                **overrides,
            }
        )

    def test_covered_discovery_tools_link_after_sources_without_relabeling_outbound_actions(self):
        guide = reverse("blog_post", kwargs={"slug": "bend-2-package-imports"})
        self.assertEqual(self.client.get(guide).status_code, 200)
        for slug, repository in (
            ("jendhub", "https://github.com/LeeeeT/JendHub"),
            ("bend-packages", "https://github.com/777genius/bend-packages"),
        ):
            with self.subTest(slug=slug):
                project = self.project(slug, repository)
                response = self.client.get(project.get_absolute_url())
                self.assertContains(response, f'href="{guide}"', count=1)
                self.assertContains(response, "not a package-wide compatibility guarantee")
                self.assertContains(response, 'data-posthog-outbound="repository"')
                self.assertLess(
                    response.content.index(b'class="sources"'),
                    response.content.index(b'id="package-guide-heading"'),
                )
                Project.objects.filter(pk=project.pk).update(
                    repository_url="https://example.com/new"
                )
                self.assertNotContains(
                    self.client.get(project.get_absolute_url()), f'href="{guide}"'
                )
        unrelated = self.project("another-tool", "https://github.com/LeeeeT/JendHub")
        self.assertNotContains(self.client.get(unrelated.get_absolute_url()), f'href="{guide}"')

    def test_sitemap_dates_change_only_for_matching_listings_and_preserve_later_publication(self):
        older = self.project("jendhub", "https://github.com/LeeeeT/JendHub")
        newer = self.project(
            "bend-packages",
            "https://github.com/777genius/bend-packages",
            published_at=datetime(2026, 10, 22, tzinfo=UTC),
        )
        unrelated = self.project("another-tool", "https://example.com/other")
        response = self.client.get("/sitemap.xml")
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        dates = {
            urlsplit(row.find("s:loc", ns).text).path: row.find("s:lastmod", ns).text
            for row in ElementTree.fromstring(response.content).findall("s:url", ns)
            if row.find("s:lastmod", ns) is not None
        }
        for project, expected in (
            (older, "2026-10-31"),
            (newer, "2026-10-22"),
            (unrelated, "2026-10-09"),
        ):
            self.assertEqual(dates[project.get_absolute_url()], expected)
