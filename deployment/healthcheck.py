"""Probe the local process and database before Swarm completes a rollout."""

import json
import os
from urllib.request import Request, urlopen

if os.environ.get("APP_PROCESS_TYPE") == "worker":
    import socket

    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "built_with_bend.settings")
    django.setup()
    from django_q.conf import Conf
    from django_q.status import Stat

    healthy = any(
        stat.host == socket.gethostname() and stat.status in (Conf.IDLE, Conf.WORKING)
        for stat in Stat.get_all()
    )
    raise SystemExit(0 if healthy else 1)

request = Request("http://127.0.0.1:8000/health/", headers={"X-Forwarded-Proto": "https"})
with urlopen(request, timeout=4) as response:
    health = json.load(response)
if health.get("status") != "ok" or health.get("revision") != os.environ["DEPLOYMENT_REVISION"]:
    raise SystemExit("Local health or revision check failed.")
