"""Bounded, public GitHub metadata refresh. No requests run in a page view."""

import re
from datetime import timedelta
from urllib.parse import urlsplit

import httpx
from django.core.cache import cache
from django.db.models import F, Q
from django.utils import timezone

from .models import Project


def github_repository(project):
    urls = [project.repository_url, project.canonical_url]
    urls.extend(link.url for link in project.sources.all() if link.kind == "github")
    for url in urls:
        parsed = urlsplit(url)
        if parsed.scheme not in ("http", "https") or parsed.hostname not in (
            "github.com",
            "www.github.com",
        ):
            continue
        parts = parsed.path.strip("/").split("/")
        if len(parts) < 2:
            continue
        owner, repo = parts[:2]
        repo = repo.removesuffix(".git")
        if all(
            re.fullmatch(r"[A-Za-z0-9_.-]+", part) and part not in (".", "..")
            for part in (owner, repo)
        ):
            return f"{owner}/{repo}"
    return None


def refresh_github_stars(limit=30):
    """Refresh up to 30 stale projects hourly; keep last known counts on errors."""
    if not cache.add("directory:github-refresh", True, timeout=600):
        return {"updated": 0, "failed": 0, "locked": True}
    updated = failed = 0
    try:
        cutoff = timezone.now() - timedelta(days=1)
        candidates = (
            Project.objects.filter(status=Project.Status.PUBLISHED)
            .filter(Q(github_stars_checked_at__isnull=True) | Q(github_stars_checked_at__lt=cutoff))
            .prefetch_related("sources")
            .order_by(F("github_stars_checked_at").asc(nulls_first=True), "pk")
        )
        attempts = 0
        with httpx.Client(
            timeout=8,
            follow_redirects=False,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "BuiltWithBend-catalog",
            },
        ) as client:
            for project in candidates.iterator(chunk_size=100):
                repo = github_repository(project)
                if not repo:
                    continue
                if attempts >= min(max(limit, 1), 30):
                    break
                attempts += 1
                try:
                    response = client.get(f"https://api.github.com/repos/{repo}")
                    if response.status_code in (403, 429):
                        failed += 1
                        break  # Respect GitHub's rate limit; next scheduled run retries.
                    response.raise_for_status()
                    stars = response.json()["stargazers_count"]
                    if type(stars) is not int or not 0 <= stars <= 2147483647:
                        raise ValueError("Invalid star count")
                except (httpx.HTTPError, ValueError, KeyError, TypeError):
                    failed += 1
                    continue
                Project.objects.filter(pk=project.pk).update(
                    github_stars=stars,
                    github_stars_checked_at=timezone.now(),
                )
                updated += 1
        return {"updated": updated, "failed": failed}
    finally:
        cache.delete("directory:github-refresh")
