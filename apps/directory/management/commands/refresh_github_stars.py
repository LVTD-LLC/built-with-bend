from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.directory.popularity import refresh_github_stars


class Command(BaseCommand):
    help = "Refresh GitHub stars, or install the idempotent hourly refresh schedule."

    def add_arguments(self, parser):
        parser.add_argument("--schedule", action="store_true")

    def handle(self, *args, **options):
        if options["schedule"]:
            from django_q.models import Schedule

            Schedule.objects.get_or_create(
                name="directory-github-stars",
                defaults={
                    "func": "apps.directory.popularity.refresh_github_stars",
                    "schedule_type": Schedule.HOURLY,
                    # Allow the matching worker revision to finish deploying first.
                    "next_run": timezone.now() + timedelta(minutes=15),
                },
            )
            self.stdout.write("GitHub star refresh schedule ready.")
        else:
            result = refresh_github_stars()
            self.stdout.write(f"Updated {result['updated']}; failed {result['failed']}.")
