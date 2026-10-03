"""OpenStreetMap provider."""

from .provider import OSM_PROVIDER_NAME, OsmProvider
from .tags import SURFACE_MAP, OsmTags, map_osm_category, map_osm_tags

__all__ = [
    "OSM_PROVIDER_NAME",
    "SURFACE_MAP",
    "OsmProvider",
    "OsmTags",
    "map_osm_category",
    "map_osm_tags",
]
