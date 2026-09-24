"""One-time, account-scoped Stripe Checkout for seven-day directory placements."""

from datetime import timedelta

import stripe
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from apps.directory.models import Sponsorship

AMOUNT = 10_000
CURRENCY = "usd"
PURPOSE = "built_with_bend_sponsorship"


def enabled():
    return bool(
        settings.SPONSORSHIPS_ENABLED
        and settings.SPONSORSHIP_STRIPE_SECRET_KEY
        and settings.SPONSORSHIP_STRIPE_ACCOUNT_ID
        and settings.SPONSORSHIP_STRIPE_PRICE_ID
        and settings.SPONSORSHIP_STRIPE_WEBHOOK_SECRET
    )


def stripe_client():
    return stripe.StripeClient(
        settings.SPONSORSHIP_STRIPE_SECRET_KEY,
        stripe_context=settings.SPONSORSHIP_STRIPE_ACCOUNT_ID,
        http_client=stripe.RequestsClient(timeout=10),
        max_network_retries=1,
    )


def create_checkout(data):
    """Persist first; reuse the same order and Stripe idempotency key on retries."""
    sponsor, _ = Sponsorship.objects.get_or_create(
        id=data["order_id"],
        defaults={
            **{key: data[key] for key in ("business_name", "website_url", "tagline")},
            "stripe_price_id": settings.SPONSORSHIP_STRIPE_PRICE_ID,
        },
    )
    with transaction.atomic():
        sponsor = Sponsorship.objects.select_for_update().get(pk=sponsor.pk)
        if any(
            getattr(sponsor, key) != data[key]
            for key in ("business_name", "website_url", "tagline")
        ):
            raise ValidationError("Refresh this page before changing a submitted sponsorship.")
        if sponsor.status != Sponsorship.Status.PENDING:
            raise ValidationError("This sponsorship has already been processed.")
        if timezone.now() >= sponsor.created_at + timedelta(minutes=30):
            raise ValidationError("This checkout has expired. Refresh this page to start again.")
        if sponsor.checkout_url:
            return sponsor.checkout_url
        client = stripe_client()
        price = client.v1.prices.retrieve(sponsor.stripe_price_id)
        if not (
            price.active
            and price.type == "one_time"
            and price.unit_amount == AMOUNT
            and price.currency == CURRENCY
            and price.livemode == settings.SPONSORSHIP_STRIPE_LIVE_MODE
        ):
            raise ValidationError("Sponsorship checkout is temporarily unavailable.")
        metadata = {"purpose": PURPOSE, "sponsorship_id": str(sponsor.pk)}
        base = settings.SITE_URL.rstrip("/")
        session = client.v1.checkout.sessions.create(
            {
                "mode": "payment",
                "payment_method_types": ["card"],
                "line_items": [{"price": sponsor.stripe_price_id, "quantity": 1}],
                "client_reference_id": str(sponsor.pk),
                "metadata": metadata,
                "payment_intent_data": {"metadata": metadata},
                "success_url": base
                + reverse("directory:sponsor_success")
                + "?session_id={CHECKOUT_SESSION_ID}",
                "cancel_url": base + reverse("directory:sponsor") + "?cancelled=1",
                "allow_promotion_codes": False,
                "adaptive_pricing": {"enabled": False},
            },
            options={"idempotency_key": f"bend-sponsor-{sponsor.pk}"},
        )
        sponsor.checkout_session_id = session.id
        sponsor.checkout_url = session.url
        sponsor.save(update_fields=["checkout_session_id", "checkout_url"])
        return session.url


def fulfill_checkout(session_id):
    """Re-read Stripe, then serialize activation so retries never extend a week."""
    session = (
        stripe_client()
        .v1.checkout.sessions.retrieve(
            session_id, {"expand": ["line_items", "payment_intent.latest_charge"]}
        )
        .to_dict()
    )
    metadata = session.get("metadata") or {}
    if metadata.get("purpose") != PURPOSE:
        return None
    if not (
        session.get("livemode") == settings.SPONSORSHIP_STRIPE_LIVE_MODE
        and session.get("mode") == "payment"
        and session.get("payment_status") == "paid"
        and session.get("status") == "complete"
        and session.get("amount_total") == AMOUNT
        and session.get("currency") == CURRENCY
    ):
        return None
    with transaction.atomic():
        sponsor = (
            Sponsorship.objects.select_for_update().filter(checkout_session_id=session_id).first()
        )
        if sponsor is None:
            # Do not acknowledge a rare create/fulfillment race: Stripe must retry.
            raise ValueError("Sponsorship checkout has not been persisted yet")
        items = (session.get("line_items") or {}).get("data", [])
        if not (
            metadata.get("sponsorship_id") == str(sponsor.pk)
            and session.get("client_reference_id") == str(sponsor.pk)
            and len(items) == 1
            and items[0].get("quantity") == 1
            and (items[0].get("price") or {}).get("id") == sponsor.stripe_price_id
        ):
            return None
        intent = session.get("payment_intent") or {}
        charge = intent.get("latest_charge") or {}
        if not intent.get("id") or not charge.get("id"):
            raise ValueError("Sponsorship payment details are incomplete")
        sponsor.payment_intent_id = intent["id"]
        if charge.get("amount_refunded", 0) > 0 or charge.get("disputed"):
            sponsor.status = Sponsorship.Status.REVOKED
        elif sponsor.status == Sponsorship.Status.PENDING:
            sponsor.status = Sponsorship.Status.PAID
            sponsor.starts_at = timezone.now()
            sponsor.ends_at = sponsor.starts_at + timedelta(days=7)
        sponsor.save(update_fields=["payment_intent_id", "status", "starts_at", "ends_at"])
        return sponsor


def revoke_payment(payment_intent_id):
    """PI metadata also resolves refunds/disputes delivered before completion."""
    intent = stripe_client().v1.payment_intents.retrieve(payment_intent_id).to_dict()
    metadata = intent.get("metadata") or {}
    if metadata.get("purpose") != PURPOSE:
        return
    if intent.get("livemode") != settings.SPONSORSHIP_STRIPE_LIVE_MODE:
        return
    with transaction.atomic():
        sponsor = Sponsorship.objects.select_for_update().get(pk=metadata["sponsorship_id"])
        sponsor.status = Sponsorship.Status.REVOKED
        sponsor.payment_intent_id = payment_intent_id
        sponsor.save(update_fields=["status", "payment_intent_id"])
