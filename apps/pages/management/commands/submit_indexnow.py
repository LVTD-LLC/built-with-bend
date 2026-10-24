from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.pages.indexnow import IndexNowError, read_snapshot, submit


class Command(BaseCommand):
    help = "Submit the live public sitemap to IndexNow (never private catalogue URLs)."
    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument(
            "--previous",
            type=Path,
            help="Pre-deployment URL-to-lastmod JSON snapshot for delta notifications",
        )

    def handle(self, *args, **options):
        try:
            previous = (
                read_snapshot(settings.SITE_URL, options["previous"])
                if options["previous"]
                else None
            )
            result = submit(settings.SITE_URL, previous, dry_run=options["dry_run"])
        except (IndexNowError, ValueError, OSError) as error:
            raise CommandError(str(error)) from None
        self.stdout.write(result)
