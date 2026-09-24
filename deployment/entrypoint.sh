#!/bin/sh
set -eu
python - <<'PY'
import os, time
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'built_with_bend.settings')
import django
django.setup()
from django.db import connection
for attempt in range(60):
    try:
        connection.ensure_connection()
        break
    except Exception:
        if attempt == 59:
            raise SystemExit('Database unavailable after 120 seconds.') from None
        time.sleep(2)
PY
if [ "${APP_PROCESS_TYPE:-server}" = "worker" ]; then
    exec python manage.py runworker
fi
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py refresh_github_stars --schedule
if [ -n "${BEND_ADMIN_PASSWORD:-}" ]; then
    python manage.py bootstrap_curator
fi
exec gunicorn built_with_bend.asgi:application --worker-class uvicorn_worker.UvicornWorker --bind 0.0.0.0:8000 --workers 2 --access-logfile - --access-logformat '%(m)s %(U)s %(s)s' --error-logfile -
