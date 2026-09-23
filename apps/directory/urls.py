from django.contrib.sitemaps.views import sitemap
from django.urls import path

from . import views
from .sitemaps import PageSitemap, ProjectSitemap

app_name = "directory"
urlpatterns = [
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": {"pages": PageSitemap, "projects": ProjectSitemap}},
        name="sitemap",
    ),
    path("", views.index, name="index"),
    path("submit/", views.submit, name="submit"),
    path("submitted/", views.submitted, name="submitted"),
    path("projects/<uuid:pk>/", views.detail, name="project"),
    path("health/", views.health, name="health"),
    path("robots.txt", views.robots),
]
