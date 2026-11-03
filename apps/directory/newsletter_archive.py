"""Read only Listmonk's public archive metadata; never request subscriber data."""

from hashlib import sha256
from urllib.parse import urlsplit

import requests
from django.conf import settings
from django.core.cache import cache
from django.utils.dateparse import parse_datetime
from redis.exceptions import RedisError

PAGE_SIZE = 20
FRESH_SECONDS = 300
STALE_SECONDS = 60 * 60 * 24 * 30


def _cached(key):
    try:
        return cache.get(key)
    except (RedisError, OSError):
        return None


def _store(key, value, seconds):
    try:
        cache.set(key, value, seconds)
    except (RedisError, OSError):
        pass


def _issue(row):
    public = urlsplit(settings.NEWSLETTER_ARCHIVE_PUBLIC_URL)
    url = row["url"]
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or parsed.netloc != public.netloc
        or not parsed.path.startswith("/archive/")
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("Unexpected public archive URL")
    subject = row["subject"]
    if not isinstance(subject, str) or not subject.strip():
        raise ValueError("Missing archive subject")
    sent_at = parse_datetime(row.get("send_at") or row["created_at"])
    if sent_at is None:
        raise ValueError("Missing archive date")
    return {"subject": subject, "url": url, "sent_at": sent_at}


def archive_page_number(value):
    try:
        return min(max(int(value), 1), 1000)
    except (ValueError, TypeError):
        return 1


def archive_page(page=1):
    base = settings.NEWSLETTER_LISTMONK_URL.rstrip("/")
    key = f"newsletter:archive:v1:{sha256(base.encode()).hexdigest()[:12]}:{page}"
    fresh = _cached(key + ":fresh")
    if fresh is not None:
        return fresh
    stale = _cached(key)
    if not base:
        return stale or {"issues": [], "unavailable": True}
    try:
        response = requests.get(
            base + "/api/public/archive",
            params={"page": page, "per_page": PAGE_SIZE},
            timeout=(2, 3),
            allow_redirects=False,
        )
        response.raise_for_status()
        if response.status_code != 200:
            raise ValueError("Unexpected archive response")
        data = response.json()["data"]
        rows = data["results"]
        total = data["total"]
        if not isinstance(rows, list) or type(total) is not int or total < 0:
            raise ValueError("Unexpected archive metadata")
        result = {
            "issues": [_issue(row) for row in rows[:PAGE_SIZE]],
            "previous_page": page - 1 if page > 1 else None,
            "next_page": page + 1 if page * PAGE_SIZE < total else None,
            "unavailable": False,
        }
    except (requests.RequestException, ValueError, TypeError, KeyError, AttributeError):
        return stale or {"issues": [], "unavailable": True}
    _store(key, result, STALE_SECONDS)
    _store(key + ":fresh", result, FRESH_SECONDS)
    return result
