from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Project


class ProjectSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"

    def items(self):
        return Project.objects.filter(status=Project.Status.PUBLISHED)

    def lastmod(self, obj):
        return obj.published_at


class PageSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"

    def items(self):
        return ["directory:index", "directory:submit"]

    def location(self, item):
        return reverse(item)
