from datetime import UTC, datetime

from django.test import TestCase

from .editorial import HTTP_SERVER_REPOSITORY
from .models import Category, Project
from .sitemaps import ProjectSitemap


class HttpServerNoteTests(TestCase):
    def project(self, slug="bend-http-server", **overrides):
        return Project.objects.create(
            slug=slug,
            title="Bend HTTP Server",
            description="An HTTP server experiment.",
            canonical_url=f"https://example.com/{slug}",
            **{
                "repository_url": HTTP_SERVER_REPOSITORY,
                "category": Category.TOOL,
                "status": Project.Status.PUBLISHED,
                "published_at": datetime(2026, 9, 24, tzinfo=UTC),
                **overrides,
            },
        )

    def test_source_specific_note_preserves_actions_and_public_identity(self):
        project = self.project()
        response = self.client.get(project.get_absolute_url())
        self.assertContains(response, "Before you run this HTTP server")
        self.assertContains(response, "Try a smaller, local HTTP example")
        self.assertContains(response, "A running HTTP response is not a passing proof")
        self.assertContains(response, "79df8d9c40722ee9507a1e253f283b51025f9d6c")
        self.assertLess(
            response.content.index(b'class="sources"'),
            response.content.index(b'id="http-server-demo-heading"'),
        )
        self.assertContains(response, 'datetime="2026-10-15"')
        self.assertContains(response, "Bend 2.0.35")
        self.assertContains(response, "not a verified one-line fix")
        self.assertContains(
            response, "separate <code>bend PROOF.bend --verdict</code> check passes"
        )
        self.assertContains(response, 'data-posthog-outbound="repository"')
        self.assertEqual(
            response.context["posthog_public_content_path"], project.get_absolute_url()
        )
        self.assertLess(
            response.content.index(b'class="project-actions"'),
            response.content.index(b'id="http-server-note-heading"'),
        )
        self.assertLess(
            response.content.index(b'id="http-server-note-heading"'),
            response.content.index(b'class="sources"'),
        )

    def test_note_and_editorial_date_require_both_slug_and_repository(self):
        renamed = self.project("other-http-server")
        repurposed = self.project(repository_url="https://github.com/example/different-server")
        sitemap = ProjectSitemap()
        for project in (renamed, repurposed):
            with self.subTest(slug=project.slug):
                self.assertNotContains(
                    self.client.get(project.get_absolute_url()), "http-server-note-heading"
                )
                self.assertNotContains(
                    self.client.get(project.get_absolute_url()), "http-server-demo-heading"
                )
                self.assertEqual(sitemap.lastmod(project), project.published_at)

    def test_content_date_does_not_change_publication_or_hide_newer_content(self):
        project = self.project()
        self.assertEqual(ProjectSitemap().lastmod(project), datetime(2026, 10, 22, tzinfo=UTC))
        project.refresh_from_db()
        self.assertEqual(project.published_at, datetime(2026, 9, 24, tzinfo=UTC))
        project.published_at = datetime(2026, 10, 25, tzinfo=UTC)
        self.assertEqual(ProjectSitemap().lastmod(project), project.published_at)
        project.published_at = None
        self.assertEqual(ProjectSitemap().lastmod(project), datetime(2026, 10, 22, tzinfo=UTC))

    def test_note_does_not_make_draft_project_public(self):
        project = self.project(status=Project.Status.DRAFT)
        self.assertEqual(self.client.get(project.get_absolute_url()).status_code, 404)
        self.assertNotIn(project, ProjectSitemap().items())
