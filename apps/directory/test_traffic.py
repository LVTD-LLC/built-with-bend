from unittest.mock import Mock, patch

import pytest
import requests
from django.core.cache import cache
from django.core.management import call_command
from django.test import override_settings
from django_q.models import Schedule

from .traffic import CACHE_KEY, refresh_pageviews, traffic_context


@pytest.fixture(autouse=True)
def traffic_cache():
    cache.delete(CACHE_KEY)
    yield
    cache.delete(CACHE_KEY)


@override_settings(POSTHOG_PERSONAL_API_KEY="server-only", POSTHOG_PROJECT_ID="625196")
def test_refresh_counts_only_production_pageviews_and_caches_zero():
    with patch("apps.directory.traffic.requests.post") as post:
        post.return_value = Mock(json=lambda: {"results": [[0]]})
        assert refresh_pageviews() is True
    assert traffic_context(None) == {"navbar_pageviews": 0}
    args = post.call_args.kwargs
    query = args["json"]["query"]["query"]
    assert "event = '$pageview'" in query
    assert "INTERVAL 24 HOUR" in query
    assert "builtwithbend.com" in query
    assert args["headers"]["Authorization"] == "Bearer server-only"
    assert args["timeout"] == (3, 15)


@pytest.mark.parametrize(
    "payload",
    [{}, {"results": []}, {"results": [[-1]]}, {"results": [[True]]}, {"results": [["bad"]]}],
)
@override_settings(POSTHOG_PERSONAL_API_KEY="server-only", POSTHOG_PROJECT_ID="625196")
def test_invalid_results_do_not_replace_cache(payload):
    cache.set(CACHE_KEY, 19, 900)
    with patch("apps.directory.traffic.requests.post") as post:
        post.return_value = Mock(json=lambda: payload)
        assert refresh_pageviews() is False
    assert traffic_context(None)["navbar_pageviews"] == 19


@override_settings(POSTHOG_PERSONAL_API_KEY="server-only", POSTHOG_PROJECT_ID="625196")
def test_outage_is_not_zero_and_does_not_break_pages():
    with patch("apps.directory.traffic.requests.post", side_effect=requests.Timeout):
        assert refresh_pageviews() is False
    assert traffic_context(None)["navbar_pageviews"] is None
    with patch("apps.directory.traffic.cache.get", side_effect=ConnectionError):
        assert traffic_context(None)["navbar_pageviews"] is None


@override_settings(POSTHOG_PERSONAL_API_KEY="")
def test_unconfigured_does_not_query():
    with patch("apps.directory.traffic.requests.post") as post:
        assert refresh_pageviews() is False
    post.assert_not_called()


@pytest.mark.django_db
def test_schedule_is_idempotent():
    call_command("refresh_pageviews", "--schedule")
    call_command("refresh_pageviews", "--schedule")
    schedule = Schedule.objects.get(name="directory-pageviews")
    assert schedule.minutes == 5


@pytest.mark.django_db
def test_navbar_search_and_traffic(client):
    cache.set(CACHE_KEY, 1234, 900)
    response = client.get("/?q=compiler&source=github&category=tool&page=2")
    html = response.content.decode()
    assert "1,234 views in the last 24 hours" in html
    assert 'id="nav-search"' in html
    assert 'value="compiler"' in html
    assert "server-only" not in html
    cache.delete(CACHE_KEY)
    assert "views in the last 24 hours" not in client.get("/").content.decode()
