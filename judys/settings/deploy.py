import os

from .base import *  # noqa: F401,F403

DEBUG = False
SECRET_KEY = os.environ["SECRET_KEY"]
# Render provides the service's own address in RENDER_EXTERNAL_HOSTNAME.
RENDER_HOST = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "")
# Forgiving about how the list is typed: spaces, "https://" and "/" are ignored.
ALLOWED_HOSTS = [
    h.strip().removeprefix("https://").removeprefix("http://").rstrip("/")
    for h in os.environ.get("ALLOWED_HOSTS", "").split(",") + [RENDER_HOST]
]
ALLOWED_HOSTS = [h for h in ALLOWED_HOSTS if h]
CSRF_TRUSTED_ORIGINS = [f"https://{h}" for h in ALLOWED_HOSTS]
WAGTAILADMIN_BASE_URL = os.environ.get("WAGTAILADMIN_BASE_URL") or (
    f"https://{RENDER_HOST}" if RENDER_HOST else "https://judysdaughter.support"
)

# Uploaded photos live on a persistent disk (see render.yaml).
MEDIA_ROOT = os.environ.get("MEDIA_ROOT", str(MEDIA_ROOT))  # noqa: F405

# Staging: every page is marked "don't index" and shows a small staging banner.
STAGING = os.environ.get("STAGING", "false") == "true"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "true") == "true"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Serve uploaded photos from the app itself (fine for a small site on one
# server with a persistent disk). Set to false if a CDN or bucket serves /media/.
SERVE_MEDIA = os.environ.get("SERVE_MEDIA", "true") == "true"

# Email for contact-form notifications and password resets. Until an email
# server is configured, nothing is sent (and nothing personal goes in the logs);
# messages are still saved under Forms in the admin.
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
    if EMAIL_HOST
    else "django.core.mail.backends.dummy.EmailBackend"
)
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL") or os.environ.get(
    "CONTACT_EMAIL", "webmaster@localhost"
)
WAGTAILADMIN_NOTIFICATION_FROM_EMAIL = DEFAULT_FROM_EMAIL
