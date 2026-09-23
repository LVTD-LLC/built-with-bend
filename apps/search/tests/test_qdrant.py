from __future__ import annotations

from unittest.mock import patch

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings

from apps.search.qdrant import get_qdrant_client


@pytest.fixture(autouse=True)
def clear_qdrant_client_cache():
    get_qdrant_client.cache_clear()
    yield
    get_qdrant_client.cache_clear()


@override_settings(QDRANT_URL="", QDRANT_API_KEY="test-key", QDRANT_TIMEOUT_SECONDS=5.0)
def test_qdrant_client_requires_url() -> None:
    with pytest.raises(ImproperlyConfigured, match="QDRANT_URL"):
        get_qdrant_client()


@override_settings(
    QDRANT_URL="https://qdrant.example.com",
    QDRANT_API_KEY="",
    QDRANT_TIMEOUT_SECONDS=5.0,
)
def test_qdrant_client_requires_api_key() -> None:
    with pytest.raises(ImproperlyConfigured, match="QDRANT_API_KEY"):
        get_qdrant_client()


@override_settings(
    QDRANT_URL="https://qdrant.example.com",
    QDRANT_API_KEY="test-key",
    QDRANT_TIMEOUT_SECONDS=7.5,
)
@patch("apps.search.qdrant.QdrantClient")
def test_qdrant_client_uses_configured_connection(mock_client) -> None:
    get_qdrant_client()

    mock_client.assert_called_once_with(
        url="https://qdrant.example.com",
        api_key="test-key",
        timeout=7.5,
    )


@override_settings(
    QDRANT_URL="https://qdrant.example.com",
    QDRANT_API_KEY="test-key",
    QDRANT_TIMEOUT_SECONDS=5.0,
)
@patch("apps.search.qdrant.QdrantClient")
def test_qdrant_client_is_cached(mock_client) -> None:
    first = get_qdrant_client()
    second = get_qdrant_client()

    assert first is second
    mock_client.assert_called_once()
