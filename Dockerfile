FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 PORT=8000 DJANGO_SETTINGS_MODULE=judys.settings.deploy
RUN useradd --create-home wagtail
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=wagtail:wagtail . .
RUN SECRET_KEY=build-only python manage.py collectstatic --noinput

USER wagtail
EXPOSE 8000
# Uploaded photos live in /app/media: mount a persistent volume there.
CMD set -xe; python manage.py migrate --noinput; gunicorn judys.wsgi:application --bind 0.0.0.0:$PORT
