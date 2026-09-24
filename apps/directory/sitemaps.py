from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from built_with_bend.sitemaps import ConfiguredSitemapMixin

from .models import Project


class ProjectSitemap(ConfiguredSitemapMixin, Sitemap):
    protocol = "https"
    changefreq = "weekly"

    def items(self):
        return Project.objects.filter(status=Project.Status.PUBLISHED)

    def lastmod(self, obj):
        return obj.published_at


class PageSitemap(ConfiguredSitemapMixin, Sitemap):
    protocol = "https"
    changefreq = "weekly"

    def items(self):
        return ["directory:index", "directory:submit", "blog_posts"]

    def location(self, item):
        return reverse(item)
