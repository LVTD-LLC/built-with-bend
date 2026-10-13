from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from built_with_bend.sitemaps import ConfiguredSitemapMixin

from .editorial import EDITOR_GUIDE_ADDED_AT, EDITOR_GUIDE_PROJECTS
from .models import Project


class ProjectSitemap(ConfiguredSitemapMixin, Sitemap):
    protocol = "https"
    changefreq = "weekly"

    def items(self):
        return Project.objects.filter(status=Project.Status.PUBLISHED)

    def lastmod(self, obj):
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
