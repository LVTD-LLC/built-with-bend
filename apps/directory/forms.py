from django import forms
from django.core import signing
from django.utils import timezone

from .models import Submission


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
            "category",
            "author",
            "contact",
        ]
        labels = {
            "source_url": "Source URL",
            "description": "What does it do?",
            "website_url": "Live site or demo URL",
            "repository_url": "Repository URL",
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
