from urllib.parse import urlsplit

from django.conf import settings
from django.contrib import sitemaps
from django.urls import reverse

from apps.pages.services import list_blog_posts
from apps.pages.views import get_docs_navigation, get_flat_page_list


def public_site_url():
    return settings.SITE_URL.rstrip("/")


class ConfiguredSite:
    """Sitemap site object backed by SITE_URL instead of django_site defaults."""

    def __init__(self):
        parsed_url = urlsplit(public_site_url())
        self.domain = parsed_url.netloc
        self.name = self.domain


def configured_sitemap_protocol():
    parsed_url = urlsplit(public_site_url())
    return parsed_url.scheme or "https"


class ConfiguredSitemapMixin:
    """Render sitemap URLs from SITE_URL, not the mutable django_site row."""

    def get_urls(self, page=1, site=None, protocol=None):
        return super().get_urls(
            page=page,
            site=ConfiguredSite(),
            protocol=configured_sitemap_protocol(),
        )


class StaticViewSitemap(ConfiguredSitemapMixin, sitemaps.Sitemap):
    """Generate Sitemap for the site"""

    priority = 0.9

    def items(self):
        """Identify items that will be in the Sitemap

        Returns:
            List: urlNames that will be in the Sitemap
        """
        return [
            "landing",
            "uses",
            "privacy_policy",
            "terms_of_service",
            "pricing",
            "blog_posts",
        ]

    def location(self, item):
        """Get location for each item in the Sitemap

        Args:
            item (str): Item from the items function

        Returns:
            str: Url for the sitemap item
        """
        return reverse(item)


class BlogSitemap(ConfiguredSitemapMixin, sitemaps.Sitemap):
    priority = 0.85
    changefreq = "monthly"

    def items(self):
        return [
            post
            for post in list_blog_posts()
            if not {"noindex", "none"}.intersection(post.robots.lower().replace(",", " ").split())
            and post.canonical_url == f"{public_site_url()}{post.get_absolute_url()}"
        ]

    def location(self, item):
        return item.get_absolute_url()

    def lastmod(self, item):
        return item.updated_at


class DocumentationSitemap(ConfiguredSitemapMixin, sitemaps.Sitemap):
    def items(self):
        return [page["url"] for page in get_flat_page_list(get_docs_navigation())]

    def location(self, item):
        return item


sitemaps = {
    "static": StaticViewSitemap,
    "docs": DocumentationSitemap,
    "blog": BlogSitemap,
}
