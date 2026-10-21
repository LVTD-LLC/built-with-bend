from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from built_with_bend.sitemaps import ConfiguredSitemapMixin

from .editorial import (
    EDITOR_GUIDE_ADDED_AT,
    EDITOR_GUIDE_PROJECTS,
    HTTP_SERVER_CHECKED_AT,
    JENDHUB_DESTINATIONS_RESTORED_AT,
    KNOT_RELEASE_CORRECTED_AT,
    PACKAGE_GUIDE_ADDED_AT,
    has_http_server_note,
    has_jendhub_destinations,
    has_package_guide,
)
from .models import Project


class ProjectSitemap(ConfiguredSitemapMixin, Sitemap):
    protocol = "https"
    changefreq = "weekly"

    def items(self):
        return Project.objects.filter(status=Project.Status.PUBLISHED)

    def lastmod(self, obj):
        if has_package_guide(obj):
            return (
                max(obj.published_at, PACKAGE_GUIDE_ADDED_AT)
                if obj.published_at
                else PACKAGE_GUIDE_ADDED_AT
            )
        if has_jendhub_destinations(obj):
            return (
                max(obj.published_at, JENDHUB_DESTINATIONS_RESTORED_AT)
                if obj.published_at
                else JENDHUB_DESTINATIONS_RESTORED_AT
            )
        if has_http_server_note(obj):
            return (
                max(obj.published_at, HTTP_SERVER_CHECKED_AT)
                if obj.published_at
                else HTTP_SERVER_CHECKED_AT
            )
        if obj.slug == "knot":
            return (
                max(obj.published_at, KNOT_RELEASE_CORRECTED_AT)
                if obj.published_at
                else KNOT_RELEASE_CORRECTED_AT
            )
        if obj.slug in EDITOR_GUIDE_PROJECTS:
            return (
                max(obj.published_at, EDITOR_GUIDE_ADDED_AT)
                if obj.published_at
                else EDITOR_GUIDE_ADDED_AT
            )
        return obj.published_at


class PageSitemap(ConfiguredSitemapMixin, Sitemap):
    protocol = "https"
    changefreq = "weekly"

    def items(self):
        return ["directory:index", "directory:submit", "blog_posts"]

    def location(self, item):
        return reverse(item)
