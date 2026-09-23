"""Run Q2 with a short-lived revision heartbeat for deployment verification."""

import socket
import threading
import time

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand
from django_q.cluster import Cluster
from django_q.conf import Conf
from django_q.status import Stat


class Command(BaseCommand):
    help = "Run background tasks and publish revision readiness."

    def handle(self, *args, **options):
        def heartbeat():
            while True:
                try:
                    if any(
                        stat.host == socket.gethostname()
                        and stat.status in (Conf.IDLE, Conf.WORKING)
                        for stat in Stat.get_all()
                    ):
                        cache.set(f"bend:worker:{settings.DEPLOYMENT_REVISION}", True, timeout=20)
                except Exception:
                    # A lost broker or dead cluster cannot refresh readiness.
                    pass
                time.sleep(5)

        threading.Thread(target=heartbeat, daemon=True).start()
        Cluster().start()
