"""OSM place categories; accessibility tags are classified by AI."""

from routeable_model import PlaceCategory

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
