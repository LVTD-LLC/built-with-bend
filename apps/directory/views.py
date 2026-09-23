import hashlib
from datetime import timedelta

from django.conf import settings
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods

from .forms import SubmissionForm
from .models import Category, Project, SourceKind, SubmissionLimit


@require_GET
def index(request):
    projects = Project.objects.filter(status=Project.Status.PUBLISHED).prefetch_related("sources")
    total = projects.count()
    query = request.GET.get("q", "").strip()[:200]
    category = request.GET.get("category", "")
    source = request.GET.get("source", "")
    if query:
        projects = projects.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(author__icontains=query)
        )
    if category in Category.values:
        projects = projects.filter(category=category)
    if source in SourceKind.values:
        projects = projects.filter(sources__kind=source).distinct()
    page = Paginator(projects, 24).get_page(request.GET.get("page"))
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
            "categories": Category.choices,
            "sources": SourceKind.choices,
            "query_params": params.urlencode(),
        },
    )


@require_GET
def detail(request, pk):
    project = get_object_or_404(
        Project.objects.prefetch_related("sources"),
        pk=pk,
        status=Project.Status.PUBLISHED,
    )
    return render(request, "directory/detail.html", {"project": project})


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
