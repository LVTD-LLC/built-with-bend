from datetime import UTC, datetime
from html.parser import HTMLParser

from django.test import TestCase

from .editorial import MYLSM_REPOSITORY
from .models import Project
from .sitemaps import ProjectSitemap


class SourcePathParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.items = 0

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.append(dict(attrs))
        elif tag == "li":
            self.items += 1


class MyLSMSourcePathTests(TestCase):
    def test_source_path_preserves_catalog_and_analytics_contract(self):
        published = datetime(2026, 9, 23, tzinfo=UTC)
        project = Project.objects.create(
            slug="mylsm",
            title="MyLSM",
            description="Existing curated description.",
            canonical_url=MYLSM_REPOSITORY,
            repository_url=MYLSM_REPOSITORY,
            status=Project.Status.PUBLISHED,
            published_at=published,
        )
        before = {field.attname: getattr(project, field.attname) for field in project._meta.fields}
        response = self.client.get(project.get_absolute_url())
        section = SourcePathParser()
        section.feed(
            response.content.decode()
            .split('id="mylsm-source-path-heading"', 1)[1]
            .split("</section>", 1)[0]
        )
        self.assertLess(
            response.content.index(b'class="sources"'),
            response.content.index(b'id="mylsm-source-path-heading"'),
        )
        self.assertEqual(section.items, 3)
        for link in section.links:
            self.assertTrue(link["href"].startswith(MYLSM_REPOSITORY + "/blob/be7f9066"))
            self.assertEqual(link["data-posthog-outbound"], "source")
            self.assertTrue({"noopener", "noreferrer"}.issubset(link["rel"].split()))
        self.assertEqual(response.context["posthog_public_content_path"], "/projects/mylsm/")
        self.assertEqual(ProjectSitemap().lastmod(project), datetime(2026, 11, 16, tzinfo=UTC))
        project.refresh_from_db()
        self.assertEqual({field: getattr(project, field) for field in before}, before)

    def test_repurposed_identity_does_not_inherit_advice_or_date(self):
        for slug, repository in (
            ("mylsm", "https://example.com/other"),
            ("another-store", MYLSM_REPOSITORY),
        ):
            with self.subTest(slug=slug, repository=repository):
                project = Project.objects.create(
                    slug=slug,
                    title="Other project",
                    repository_url=repository,
                    canonical_url=repository,
                    status=Project.Status.PUBLISHED,
                    published_at=datetime(2026, 9, 23, tzinfo=UTC),
                )
                self.assertNotContains(
                    self.client.get(project.get_absolute_url()), "mylsm-source-path-heading"
                )
                self.assertEqual(ProjectSitemap().lastmod(project), project.published_at)
