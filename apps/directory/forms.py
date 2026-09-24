import uuid

from django import forms
from django.core import signing
from django.utils import timezone

from .models import Sponsorship, Submission


class SubmissionForm(forms.ModelForm):
    company = forms.CharField(required=False, widget=forms.HiddenInput)
    started = forms.CharField(widget=forms.HiddenInput)
    confirm = forms.BooleanField(label="This project uses Bend 2, and the source link shows it.")

    class Meta:
        model = Submission
        fields = [
            "source_url",
            "title",
            "description",
            "website_url",
            "repository_url",
            "thumbnail_url",
            "category",
            "author",
            "contact",
        ]
        labels = {
            "source_url": "Source URL",
            "description": "What does it do?",
            "website_url": "Live site or demo URL",
            "repository_url": "Repository URL",
            "thumbnail_url": "Thumbnail image URL (optional)",
            "contact": "Contact (private, optional)",
        }
        widgets = {"description": forms.Textarea(attrs={"rows": 5})}
        help_texts = {
            "source_url": "An X or Reddit post, GitHub repo, video, or site that shows the build.",
            "website_url": "Somewhere people can try it. Optional, but encouraged.",
            "repository_url": "Optional. Closed-source projects are welcome.",
            "contact": "An email or social handle in case we need a detail. Never published.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["started"].initial = signing.dumps(
            {"time": timezone.now().timestamp()}, salt="submission"
        )
        self.fields["source_url"].widget.attrs["placeholder"] = "https://x.com/…/status/…"
        self.fields["thumbnail_url"].widget.attrs["placeholder"] = (
            "https://example.com/screenshot.png"
        )
        self.fields["title"].widget.attrs["placeholder"] = "Give your build a name"

    def clean(self):
        data = super().clean()
        try:
            token = signing.loads(data.get("started", ""), salt="submission", max_age=86400)
            if timezone.now().timestamp() - token["time"] < 2 or data.get("company"):
                raise ValueError
        except (signing.BadSignature, ValueError, KeyError):
            raise forms.ValidationError("Please refresh the form and try again.") from None
        return data


class SponsorshipForm(forms.ModelForm):
    checkout_token = forms.CharField(widget=forms.HiddenInput)
    company = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Sponsorship
        fields = ["business_name", "website_url", "tagline"]
        labels = {"website_url": "Business website", "tagline": "Short description"}
        help_texts = {"tagline": "Shown beside your link. Up to 120 characters."}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["checkout_token"].initial = signing.dumps(
            str(uuid.uuid4()), salt="sponsorship-checkout"
        )

    def clean(self):
        data = super().clean()
        try:
            data["order_id"] = uuid.UUID(
                signing.loads(
                    data.get("checkout_token", ""), salt="sponsorship-checkout", max_age=3600
                )
            )
            if data.get("company"):
                raise ValueError
        except (signing.BadSignature, ValueError, TypeError):
            raise forms.ValidationError("Please refresh the form and try again.") from None
        return data
