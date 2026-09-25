"""Background-only analytics queries; page rendering reads a short-lived aggregate."""

import logging

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)
CACHE_KEY = "directory:pageviews:24h:v1"
QUERY = """
SELECT count() FROM events
WHERE event = '$pageview'
  AND timestamp >= now() - INTERVAL 24 HOUR
  AND timestamp <= now()
  AND properties.$host IN ('builtwithbend.com', 'www.builtwithbend.com')
"""


def refresh_pageviews():
    if not settings.POSTHOG_PERSONAL_API_KEY or not settings.POSTHOG_PROJECT_ID:
        return False
    try:
        response = requests.post(
            f"{settings.POSTHOG_QUERY_HOST}/api/projects/{settings.POSTHOG_PROJECT_ID}/query/",
            headers={"Authorization": f"Bearer {settings.POSTHOG_PERSONAL_API_KEY}"},
            json={"query": {"kind": "HogQLQuery", "query": QUERY}},
            timeout=(3, 15),
        )
        response.raise_for_status()
        count = response.json()["results"][0][0]
        if type(count) is not int or count < 0:
            raise ValueError("Invalid aggregate")
        # Never extend freshness on failure. A sustained outage hides the badge.
        cache.set(CACHE_KEY, count, timeout=900)
        return True
    except (requests.RequestException, ValueError, KeyError, IndexError, TypeError):
        logger.warning(
            "directory.pageviews.refresh_failed",
            extra={"event.name": "directory.pageviews.refresh_failed", "outcome": "failure"},
        )
        return False


def traffic_context(request):
    try:
        count = cache.get(CACHE_KEY)
    except Exception:
        count = None
    return {"navbar_pageviews": count}
