import json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core import signing
from django.test import Client, TestCase
from django.utils import timezone

from .models import AdminAPIKey, Project, SourceLink, Submission
from .services import approve_submission, create_project


class DirectoryTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            "curator", "curator@example.com", "test-only-password"
        )
        self.payload = {
            "title": "A tiny game",
            "description": "A puzzle written in Bend 2.",
            "website_url": "https://example.com/game",
            "sources": [
                "https://github.com/example/game",
                "https://x.com/maker/status/123",
            ],
        }

    def token(self, user=None, active=True):
        value = "local-test-token-never-used-in-production"
        AdminAPIKey.objects.create(
            name="tests",
            user=user or self.admin,
            digest=AdminAPIKey.hash_token(value),
            active=active,
        )
        return {"HTTP_AUTHORIZATION": f"Bearer {value}"}

    def post_api(self, payload=None, **headers):
        return self.client.post(
            "/api/v1/projects",
            json.dumps(payload or self.payload),
            content_type="application/json",
            **headers,
        )

    def test_auth_boundary(self):
        self.assertEqual(self.post_api().status_code, 401)
        member = get_user_model().objects.create_user("member")
        self.assertEqual(self.post_api(**self.token(member)).status_code, 401)
        self.assertEqual(Project.objects.count(), 0)

    def test_inactive_key_rejected(self):
        self.assertEqual(self.post_api(**self.token(active=False)).status_code, 401)

    def test_revoked_admin_access_rejected(self):
        headers = self.token()
        self.admin.is_superuser = False
        self.admin.save()
        self.assertEqual(self.post_api(**headers).status_code, 401)

    def test_default_draft_is_private_and_not_in_search(self):
        response = self.post_api(**self.token())
        self.assertEqual(response.status_code, 201)
        project = Project.objects.get()
        self.assertEqual(project.status, Project.Status.DRAFT)
        self.assertNotContains(self.client.get("/?q=tiny"), project.title)
        self.assertEqual(self.client.get(project.get_absolute_url()).status_code, 404)
        self.assertEqual(self.client.get(f"/api/v1/projects/{project.pk}").status_code, 401)

    def test_admin_publishes_closed_source_with_multiple_sources(self):
        self.payload["publish"] = True
        self.assertEqual(self.post_api(**self.token()).status_code, 201)
        project = Project.objects.get()
        self.assertIsNotNone(project.published_at)
        self.assertEqual(project.repository_url, "")
        self.assertEqual(set(project.sources.values_list("kind", flat=True)), {"github", "x"})
        self.assertContains(self.client.get("/?source=github"), project.title)
        self.assertContains(self.client.get("/?source=x"), project.title)
        self.assertNotContains(self.client.get("/?source=reddit"), project.title)

    def test_source_only_project(self):
        self.payload.pop("website_url")
        response = self.post_api(**self.token())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Project.objects.get().canonical_url, self.payload["sources"][0])

    def test_invalid_urls_roll_back_entire_write(self):
        self.payload["sources"] = ["javascript:alert(1)"]
        self.assertEqual(self.post_api(**self.token()).status_code, 422)
        self.assertEqual(Project.objects.count(), 0)
        self.assertEqual(SourceLink.objects.count(), 0)

    def test_url_credentials_rejected(self):
        self.payload["website_url"] = "https://user:password@example.com/"
        self.assertEqual(self.post_api(**self.token()).status_code, 422)

    def test_no_link_rejected(self):
        self.payload.pop("website_url")
        self.payload["sources"] = []
        self.assertEqual(self.post_api(**self.token()).status_code, 422)

    def test_duplicate_does_not_create_another_project(self):
        headers = self.token()
        self.assertEqual(self.post_api(**headers).status_code, 201)
        self.assertIn(self.post_api(**headers).status_code, [409, 422])
        self.assertEqual(Project.objects.count(), 1)

    def submission(self, **overrides):
        return {
            "title": "Community build",
            "description": "A small Bend game.",
            "source_url": "https://reddit.com/r/bend/comments/demo",
            "category": "games",
            "contact": "private@example.com",
            "confirm": "on",
            "started": signing.dumps(
                {"time": (timezone.now() - timedelta(seconds=5)).timestamp()},
                salt="submission",
            ),
            **overrides,
        }

    def test_public_submission_requires_review_and_contact_stays_private(self):
        response = self.client.post("/submit/", self.submission())
        self.assertRedirects(response, "/submitted/")
        submission = Submission.objects.get()
        self.assertEqual(submission.status, Submission.Status.PENDING)
        self.assertEqual(Project.objects.count(), 0)
        project = approve_submission(submission.pk, self.admin)
        approve_submission(submission.pk, self.admin)
        self.assertEqual(Project.objects.count(), 1)
        self.assertContains(self.client.get("/"), project.title)
        self.assertNotContains(self.client.get(project.get_absolute_url()), submission.contact)
        submission.refresh_from_db()
        self.assertEqual(submission.reviewed_by, self.admin)

    def test_honeypot_and_tampered_timing_blocked(self):
        self.client.post("/submit/", self.submission(company="spam"))
        self.client.post("/submit/", self.submission(started="bad-token"))
        self.assertEqual(Submission.objects.count(), 0)

    def test_submission_cannot_set_status(self):
        self.client.post("/submit/", self.submission(status="approved"))
        self.assertEqual(Submission.objects.get().status, Submission.Status.PENDING)

    def test_public_and_session_api_writes_require_csrf(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post("/submit/", self.submission()).status_code, 403)
        client.force_login(self.admin)
        response = client.post(
            "/api/v1/projects",
            json.dumps(self.payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_api_bearer_does_not_require_csrf(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(
            "/api/v1/projects",
            json.dumps(self.payload),
            content_type="application/json",
            **self.token(),
        )
        self.assertEqual(response.status_code, 201)

    def test_rate_limit_is_enforced(self):
        for _ in range(10):
            self.client.post("/submit/", self.submission(company="spam"))
        self.assertEqual(self.client.post("/submit/", self.submission()).status_code, 429)

    def test_description_is_not_rendered_as_html(self):
        self.payload["description"] = "<script>alert(1)</script>"
        project = create_project(**self.payload, publish=True)
        self.assertNotContains(
            self.client.get(project.get_absolute_url()), "<script>alert(1)</script>"
        )

    def test_rejected_submission_not_approved(self):
        self.client.post("/submit/", self.submission())
        submission = Submission.objects.get()
        submission.status = Submission.Status.REJECTED
        submission.save()
        approve_submission(submission.pk, self.admin)
        self.assertEqual(Project.objects.count(), 0)

    def test_no_public_signup_and_docs_private(self):
        for path in ["/signup/", "/accounts/signup/", "/login/"]:
            self.assertEqual(self.client.get(path).status_code, 404)
        self.assertEqual(self.client.get("/api/v1/docs").status_code, 302)

    def test_pagination_and_empty_states(self):
        self.assertContains(self.client.get("/"), "Every collection starts with one build.")
        self.assertContains(self.client.get("/?q=missing"), "No builds match just yet.")
        self.assertEqual(self.client.get("/?page=invalid").status_code, 200)
        self.assertEqual(self.client.get("/health/").json()["status"], "ok")

    def test_sitemap_only_contains_published_projects(self):
        draft = create_project(**self.payload)
        self.assertNotContains(self.client.get("/sitemap.xml"), str(draft.pk))
        draft.status = Project.Status.PUBLISHED
        draft.full_clean()
        draft.save()
        self.assertContains(self.client.get("/sitemap.xml"), str(draft.pk))

    def test_bootstrap_does_not_reset_password_or_reenable_revoked_key(self):
        import os
        from unittest.mock import patch

        from django.core.management import call_command

        headers = self.token(active=False)
        token = headers["HTTP_AUTHORIZATION"].removeprefix("Bearer ")
        old_password = self.admin.password
        with patch.dict(
            os.environ,
            {
                "BEND_ADMIN_USERNAME": "curator",
                "BEND_ADMIN_PASSWORD": "different-password-that-must-not-be-applied",
                "BEND_ADMIN_API_KEY": token,
            },
        ):
            call_command("bootstrap_curator", verbosity=0)
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.password, old_password)
        self.assertFalse(AdminAPIKey.objects.get().active)


class OrdinaryUserTests(TestCase):
    def test_first_user_is_not_automatically_promoted(self):
        user = get_user_model().objects.create_user("ordinary-first-user")
        user.refresh_from_db()
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
