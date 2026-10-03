"""Geo and name helpers shared by providers and the identity resolver."""

import math
import re
import unicodedata

from routeable_model import GeoLocation

EARTH_RADIUS_M = 6_371_000
_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def normalize_name(name: str) -> str:
    decomposed = unicodedata.normalize("NFD", name)
    stripped = "".join(char for char in decomposed if not unicodedata.combining(char))
    return _NON_ALNUM.sub(" ", stripped.lower()).strip()


def distance_meters(a: GeoLocation, b: GeoLocation) -> float:
    lat1, lat2 = math.radians(a.lat), math.radians(b.lat)
    d_lat = lat2 - lat1
    d_lng = math.radians(b.lng - a.lng)

    h = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lng / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(h))
