from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.directory.thumbnail_storage import refresh_thumbnails


class Command(BaseCommand):
    help = "Copy reviewed thumbnails to R2, or configure the periodic reconciliation job."

    def add_arguments(self, parser):
        parser.add_argument("--schedule", action="store_true")

    def handle(self, *args, **options):
        if options["schedule"]:
            from django_q.models import Schedule

            if settings.THUMBNAIL_R2_ENABLED:
                Schedule.objects.get_or_create(
                    name="Import project thumbnails to R2",
                    defaults={
                        "func": "apps.directory.thumbnail_storage.refresh_thumbnails",
                        "schedule_type": Schedule.MINUTES,
                        "minutes": 1,
                        "repeats": -1,
                        # Let the newly deployed worker start before scheduling new code.
                        "next_run": timezone.now() + timedelta(minutes=5),
                    },
                )
            self.stdout.write("Thumbnail schedule configured; disabled when R2 is not enabled.")
        else:
            self.stdout.write(str(refresh_thumbnails()))
