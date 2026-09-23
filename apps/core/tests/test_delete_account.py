import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse


@pytest.mark.django_db
def test_delete_account_requires_confirmation(auth_client, user):
    url = reverse("delete_account")

    response = auth_client.post(url, data={"confirmation": "nope"})
    assert response.status_code == 302

    # user should still exist
    assert get_user_model().objects.filter(id=user.id).exists()


@pytest.mark.django_db
def test_delete_account_deletes_user(auth_client, user):
    url = reverse("delete_account")

    response = auth_client.post(url, data={"confirmation": "DELETE"})

    assert response.status_code == 302
    assert response["Location"].startswith(reverse("landing"))

    assert not get_user_model().objects.filter(id=user.id).exists()


@pytest.mark.django_db
@pytest.mark.parametrize("cookie", [None, "granted", "denied"])
def test_deletion_queues_analytics_after_commit_without_consent(
    auth_client, user, settings, monkeypatch, django_capture_on_commit_callbacks, cookie
):
    settings.POSTHOG_API_KEY = "phc_test"
    profile_id = user.profile.id
    queued = []
    monkeypatch.setattr("apps.core.analytics.async_task", lambda *a, **kw: queued.append((a, kw)))
    if cookie is not None:
        auth_client.cookies["analytics_consent"] = cookie

    with django_capture_on_commit_callbacks(execute=True):
        response = auth_client.post(reverse("delete_account"), {"confirmation": "DELETE"})
        assert queued == []

    assert response.status_code == 302
    assert not get_user_model().objects.filter(id=user.id).exists()
    assert len(queued) == 1
    assert queued[0][0] == ("apps.core.tasks.track_account_deleted_event",)
    assert queued[0][1]["profile_id"] == profile_id
