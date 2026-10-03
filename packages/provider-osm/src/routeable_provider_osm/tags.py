"""OSM tag -> RouteAble fact mapping.

``wheelchair=yes`` is treated as an *observation about the entrance*, not a verdict.
If another source reports steps, the engine surfaces the conflict.
"""

from typing import Any

from routeable_model import (
    FeatureKey,
    PlaceCategory,
    RawAccessibilityEvidence,
    SurfaceValue,
    VerificationStatus,
)

OsmTags = dict[str, str]

_TRUE_VALUES = {"yes", "designated", "true", "1"}
_FALSE_VALUES = {"no", "false", "0"}

SURFACE_MAP: dict[str, SurfaceValue] = {
    "asphalt": SurfaceValue.ASPHALT,
    "concrete": SurfaceValue.CONCRETE,
    "concrete:plates": SurfaceValue.CONCRETE,
    "paving_stones": SurfaceValue.PAVING_STONES,
    "sett": SurfaceValue.COBBLESTONE,
    "cobblestone": SurfaceValue.COBBLESTONE,
    "cobblestone:flattened": SurfaceValue.COBBLESTONE,
    "unhewn_cobblestone": SurfaceValue.COBBLESTONE,
    "gravel": SurfaceValue.GRAVEL,
    "fine_gravel": SurfaceValue.GRAVEL,
    "compacted": SurfaceValue.GRAVEL,
    "ground": SurfaceValue.UNPAVED,
    "dirt": SurfaceValue.UNPAVED,
    "earth": SurfaceValue.UNPAVED,
    "grass": SurfaceValue.UNPAVED,
    "sand": SurfaceValue.UNPAVED,
    "unpaved": SurfaceValue.UNPAVED,
}

CATEGORY_MAP: dict[str, PlaceCategory] = {
    "museum": PlaceCategory.MUSEUM,
    "hotel": PlaceCategory.HOTEL,
    "hostel": PlaceCategory.HOTEL,
    "guest_house": PlaceCategory.HOTEL,
    "apartment": PlaceCategory.HOTEL,
    "restaurant": PlaceCategory.RESTAURANT,
    "cafe": PlaceCategory.RESTAURANT,
    "fast_food": PlaceCategory.RESTAURANT,
    "bar": PlaceCategory.RESTAURANT,
    "pub": PlaceCategory.RESTAURANT,
    "attraction": PlaceCategory.ATTRACTION,
    "viewpoint": PlaceCategory.ATTRACTION,
    "gallery": PlaceCategory.ATTRACTION,
    "artwork": PlaceCategory.ATTRACTION,
    "theatre": PlaceCategory.EVENT_VENUE,
    "cinema": PlaceCategory.EVENT_VENUE,
    "arts_centre": PlaceCategory.EVENT_VENUE,
    "community_centre": PlaceCategory.EVENT_VENUE,
    "events_venue": PlaceCategory.EVENT_VENUE,
    "conference_centre": PlaceCategory.EVENT_VENUE,
}


def map_osm_category(klass: str | None, type_: str | None) -> PlaceCategory:
    return CATEGORY_MAP.get(type_ or "") or CATEGORY_MAP.get(klass or "") or PlaceCategory.OTHER


def _yes_no(value: str | None) -> bool | None:
    if value is None:
        return None
    if value in _TRUE_VALUES:
        return True
    if value in _FALSE_VALUES:
        return False
    return None


def _to_number(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value.replace(",", "."))
    except ValueError:
        return None


def _width_to_cm(value: str | None) -> float | None:
    """OSM widths are metres unless a unit is given; RouteAble stores centimetres."""
    if value is None:
        return None

    normalized = value.strip().lower()
    numeric = _to_number("".join(c for c in normalized if c.isdigit() or c in ".,"))
    if numeric is None:
        return None
    if normalized.endswith("cm"):
        return round(numeric)
    if normalized.endswith("mm"):
        return round(numeric / 10)
    return round(numeric * 100)


def map_osm_tags(tags: OsmTags, source_url: str | None = None) -> list[RawAccessibilityEvidence]:
    evidence: list[RawAccessibilityEvidence] = []

    def push(feature_key: FeatureKey, value: Any, raw_tag: str) -> None:
        if value is None:
            return
        evidence.append(
            RawAccessibilityEvidence(
                feature_key=feature_key,
                value=value,
                verification_status=VerificationStatus.UNVERIFIED,
                raw_data={"tag": raw_tag, "value": tags.get(raw_tag)},
                source_url=source_url,
            )
        )

    wheelchair = tags.get("wheelchair")
    if wheelchair in ("yes", "no"):
        push(FeatureKey.STEP_FREE_ENTRANCE, wheelchair == "yes", "wheelchair")

    step_count = _to_number(tags.get("entrance:step_count") or tags.get("step_count"))
    if step_count is not None:
        push(FeatureKey.ENTRANCE_STEPS, int(step_count), "step_count")

    push(FeatureKey.RAMP, _yes_no(tags.get("ramp:wheelchair") or tags.get("ramp")), "ramp")
    push(
        FeatureKey.THRESHOLD_CM,
        _width_to_cm(tags.get("kerb:height") or tags.get("entrance:threshold")),
        "kerb:height",
    )
    push(
        FeatureKey.DOOR_WIDTH_CM,
        _width_to_cm(tags.get("door:width") or tags.get("width")),
        "door:width",
    )
    push(
        FeatureKey.ACCESSIBLE_TOILET,
        _yes_no(tags.get("toilets:wheelchair")),
        "toilets:wheelchair",
    )
    push(FeatureKey.SEATING, _yes_no(tags.get("bench")), "bench")

    is_elevator = tags.get("highway") == "elevator" or tags.get("building:part") == "elevator"
    push(FeatureKey.ELEVATOR, True if is_elevator else _yes_no(tags.get("elevator")), "elevator")

    kerb = tags.get("kerb")
    if kerb is not None:
        push(FeatureKey.CURB, kerb not in ("flush", "no"), "kerb")

    disabled_capacity = _to_number(tags.get("capacity:disabled"))
    if disabled_capacity is not None:
        accessible_parking = disabled_capacity > 0
    else:
        accessible_parking = _yes_no(tags.get("parking:disabled"))
    push(FeatureKey.ACCESSIBLE_PARKING, accessible_parking, "capacity:disabled")

    surface = SURFACE_MAP.get(tags.get("surface", ""))
    if surface is not None:
        push(FeatureKey.SURFACE, surface, "surface")

    return evidence
