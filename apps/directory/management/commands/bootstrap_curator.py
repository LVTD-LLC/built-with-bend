import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.directory.models import AdminAPIKey


class Command(BaseCommand):
    help = "Create the initial curator from environment; preserve existing credentials."

    @transaction.atomic
    def handle(self, *args, **options):
        username = os.environ.get("BEND_ADMIN_USERNAME", "curator")
        password = os.environ.get("BEND_ADMIN_PASSWORD")
        email = os.environ.get("BEND_ADMIN_EMAIL", "")
        token = os.environ.get("BEND_ADMIN_API_KEY")
        user = get_user_model().objects.filter(username=username).first()
        if user is None:
            if not password or len(password) < 20:
                raise CommandError(
                    "Set BEND_ADMIN_PASSWORD to a strong value of at least 20 characters."
                )
            user = get_user_model().objects.create_superuser(
                username=username, email=email, password=password
            )
        if not user.is_active or not user.is_superuser:
            raise CommandError(
                "The selected user is not an active superuser; no privileges were changed."
            )
        if token:
            if len(token) < 32:
                raise CommandError("BEND_ADMIN_API_KEY must be at least 32 characters.")
            # Keep revoked keys revoked on later deploys. New keys are a deliberate rotation.
            AdminAPIKey.objects.get_or_create(
                digest=AdminAPIKey.hash_token(token),
                defaults={"user": user, "name": "Initial curator automation"},
            )
        from apps.core.models import Profile

        profile, _created = Profile.objects.get_or_create(user=user)
        mcp_key = os.environ.get("BEND_MCP_API_KEY")
        if mcp_key and not profile.has_api_key:
            profile.set_api_key(mcp_key)
            profile.save(update_fields=["api_key_prefix", "api_key_hash", "updated_at"])
        self.stdout.write(
            "Curator bootstrap complete; existing passwords and key revocations were preserved."
        )
