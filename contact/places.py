"""Check a town/city chosen from Google Places autocomplete.

The browser sends the Google place ID of the suggestion the visitor picked. We
look it up with the Places API (New) to confirm it really is a town or city,
and save Google's name for it (e.g. "Oakland, CA, USA").
"""

import json
import logging
import re
import urllib.error
import urllib.request

from django.conf import settings

log = logging.getLogger(__name__)

# Google place types that count as a town or city.
CITY_TYPES = {"locality", "postal_town", "administrative_area_level_3"}
PLACE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{10,300}$")


class NotACity(Exception):
    pass


def server_key():
    return getattr(settings, "GOOGLE_PLACES_SERVER_KEY", "")


def verify_city(place_id):
    """Return Google's name for the place, or raise NotACity.

    Returns None if Google can't be reached, so a Google outage never stops
    someone from sending a message (the typed text is kept instead).
    """
    if not PLACE_ID_RE.match(place_id or ""):
        raise NotACity
    request = urllib.request.Request(
        f"https://places.googleapis.com/v1/places/{place_id}",
        headers={
            "X-Goog-Api-Key": server_key(),
            "X-Goog-FieldMask": "formattedAddress,types",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            place = json.load(response)
    except urllib.error.HTTPError as e:
        if e.code in (400, 404):
            raise NotACity from e
        log.warning("Places lookup failed (%s); keeping typed value", e.code)
        return None
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        log.warning("Places lookup failed (%s); keeping typed value", e)
        return None
    if not CITY_TYPES & set(place.get("types", [])):
        raise NotACity
    return place.get("formattedAddress") or None
