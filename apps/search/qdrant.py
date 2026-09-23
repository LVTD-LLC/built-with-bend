from __future__ import annotations

from functools import lru_cache

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from qdrant_client import QdrantClient


@lru_cache(maxsize=1)
def get_qdrant_client() -> QdrantClient:
    """Return the configured Qdrant client, creating it on first use."""
    if not settings.QDRANT_URL:
        raise ImproperlyConfigured("QDRANT_URL must be configured before using Qdrant.")
    if not settings.QDRANT_API_KEY:
        raise ImproperlyConfigured("QDRANT_API_KEY must be configured before using Qdrant.")

    return QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
        timeout=settings.QDRANT_TIMEOUT_SECONDS,
    )
