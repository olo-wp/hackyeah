"""RouteAble place ids are ``<provider>:<external_id>``, e.g. ``osm:node:123456``."""

from typing import NamedTuple


class ParsedPlaceId(NamedTuple):
    provider: str
    external_id: str


def build_place_id(provider: str, external_id: str) -> str:
    return f"{provider}:{external_id}"


def parse_place_id(place_id: str) -> ParsedPlaceId:
    provider, separator, external_id = place_id.partition(":")
    if not separator or not provider or not external_id:
        raise ValueError(f'Invalid place id: "{place_id}". Expected "<provider>:<external_id>".')
    return ParsedPlaceId(provider, external_id)
