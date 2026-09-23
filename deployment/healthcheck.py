"""Probe the local process and database before Swarm completes a rollout."""

import json
import os
from urllib.request import Request, urlopen

request = Request("http://127.0.0.1:8000/health/", headers={"X-Forwarded-Proto": "https"})
with urlopen(request, timeout=4) as response:
    health = json.load(response)
if health.get("status") != "ok" or health.get("revision") != os.environ["DEPLOYMENT_REVISION"]:
    raise SystemExit("Local health or revision check failed.")
