"""Feature keys and the vocabulary used to describe their state."""

from enum import StrEnum


class FeatureKey(StrEnum):
    """One concrete, observable fact about a place."""

    STEP_FREE_ENTRANCE = "step_free_entrance"
    ENTRANCE_STEPS = "entrance_steps"
    RAMP = "ramp"
    THRESHOLD_CM = "threshold_cm"
    DOOR_WIDTH_CM = "door_width_cm"
    ELEVATOR = "elevator"
    INTERIOR_STAIRS = "interior_stairs"
    ACCESSIBLE_TOILET = "accessible_toilet"
    SEATING = "seating"
    SURFACE = "surface"
    CURB = "curb"
    ACCESSIBLE_PARKING = "accessible_parking"


class SurfaceValue(StrEnum):
    ASPHALT = "asphalt"
    CONCRETE = "concrete"
    PAVING_STONES = "paving_stones"
    COBBLESTONE = "cobblestone"
    GRAVEL = "gravel"
    UNPAVED = "unpaved"
    UNKNOWN = "unknown"


class FeatureStatus(StrEnum):
    CONFIRMED = "confirmed"
    UNKNOWN = "unknown"
    CONFLICTING = "conflicting"
    STALE = "stale"


class ConfidenceLevel(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


def is_feature_key(value: str) -> bool:
    return value in FeatureKey.__members__.values()
