import hashlib
import hmac
import json
import time
import uuid
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
import stripe
from django.core import signing
from django.test import Client
from django.utils import timezone

from apps.core import sponsorships
from apps.directory.models import Sponsorship

pytestmark = pytest.mark.django_db


@pytest.fixture
def billing(settings, monkeypatch):
    settings.SPONSORSHIPS_ENABLED = True
    settings.SPONSORSHIP_STRIPE_SECRET_KEY = "sk_test_local_only"
    settings.SPONSORSHIP_STRIPE_ACCOUNT_ID = "acct_bend_test"
    settings.SPONSORSHIP_STRIPE_PRICE_ID = "price_week"
    settings.SPONSORSHIP_STRIPE_WEBHOOK_SECRET = "whsec_local_test_only"
    settings.SPONSORSHIP_STRIPE_LIVE_MODE = False
    api = Mock()
    api.v1.prices.retrieve.return_value = SimpleNamespace(
        active=True, type="one_time", unit_amount=10000, currency="usd", livemode=False
    )
    api.v1.checkout.sessions.create.return_value = SimpleNamespace(
        id="cs_test_week", url="https://checkout.stripe.com/c/pay/cs_test_week"
    )
    monkeypatch.setattr(sponsorships, "stripe_client", lambda: api)
    return api


def payload():
    return {
        "business_name": "Example business",
        "website_url": "https://example.com/",
        "tagline": "Useful tools for builders.",
        "checkout_token": signing.dumps(str(uuid.uuid4()), salt="sponsorship-checkout"),
    }


def order():
    return Sponsorship.objects.create(
        business_name="Paid partner",
        website_url="https://example.com/partner",
        tagline="Build something useful.",
        stripe_price_id="price_week",
        checkout_session_id="cs_test_week",
    )


def paid_session(sponsor):
    return {
        "id": sponsor.checkout_session_id,
        "metadata": {"purpose": sponsorships.PURPOSE, "sponsorship_id": str(sponsor.pk)},
        "client_reference_id": str(sponsor.pk),
        "livemode": False,
        "mode": "payment",
        "status": "complete",
        "payment_status": "paid",
        "amount_total": 10000,
        "currency": "usd",
        "line_items": {"data": [{"quantity": 1, "price": {"id": "price_week"}}]},
        "payment_intent": {
            "id": "pi_week",
            "latest_charge": {"id": "ch_week", "amount_refunded": 0, "disputed": False},
        },
    }


def event_post(client, settings, kind="checkout.session.completed", obj=None, **extra):
    event = {
        "id": "evt_week",
        "type": kind,
        "livemode": False,
        "data": {"object": obj or {"id": "cs_test_week"}},
        **extra,
    }
    body = json.dumps(event)
    timestamp = int(time.time())
    signature = hmac.new(
        settings.SPONSORSHIP_STRIPE_WEBHOOK_SECRET.encode(),
        f"{timestamp}.{body}".encode(),
        hashlib.sha256,
    ).hexdigest()
    return client.post(
        "/sponsor/webhook/",
        body,
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE=f"t={timestamp},v1={signature}",
    )


def test_checkout_disabled_by_default(client):
    assert b"opening soon" in client.get("/sponsor/").content
    assert client.post("/sponsor/", payload()).status_code == 503
    assert not Sponsorship.objects.exists()


def test_checkout_fixed_price_anonymous_and_idempotent(client, billing):
    data = payload()
    first = client.post("/sponsor/", data)
    second = client.post("/sponsor/", data)
    assert first.status_code == second.status_code == 303
    assert first.url == second.url == billing.v1.checkout.sessions.create.return_value.url
    assert Sponsorship.objects.count() == 1
    billing.v1.checkout.sessions.create.assert_called_once()
    params = billing.v1.checkout.sessions.create.call_args.args[0]
    assert params["mode"] == "payment"
    assert params["line_items"] == [{"price": "price_week", "quantity": 1}]
    assert params["payment_method_types"] == ["card"]
    assert params["allow_promotion_codes"] is False
    assert params["adaptive_pricing"] == {"enabled": False}
    assert Sponsorship.objects.get().status == "pending"


@pytest.mark.parametrize(
    "url", ["javascript:alert(1)", "https://user:pass@example.com/", "ftp://example.com/"]
)
def test_unsafe_link_cannot_create_checkout(client, billing, url):
    data = payload()
    data["website_url"] = url
    assert client.post("/sponsor/", data).status_code == 200
    billing.v1.checkout.sessions.create.assert_not_called()
    assert not Sponsorship.objects.exists()


@pytest.mark.parametrize(
    "field,value",
    [
        ("unit_amount", 100),
        ("currency", "eur"),
        ("type", "recurring"),
        ("active", False),
        ("livemode", True),
    ],
)
def test_wrong_configured_price_fails_closed(client, billing, field, value):
    setattr(billing.v1.prices.retrieve.return_value, field, value)
    assert client.post("/sponsor/", payload()).status_code == 400
    billing.v1.checkout.sessions.create.assert_not_called()


def test_tampered_form_csrf_and_rate_limit(client, billing):
    data = payload()
    data["checkout_token"] = "forged"
    client.post("/sponsor/", data)
    assert not Sponsorship.objects.exists()
    assert Client(enforce_csrf_checks=True).post("/sponsor/", payload()).status_code == 403
    for _ in range(9):
        client.post("/sponsor/", data)
    assert client.post("/sponsor/", data).status_code == 429
    billing.v1.checkout.sessions.create.assert_not_called()


def test_stripe_failure_retries_same_order_and_key(client, billing):
    data = payload()
    billing.v1.checkout.sessions.create.side_effect = stripe.APIConnectionError("test failure")
    assert client.post("/sponsor/", data).status_code == 503
    first_key = billing.v1.checkout.sessions.create.call_args.kwargs["options"]["idempotency_key"]
    billing.v1.checkout.sessions.create.side_effect = None
    assert client.post("/sponsor/", data).status_code == 303
    assert Sponsorship.objects.count() == 1
    assert (
        billing.v1.checkout.sessions.create.call_args.kwargs["options"]["idempotency_key"]
        == first_key
    )


def test_changed_payload_cannot_reuse_checkout(client, billing):
    data = payload()
    client.post("/sponsor/", data)
    data["website_url"] = "https://example.com/different"
    assert client.post("/sponsor/", data).status_code == 400
    billing.v1.checkout.sessions.create.assert_called_once()


def test_signed_payment_activates_once_and_expires(client, billing, settings, monkeypatch):
    sponsor = order()
    billing.v1.checkout.sessions.retrieve.return_value = stripe.StripeObject.construct_from(
        paid_session(sponsor), None
    )
    assert event_post(client, settings).status_code == 200
    sponsor.refresh_from_db()
    start, end = sponsor.starts_at, sponsor.ends_at
    assert end - start == timedelta(days=7)
    assert b"Paid partner" in client.get("/").content
    monkeypatch.setattr(timezone, "now", lambda: start + timedelta(days=1))
    assert event_post(client, settings).status_code == 200
    sponsor.refresh_from_db()
    assert (sponsor.starts_at, sponsor.ends_at) == (start, end)
    monkeypatch.setattr(timezone, "now", lambda: end)
    assert b"Paid partner" not in client.get("/").content


@pytest.mark.parametrize(
    "field,value",
    [
        ("payment_status", "unpaid"),
        ("amount_total", 1),
        ("currency", "eur"),
        ("mode", "subscription"),
        ("status", "open"),
        ("livemode", True),
        ("client_reference_id", "wrong"),
    ],
)
def test_wrong_payment_never_activates(billing, field, value):
    sponsor = order()
    session = paid_session(sponsor)
    session[field] = value
    billing.v1.checkout.sessions.retrieve.return_value = stripe.StripeObject.construct_from(
        session, None
    )
    sponsorships.fulfill_checkout(sponsor.checkout_session_id)
    sponsor.refresh_from_db()
    assert sponsor.status == "pending"
    assert sponsor.starts_at is None


@pytest.mark.parametrize(
    "items",
    [
        [],
        [{"quantity": 2, "price": {"id": "price_week"}}],
        [{"quantity": 1, "price": {"id": "price_other"}}],
    ],
)
def test_wrong_line_items_never_activate(billing, items):
    sponsor = order()
    session = paid_session(sponsor)
    session["line_items"]["data"] = items
    billing.v1.checkout.sessions.retrieve.return_value = stripe.StripeObject.construct_from(
        session, None
    )
    assert sponsorships.fulfill_checkout(sponsor.checkout_session_id) is None
    assert not Sponsorship.active().exists()


def test_unsigned_wrong_mode_and_wrong_account_events_rejected(client, billing, settings):
    assert (
        client.post("/sponsor/webhook/", "{}", content_type="application/json").status_code == 400
    )
    assert event_post(client, settings, livemode=True).status_code == 400
    assert event_post(client, settings, context="acct_wrong").status_code == 400
    billing.v1.checkout.sessions.retrieve.assert_not_called()


@pytest.mark.parametrize("kind", ["charge.refunded", "charge.dispute.created"])
@pytest.mark.parametrize("refund_first", [True, False])
def test_refund_and_dispute_remove_link_even_out_of_order(
    client, billing, settings, kind, refund_first
):
    sponsor = order()
    session = paid_session(sponsor)
    billing.v1.checkout.sessions.retrieve.return_value = stripe.StripeObject.construct_from(
        session, None
    )
    billing.v1.payment_intents.retrieve.return_value = stripe.StripeObject.construct_from(
        {
            "id": "pi_week",
            "metadata": session["metadata"],
            "livemode": False,
        },
        None,
    )
    if not refund_first:
        event_post(client, settings)
    assert (
        event_post(
            client, settings, kind, {"payment_intent": "pi_week", "amount_refunded": 100}
        ).status_code
        == 200
    )
    event_post(client, settings)
    sponsor.refresh_from_db()
    assert sponsor.status == "revoked"
    assert b"Paid partner" not in client.get("/").content


def test_refund_detected_during_fulfillment(billing):
    sponsor = order()
    session = paid_session(sponsor)
    session["payment_intent"]["latest_charge"]["amount_refunded"] = 10000
    billing.v1.checkout.sessions.retrieve.return_value = stripe.StripeObject.construct_from(
        session, None
    )
    sponsorships.fulfill_checkout(sponsor.checkout_session_id)
    sponsor.refresh_from_db()
    assert sponsor.status == "revoked"


def test_receipt_does_not_grant_payment_or_leak_sensitive_data(client, billing):
    sponsor = order()
    response = client.get("/sponsor/thanks/?session_id=" + sponsor.checkout_session_id)
    assert response.status_code == 200
    assert b"please do not pay again" in response.content
    assert "no-store" in response["Cache-Control"]
    assert response["Referrer-Policy"] == "no-referrer"
    assert Sponsorship.objects.get().status == "pending"
    billing.v1.checkout.sessions.retrieve.assert_not_called()


def test_hidden_and_unpaid_links_are_not_public(client, billing):
    sponsor = order()
    assert b"Paid partner" not in client.get("/").content
    billing.v1.checkout.sessions.retrieve.return_value = stripe.StripeObject.construct_from(
        paid_session(sponsor), None
    )
    sponsorships.fulfill_checkout(sponsor.checkout_session_id)
    sponsor.refresh_from_db()
    sponsor.hidden = True
    sponsor.save()
    assert b"Paid partner" not in client.get("/").content


def test_database_failure_is_retriable(client, billing, settings):
    billing.v1.checkout.sessions.retrieve.side_effect = stripe.APIConnectionError("test failure")
    client.raise_request_exception = False
    assert event_post(client, settings).status_code == 500


def test_payment_before_checkout_persisted_is_retriable(client, billing, settings):
    sponsor = order()
    billing.v1.checkout.sessions.retrieve.return_value = stripe.StripeObject.construct_from(
        paid_session(sponsor), None
    )
    sponsor.checkout_session_id = None
    sponsor.save()
    client.raise_request_exception = False
    assert event_post(client, settings).status_code == 500
