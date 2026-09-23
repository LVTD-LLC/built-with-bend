from types import SimpleNamespace

import pytest

from apps.core import tasks
from apps.core.analytics import EVENT_PREFIX, track_event
from apps.core.context_processors import posthog_api_key


def test_analytics_stays_disabled_without_project_token(settings, monkeypatch):
    settings.POSTHOG_API_KEY = ""
    queued = []
    monkeypatch.setattr("apps.core.analytics.async_task", lambda *a, **kw: queued.append(kw))

    track_event(SimpleNamespace(id=7, state="signed_up"), f"{EVENT_PREFIX}_user_logged_in")

    assert queued == []


@pytest.mark.parametrize("cookie", [None, "granted", "denied"])
@pytest.mark.parametrize("method", ["password", "passkey"])
def test_signup_tracks_success_without_consent(cookie, method, monkeypatch):
    from apps.pages import views

    captured = []
    monkeypatch.setattr(views, "track_event", lambda *a, **kw: captured.append((a, kw)))

    class SignupSuccess:
        def form_valid(self, form):
            return "signup succeeded"

    class Signup(views.SignupTrackingMixin, SignupSuccess):
        pass

    view = Signup()
    view.user = SimpleNamespace(profile=SimpleNamespace(id=7))
    view.request = SimpleNamespace(COOKIES={} if cookie is None else {"analytics_consent": cookie})
    view.tracking_source_name = method

    assert view.form_valid(None) == "signup succeeded"
    assert len(captured) == 1
    assert captured[0][0][1] == f"{EVENT_PREFIX}_signup_completed"
    assert captured[0][0][2] == {"signup_method": method}


def test_browser_identity_exposes_profile_id_without_email(settings):
    settings.POSTHOG_API_KEY = "phc_test"
    settings.POSTHOG_BROWSER_HOST = "https://example.test"
    settings.ENVIRONMENT = "test"
    request = SimpleNamespace(
        resolver_match=SimpleNamespace(url_name="landing", route=""),
        user=SimpleNamespace(
            is_authenticated=True,
            profile=SimpleNamespace(id=7),
            email="private@example.com",
        ),
    )

    context = posthog_api_key(request)

    assert context["posthog_distinct_id"] == "7"
    assert "posthog_user_email" not in context
    assert "private@example.com" not in repr(context)


@pytest.mark.django_db
def test_track_event_queues_only_bounded_properties(
    profile,
    settings,
    monkeypatch,
    django_capture_on_commit_callbacks,
):
    settings.POSTHOG_API_KEY = "phc_test"
    queued = {}

    def fake_async_task(path, **kwargs):
        queued["path"] = path
        queued["kwargs"] = kwargs

    monkeypatch.setattr("apps.core.analytics.async_task", fake_async_task)

    with django_capture_on_commit_callbacks(execute=True):
        track_event(
            profile,
            f"{EVENT_PREFIX}_feature_completed",
            {"feature": "example"},
            source_function="test",
        )

    assert queued["path"] == "apps.core.tasks.track_event"
    assert queued["kwargs"]["profile_id"] == profile.id
    assert queued["kwargs"]["current_state"] == profile.state
    assert queued["kwargs"]["properties"] == {"feature": "example"}
    assert "email" not in queued["kwargs"]


@pytest.mark.django_db
def test_track_event_uses_profile_identity_without_email(profile, settings, monkeypatch):
    settings.POSTHOG_API_KEY = "phc_test"
    settings.ENVIRONMENT = "test"
    captures = []
    monkeypatch.setattr(
        tasks.posthog,
        "capture",
        lambda *args, **kwargs: captures.append((args, kwargs)),
    )

    result = tasks.track_event(
        profile.id,
        f"{EVENT_PREFIX}_feature_completed",
        profile.state,
        {"feature": "example"},
    )

    assert result == f"Tracked event {EVENT_PREFIX}_feature_completed for profile {profile.id}"
    args, kwargs = captures[0]
    assert args == (f"{EVENT_PREFIX}_feature_completed",)
    assert kwargs["distinct_id"] == str(profile.id)
    assert kwargs["properties"] == {
        "event_version": 1,
        "environment": "test",
        "profile_id": profile.id,
        "current_state": profile.state,
        "feature": "example",
    }
    assert profile.user.email not in repr(captures)


@pytest.mark.parametrize("template", ["base_landing.html", "base_app.html"])
@pytest.mark.parametrize("token", ["", "phc_test"])
def test_page_shell_has_no_consent_banner_and_only_configured_analytics(template, token):
    from django.template.loader import render_to_string

    html = render_to_string(template, {"posthog_api_key": token})

    assert "data-analytics-consent" not in html
    assert "Allow analytics" not in html
    assert ("posthog.init(" in html) is bool(token)
    if token:
        assert "opt_out_capturing_by_default: false" in html


@pytest.mark.django_db
@pytest.mark.parametrize("cookie", [None, "granted", "denied"])
def test_checkout_tracks_success_without_consent(auth_client, user, cookie, monkeypatch):
    from django.urls import reverse

    from apps.core import views

    captured = []
    monkeypatch.setattr(views, "track_event", lambda *a, **kw: captured.append((a, kw)))
    monkeypatch.setattr(views, "get_price_id_for_plan", lambda plan: "price_test")
    monkeypatch.setattr(
        views, "get_or_create_stripe_customer", lambda *a: SimpleNamespace(id="cus_test")
    )
    monkeypatch.setattr(
        views.stripe.checkout.Session,
        "create",
        lambda **kw: SimpleNamespace(url="https://checkout.stripe.com/test"),
    )
    if cookie is not None:
        auth_client.cookies["analytics_consent"] = cookie

    response = auth_client.post(reverse("user_upgrade_checkout_session", args=[user.pk, "monthly"]))

    assert response.status_code == 302
    assert response.url == "https://checkout.stripe.com/test"
    assert len(captured) == 1
    assert captured[0][0][1] == f"{EVENT_PREFIX}_checkout_started"
    assert captured[0][0][2] == {"plan": "monthly", "checkout_mode": "subscription"}
