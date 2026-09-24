from django.contrib.sitemaps.views import sitemap
from django.urls import path

from built_with_bend.sitemaps import BlogSitemap, DocumentationSitemap

from . import views
from .sitemaps import PageSitemap, ProjectSitemap

app_name = "directory"
urlpatterns = [
    path(
        "sitemap.xml",
        sitemap,
        {
            "sitemaps": {
                "pages": PageSitemap,
                "projects": ProjectSitemap,
                "blog": BlogSitemap,
                "docs": DocumentationSitemap,
            }
        },
        name="sitemap",
    ),
    path("", views.index, name="index"),
    path("submit/", views.submit, name="submit"),
    path("submitted/", views.submitted, name="submitted"),
    path("projects/<uuid:pk>/", views.legacy_detail, name="legacy_project"),
    path("projects/<slug:slug>/og.png", views.project_image, name="project_image"),
    path("projects/<slug:slug>/", views.detail, name="project"),
    path("health/", views.health, name="health"),
    path("health/workers/", views.worker_health, name="worker_health"),
    path("robots.txt", views.robots),
]
