#!/usr/bin/env bash
# Start command for Render (see render.yaml). Safe to run on every deploy.
set -euo pipefail

python manage.py migrate --noinput
python manage.py seed_site                      # loads content the first time only
python manage.py seed_site --site-host "${SITE_HOSTNAME:-${RENDER_EXTERNAL_HOSTNAME:-}}"

# First deploy: create the admin login from DJANGO_SUPERUSER_* if it doesn't exist yet.
if [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
  python manage.py createsuperuser --noinput 2>/dev/null || echo "Admin login already exists."
fi

exec gunicorn judys.wsgi --bind "0.0.0.0:${PORT:-10000}" --workers 2 --timeout 60
