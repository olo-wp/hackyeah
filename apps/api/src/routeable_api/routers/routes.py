"""Walking routes to places, backed by OpenRouteService."""

import json
from typing import Annotated, Literal

import httpx
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field, ValidationError

from routeable_model import GeoLocation
from routeable_provider_core import system_ssl_context

from ..dependencies import PLACE_ID_PATTERN, ServiceDep

router = APIRouter(prefix="/api/routes", tags=["routes"])
ORS_URL = "https://api.openrouteservice.org"
MAX_RESPONSE_BYTES = 2 * 1024 * 1024


class Origin(BaseModel):
    label: str
    location: GeoLocation


class OriginResults(BaseModel):
    results: list[Origin]


class WalkingRequest(BaseModel):
    place_id: str = Field(min_length=3, max_length=120, pattern=PLACE_ID_PATTERN)
    start: GeoLocation


class RouteGeometry(BaseModel):
    type: Literal["LineString"]
    coordinates: list[tuple[float, float]] = Field(min_length=2)


class WalkingRoute(BaseModel):
    geometry: RouteGeometry
    distance_m: float = Field(ge=0)
    duration_s: float = Field(ge=0)


class GeocodeGeometry(BaseModel):
    coordinates: tuple[float, float]


class OrsProperties(BaseModel):
    label: str


class GeocodeFeature(BaseModel):
    geometry: GeocodeGeometry
    properties: OrsProperties


class GeocodeResponse(BaseModel):
    features: list[GeocodeFeature]


class RouteSummary(BaseModel):
    distance: float
    duration: float


class RouteProperties(BaseModel):
    summary: RouteSummary


class RouteFeature(BaseModel):
    geometry: RouteGeometry
    properties: RouteProperties


class RouteResponse(BaseModel):
    features: list[RouteFeature]


async def ors_request(
    request: Request,
    method: str,
    path: str,
    params: dict[str, str | int | float] | None = None,
    body: dict[str, object] | None = None,
) -> object:
    api_key = request.app.state.route_settings.ors_api_key
    if api_key is None:
        raise HTTPException(status_code=503, detail="Routing is not configured")

    try:
        async with (
            httpx.AsyncClient(
                verify=system_ssl_context(),
                timeout=8.0,
                headers={
                    "Authorization": api_key.get_secret_value(),
                    "User-Agent": request.app.state.route_settings.user_agent,
                },
            ) as client,
            client.stream(method, f"{ORS_URL}{path}", params=params, json=body) as response,
        ):
            if response.status_code == 429:
                raise HTTPException(status_code=429, detail="Routing quota exceeded")
            if response.status_code == 404 and path.endswith("/geojson"):
                raise HTTPException(status_code=404, detail="No walking route found")
            response.raise_for_status()
            response_body = bytearray()
            async for chunk in response.aiter_bytes():
                response_body.extend(chunk)
                if len(response_body) > MAX_RESPONSE_BYTES:
                    raise HTTPException(status_code=502, detail="Routing response too large")
        return json.loads(response_body)
    except (httpx.HTTPError, ValueError) as error:
        raise HTTPException(status_code=502, detail="Routing provider unavailable") from error


@router.get("/origins", response_model=OriginResults)
async def search_origins(
    request: Request, q: Annotated[str, Query(min_length=3, max_length=120)]
) -> OriginResults:
    payload = await ors_request(
        request,
        "GET",
        "/geocode/search",
        params={
            "text": q,
            "size": 5,
            "boundary.circle.lat": 50.0614,
            "boundary.circle.lon": 19.9366,
            "boundary.circle.radius": 20,
        },
    )
    try:
        features = GeocodeResponse.model_validate(payload).features
        return OriginResults(
            results=[
                Origin(
                    label=feature.properties.label,
                    location=GeoLocation(
                        lat=feature.geometry.coordinates[1],
                        lng=feature.geometry.coordinates[0],
                    ),
                )
                for feature in features[:5]
            ]
        )
    except (ValidationError, IndexError) as error:
        raise HTTPException(status_code=502, detail="Invalid geocoding response") from error


@router.post("/walking", response_model=WalkingRoute)
async def walking_route(
    request: Request, route: WalkingRequest, service: ServiceDep
) -> WalkingRoute:
    place = await service.get_place(route.place_id)
    payload = await ors_request(
        request,
        "POST",
        "/v2/directions/foot-walking/geojson",
        body={
            "coordinates": [
                [route.start.lng, route.start.lat],
                [place.location.lng, place.location.lat],
            ]
        },
    )
    try:
        features = RouteResponse.model_validate(payload).features
        if not features:
            raise HTTPException(status_code=404, detail="No walking route found")
        feature = features[0]
        return WalkingRoute(
            geometry=feature.geometry,
            distance_m=feature.properties.summary.distance,
            duration_s=feature.properties.summary.duration,
        )
    except ValidationError as error:
        raise HTTPException(status_code=502, detail="Invalid routing response") from error
