"""Provider contract, registry and shared provider utilities."""

from .geo import distance_meters, normalize_name
from .http import (
    DEFAULT_MAX_BYTES,
    DEFAULT_TIMEOUT_S,
    HttpClient,
    ProviderHttpError,
    system_ssl_context,
)
from .protocol import AccessibilityProvider, SearchOptions
from .registry import ProviderRegistry

__all__ = [
    "DEFAULT_MAX_BYTES",
    "DEFAULT_TIMEOUT_S",
    "AccessibilityProvider",
    "HttpClient",
    "ProviderHttpError",
    "ProviderRegistry",
    "SearchOptions",
    "distance_meters",
    "normalize_name",
    "system_ssl_context",
]
