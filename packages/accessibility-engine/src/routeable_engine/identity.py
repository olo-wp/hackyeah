"""MVP identity resolution: normalized name plus proximity (ARCHITECTURE section 36)."""

from routeable_model import ExternalPlace
from routeable_provider_core import distance_meters, normalize_name

DEFAULT_MAX_DISTANCE_M = 75.0


def is_same_place(
    a: ExternalPlace, b: ExternalPlace, max_distance_m: float = DEFAULT_MAX_DISTANCE_M
) -> bool:
    if distance_meters(a.location, b.location) > max_distance_m:
        return False

    name_a = normalize_name(a.name)
    name_b = normalize_name(b.name)
    return name_a == name_b or name_a in name_b or name_b in name_a
