from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from built_with_bend.sitemaps import ConfiguredSitemapMixin

from .discovery import BEND2_DISCOVERY_ADDED_AT, has_bend2_discovery
from .editorial import (
    BROWSER_EXERCISE_ADDED_AT,
    EDITOR_GUIDE_ADDED_AT,
    EDITOR_GUIDE_PROJECTS,
    HTTP_SERVER_DEMO_ADDED_AT,
    JENDHUB_DESTINATIONS_RESTORED_AT,
    KNOT_FIRST_USE_ADDED_AT,
    KNOT_RELEASE_CORRECTED_AT,
    NEOVIM_FIRST_USE_ADDED_AT,
    PACKAGE_GUIDE_ADDED_AT,
    has_browser_exercise,
    has_http_server_note,
    has_jendhub_destinations,
    has_knot_first_use,
    has_neovim_first_use,
    has_package_guide,
)
from .models import Project


class ProjectSitemap(ConfiguredSitemapMixin, Sitemap):
    protocol = "https"
    changefreq = "weekly"

    def items(self):
        return Project.objects.filter(status=Project.Status.PUBLISHED)

    def lastmod(self, obj):
        content_date = self.content_lastmod(obj)
        if has_bend2_discovery(obj):
            return (
                max(content_date, BEND2_DISCOVERY_ADDED_AT)
                if content_date
                else BEND2_DISCOVERY_ADDED_AT
            )
        return content_date

    def content_lastmod(self, obj):
        if has_knot_first_use(obj):
            return (
                max(obj.published_at, KNOT_FIRST_USE_ADDED_AT)
                if obj.published_at
                else KNOT_FIRST_USE_ADDED_AT
            )
        if has_neovim_first_use(obj):
            return (
                max(obj.published_at, NEOVIM_FIRST_USE_ADDED_AT)
                if obj.published_at
                else NEOVIM_FIRST_USE_ADDED_AT
            )
        if has_browser_exercise(obj):
            return (
                max(obj.published_at, BROWSER_EXERCISE_ADDED_AT)
                if obj.published_at
                else BROWSER_EXERCISE_ADDED_AT
            )
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
                max(obj.published_at, HTTP_SERVER_DEMO_ADDED_AT)
                if obj.published_at
                else HTTP_SERVER_DEMO_ADDED_AT
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
