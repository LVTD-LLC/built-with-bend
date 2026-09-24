import hashlib
from datetime import timedelta

from django.conf import settings
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods, require_safe

from .forms import SubmissionForm
from .models import Category, Project, SourceKind, SubmissionLimit


def source_filter(kind):
    # Include native project URLs even when ingestion omitted a SourceLink.
    hosts = {
        "github": ("github.com",),
        "x": ("x.com", "twitter.com"),
        "reddit": ("reddit.com", "old.reddit.com"),
        "video": ("youtube.com", "youtu.be", "vimeo.com"),
    }
    result = Q(sources__kind=kind)
    if kind == "website":
        result |= ~Q(website_url="")
    for host in hosts.get(kind, ()):
        for field in ("repository_url", "canonical_url", "website_url"):
            for scheme in ("https", "http"):
                result |= Q(**{f"{field}__istartswith": f"{scheme}://{host}/"})
                result |= Q(**{f"{field}__istartswith": f"{scheme}://www.{host}/"})
    return result


def minimum_count(value):
    try:
        return min(max(int(value), 0), 2147483647)
    except (ValueError, TypeError):
        return None


@require_GET
def index(request):
    published = Project.objects.filter(status=Project.Status.PUBLISHED)
    total = published.count()
    projects = published.prefetch_related("sources")
    query = request.GET.get("q", "").strip()[:200]
    category = request.GET.get("category", "")
    source = request.GET.get("source", "")
    category = category if category in Category.values else ""
    source = source if source in SourceKind.values else ""
    stars = minimum_count(request.GET.get("min_stars"))
    likes = minimum_count(request.GET.get("min_likes"))
    sort = request.GET.get("sort", "newest")
    sort = sort if sort in ("newest", "stars", "likes") else "newest"
    if query:
        projects = projects.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(author__icontains=query)
        )
    if stars is not None:
        projects = projects.filter(github_stars__gte=stars)
    if likes is not None:
        projects = projects.filter(x_likes__gte=likes)
    # Each facet counts the current search and the other facet, not itself.
    category_base = projects.filter(source_filter(source)).distinct() if source else projects
    source_base = projects.filter(category=category) if category else projects
    categories = [
        (value, label, category_base.filter(category=value).distinct().count())
        for value, label in Category.choices
    ]
    sources = [
        (value, label, source_base.filter(source_filter(value)).distinct().count())
        for value, label in SourceKind.choices
    ]
    all_categories = category_base.distinct().count()
    all_sources = source_base.distinct().count()
    if category:
        projects = projects.filter(category=category)
    if source:
        projects = projects.filter(source_filter(source)).distinct()
    ordering = ["-featured", "-published_at", "-created_at", "pk"]
    if sort in ("stars", "likes"):
        field = "github_stars" if sort == "stars" else "x_likes"
        ordering = [F(field).desc(nulls_last=True), "-published_at", "pk"]
    page = Paginator(projects.order_by(*ordering), 24).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    return render(
        request,
        "directory/index.html",
        {
            "page": page,
            "total": total,
            "q": query,
            "category": category,
            "source": source,
            "categories": categories,
            "sources": sources,
            "query_params": params.urlencode(),
            "all_categories": all_categories,
            "all_sources": all_sources,
            "min_stars": stars,
            "min_likes": likes,
            "sort": sort,
            "is_filtered": bool(
                query or category or source or stars is not None or likes is not None
            ),
            "heading": dict(SourceKind.choices).get(source, ""),
        },
    )


@require_GET
def detail(request, slug):
    project = get_object_or_404(
        Project.objects.prefetch_related("sources"),
        slug=slug,
        status=Project.Status.PUBLISHED,
    )
    return render(request, "directory/detail.html", {"project": project})


@require_GET
def legacy_detail(request, pk):
    project = get_object_or_404(Project, pk=pk, status=Project.Status.PUBLISHED)
    return redirect(project.get_absolute_url(), permanent=True)


def submission_allowed(request):
    now = timezone.now()
    # REMOTE_ADDR is supplied by the reverse proxy; do not trust client-supplied X-Forwarded-For.
    identity = request.META.get("REMOTE_ADDR", "")
    if settings.TRUST_CAPROVER_PROXY:
        identity = request.META.get("HTTP_X_REAL_IP", identity)
    bucket = now.strftime("%Y%m%d%H")
    key = hashlib.sha256(f"{settings.SECRET_KEY}:{identity}:{bucket}".encode()).hexdigest()
    with transaction.atomic():
        limit, _ = SubmissionLimit.objects.select_for_update().get_or_create(
            key=key, defaults={"expires_at": now + timedelta(hours=2)}
        )
        if limit.count >= 10:
            return False
        limit.count += 1
        limit.save(update_fields=["count"])
    SubmissionLimit.objects.filter(expires_at__lt=now).delete()
    return True


@require_http_methods(["GET", "POST"])
def submit(request):
    form = SubmissionForm(request.POST or None)
    if request.method == "POST":
        if not submission_allowed(request):
            response = render(
                request,
                "directory/submit.html",
                {"form": form, "rate_limited": True},
                status=429,
            )
            response["Retry-After"] = "3600"
            return response
        if form.is_valid():
            form.save()
            return redirect("directory:submitted")
    return render(request, "directory/submit.html", {"form": form})


@require_GET
def submitted(request):
    return render(request, "directory/submitted.html")


@require_GET
def health(request):
    from django.core.cache import cache
    from django.db import connection

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        cache.set("bend:health", True, timeout=10)
        if cache.get("bend:health") is not True:
            return JsonResponse({"status": "unavailable"}, status=503)
        return JsonResponse({"status": "ok", "revision": settings.DEPLOYMENT_REVISION})
    except Exception:
        return JsonResponse({"status": "unavailable"}, status=503)


@require_GET
def worker_health(request):
    from django.core.cache import cache

    try:
        healthy = cache.get(f"bend:worker:{settings.DEPLOYMENT_REVISION}") is True
    except Exception:
        healthy = False
    return JsonResponse(
        {"status": "ok" if healthy else "unavailable", "revision": settings.DEPLOYMENT_REVISION},
        status=200 if healthy else 503,
    )


@require_GET
def robots(request):
    return HttpResponse(
        "User-agent: *\nDisallow: /admin/\nDisallow: /api/\nSitemap: https://builtwithbend.com/sitemap.xml\n",
        content_type="text/plain",
    )


@require_safe
def project_image(request, slug):
    from django.utils.http import parse_etags

    from .social import project_card_content, project_card_version, render_project_card

    # Check publication on every request, including conditional/cache hits.
    project = get_object_or_404(Project, slug=slug, status=Project.Status.PUBLISHED)
    content = project_card_content(project)
    etag = f'"{project_card_version(content)}"'
    etags = parse_etags(request.headers.get("If-None-Match", ""))
    if "*" in etags or etag in [value.removeprefix("W/") for value in etags]:
        response = HttpResponse(status=304)
    else:
        response = HttpResponse(render_project_card(content), content_type="image/png")
    response["ETag"] = etag
    response["Cache-Control"] = "public, max-age=0, must-revalidate"
    response["X-Content-Type-Options"] = "nosniff"
    return response
