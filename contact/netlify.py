"""Hand contact form messages to Netlify Forms.

The old site's contact form was a Netlify form called "contact". Netlify
stored each message and emailed it out using the notification settings in
the Netlify dashboard. This keeps that working: after the site saves a
message, it sends the same fields to the old Netlify site, which still has
the "contact" form registered (see netlify-forms/ and netlify.toml).

Set NETLIFY_FORMS_URL to the old site's address, e.g.
https://judys-daughter.netlify.app/ . Leave it blank to switch this off.
"""

import datetime
import logging
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings

log = logging.getLogger(__name__)


def as_text(value):
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()
    if isinstance(value, (list, tuple)):
        return ", ".join(as_text(v) for v in value)
    return "" if value is None else str(value)


def send_to_netlify(fields):
    """Post the message to Netlify Forms. Returns True if Netlify accepted it.

    Never raises: the message is already saved in the admin, so a Netlify
    problem must not stop the visitor from seeing the thank-you page.
    """
    url = getattr(settings, "NETLIFY_FORMS_URL", "")
    if not url:
        return False
    data = {"form-name": getattr(settings, "NETLIFY_FORM_NAME", "contact"), "bot-field": ""}
    data.update({name: as_text(value) for name, value in fields.items()})
    request = urllib.request.Request(
        url,
        data=urllib.parse.urlencode(data).encode(),
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "JudysDaughterWebsite/1.0 (contact form)",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            ok = 200 <= response.status < 400
    except urllib.error.HTTPError as e:
        log.error("Netlify Forms refused the contact message (HTTP %s)", e.code)
        return False
    except (urllib.error.URLError, TimeoutError) as e:
        log.error("Couldn't reach Netlify Forms: %s", e)
        return False
    if not ok:
        log.error("Netlify Forms returned an unexpected response")
    return ok
