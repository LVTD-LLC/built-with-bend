from datetime import UTC, datetime

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from .discovery import BEND2_PROJECTS
from .models import Category, Project
from .sitemaps import ProjectSitemap


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

    def test_reviewed_bend2_peers_keep_the_full_category_browse_ring(self):
        peers = [
            self.project(slug, repository_url=repo, category=Category.TOOL)
            for slug, repo in BEND2_PROJECTS.items()
            if slug != "knot"
        ]
        # These fall immediately after the workshop in the unmodified ring.
        classic = self.project("bend-cli-hello-world", category=Category.TOOL)
        unknown = self.project("bend-devcontainer", category=Category.TOOL)
        hidden = self.project(
            "knot",
            repository_url=BEND2_PROJECTS["knot"],
            category=Category.TOOL,
            status=Project.Status.DRAFT,
        )
        wrong_category = self.project("another-category", category=Category.GAME)
        projects = sorted(peers + [classic, unknown], key=lambda item: item.slug)
        incoming = {project.slug: 0 for project in projects}
        for index, project in enumerate(projects):
            response = self.client.get(project.get_absolute_url())
            related = response.context["related_projects"]
            self.assertEqual(len(related), 3)
            self.assertEqual(len({item.pk for item in related}), 3)
            self.assertIn(projects[(index + 1) % len(projects)], related)
            self.assertNotIn(project, related)
            self.assertNotIn(hidden, related)
            self.assertNotIn(wrong_category, related)
            if project in peers:
                self.assertTrue(all(item in peers for item in related[:2]))
            else:
                self.assertEqual(related, (projects[index + 1 :] + projects[:index])[:3])
            for item in related:
                incoming[item.slug] += 1
                self.assertContains(response, f'href="{item.get_absolute_url()}"')
        self.assertTrue(all(count >= 1 for count in incoming.values()))

    def test_identity_guards_and_sparse_reviewed_pool_fall_back_without_duplicates(self):
        workshop = self.project(
            "bend-2-pocket-workshop",
            repository_url=BEND2_PROJECTS["bend-2-pocket-workshop"],
        )
        lookalike = self.project("bend2-lsp", repository_url="https://example.com/other")
        later = self.project("charlie")
        last = self.project("delta")
        self.assertEqual(
            self.client.get(workshop.get_absolute_url()).context["related_projects"],
            [lookalike, later, last],
        )
        # A reviewed candidate in the wrong category is not a peer.
        self.project("jendhub", repository_url=BEND2_PROJECTS["jendhub"], category=Category.GAME)
        later.slug = "knot"
        later.repository_url = BEND2_PROJECTS["knot"]
        later.save()
        self.assertEqual(
            self.client.get(workshop.get_absolute_url()).context["related_projects"],
            [later, lookalike, last],
        )
        workshop.repository_url = "https://example.com/repurposed"
        workshop.save()
        self.assertEqual(
            self.client.get(workshop.get_absolute_url()).context["related_projects"],
            [lookalike, last, later],
        )

    def test_discovery_content_date_only_applies_to_exact_reviewed_identity(self):
        project = self.project(
            "bend-2-pocket-workshop",
            repository_url=BEND2_PROJECTS["bend-2-pocket-workshop"],
            published_at=datetime(2026, 10, 1, tzinfo=UTC),
        )
        sitemap = ProjectSitemap()
        self.assertEqual(sitemap.lastmod(project), datetime(2026, 10, 31, tzinfo=UTC))
        project.published_at = datetime(2026, 11, 2, tzinfo=UTC)
        self.assertEqual(sitemap.lastmod(project), project.published_at)
        project.published_at = datetime(2026, 10, 1, tzinfo=UTC)
        project.repository_url = "https://example.com/repurposed"
        self.assertEqual(sitemap.lastmod(project), project.published_at)
