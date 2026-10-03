"""OpenStreetMap provider."""

from .provider import OSM_PROVIDER_NAME, OsmProvider
from .tags import map_osm_category

__all__ = ["OSM_PROVIDER_NAME", "OsmProvider", "map_osm_category"]
