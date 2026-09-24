"""Public sponsorship entry points; no account or subscription is required."""

import logging

import stripe
from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from apps.core import sponsorships
from apps.directory.forms import SponsorshipForm
from apps.directory.models import Sponsorship
from apps.directory.views import submission_allowed

logger = logging.getLogger(__name__)


@never_cache
@require_http_methods(["GET", "POST"])
def sponsor(request):
    form = SponsorshipForm(request.POST if request.method == "POST" else None)
    available = sponsorships.enabled()
    status = 200
    if request.method == "POST":
        if not available:
            status = 503
        elif not submission_allowed(request, scope=":sponsorship"):
            form.add_error(None, "Too many attempts. Please try again in an hour.")
            status = 429
        elif form.is_valid():
            try:
                response = redirect(sponsorships.create_checkout(form.cleaned_data))
                response.status_code = 303
                return response
            except ValidationError as exc:
                form.add_error(None, exc)
                status = 400
            except stripe.StripeError:
                logger.warning(
                    "sponsorship.checkout.failed",
                    extra={"event.name": "sponsorship.checkout.failed", "outcome": "failure"},
                )
                form.add_error(None, "Checkout is temporarily unavailable. Please try again.")
                status = 503
    response = render(
        request, "directory/sponsorship.html", {"form": form, "available": available}, status=status
    )
    if status == 429:
        response["Retry-After"] = "3600"
    return response


@never_cache
@require_GET
def sponsor_success(request):
    # A redirect is not proof of payment. Only report state saved by the webhook.
    session_id = request.GET.get("session_id", "")[:255]
    sponsor = (
        Sponsorship.objects.filter(checkout_session_id=session_id).first() if session_id else None
    )
    response = render(request, "directory/sponsorship_success.html", {"sponsor": sponsor})
    response["Referrer-Policy"] = "no-referrer"
    response["X-Robots-Tag"] = "noindex"
    return response


@csrf_exempt
@require_POST
def sponsor_webhook(request):
    if not settings.SPONSORSHIP_STRIPE_WEBHOOK_SECRET:
        return HttpResponse(status=503)
    try:
        event = stripe.Webhook.construct_event(
            request.body,
            request.headers.get("Stripe-Signature", ""),
            settings.SPONSORSHIP_STRIPE_WEBHOOK_SECRET,
        ).to_dict()
    except (ValueError, stripe.SignatureVerificationError):
        return HttpResponse(status=400)
    if event.get("livemode") != settings.SPONSORSHIP_STRIPE_LIVE_MODE:
        return HttpResponse(status=400)
    context = event.get("context") or event.get("account")
    if context and context != settings.SPONSORSHIP_STRIPE_ACCOUNT_ID:
        return HttpResponse(status=400)
    from apps.core.stripe_webhooks import handle_sponsorship_event

    # Exceptions propagate as 500 so Stripe retries instead of losing fulfillment.
    handle_sponsorship_event(event)
    return HttpResponse(status=200)
