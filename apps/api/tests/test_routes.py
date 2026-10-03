import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest
import respx
from fastapi.testclient import TestClient

from routeable_api.config import Settings
from routeable_api.dependencies import get_service
from routeable_api.main import create_app
from routeable_model import GeoLocation, Place

ORS_URL = "https://api.openrouteservice.org"


def client_with_key(key: str | None = "test-only") -> TestClient:
    app = create_app(Settings(_env_file=None, ors_api_key=key, database_url=None))
    app.dependency_overrides[get_service] = lambda: SimpleNamespace(
        get_place=AsyncMock(
            return_value=Place(
                id="krakow:museum",
                name="Muzeum",
                location=GeoLocation(lat=50.07, lng=19.94),
            )
        )
    )
    return TestClient(app)


@respx.mock
def test_search_origins_returns_locations() -> None:
    respx.get(f"{ORS_URL}/geocode/search").mock(
        return_value=httpx.Response(
            200,
            json={
                "features": [
                    {
                        "properties": {"label": "Rynek Główny, Kraków"},
                        "geometry": {"coordinates": [19.936, 50.062]},
                    },
                    {
                        "properties": {"label": "Rynek Podgórski, Kraków"},
                        "geometry": {"coordinates": [19.944, 50.042]},
                    },
                ]
            },
        )
    )

    response = client_with_key().get("/api/routes/origins", params={"q": "Rynek"})

    assert response.status_code == 200, response.json()
    assert response.json()["results"][0]["location"] == {"lat": 50.062, "lng": 19.936}
    assert len(response.json()["results"]) == 2


@respx.mock
def test_walking_route_uses_stored_destination_coordinates() -> None:
    route = respx.post(f"{ORS_URL}/v2/directions/foot-walking/geojson").mock(
        return_value=httpx.Response(
            200,
            json={
                "features": [
                    {
                        "geometry": {
                            "type": "LineString",
                            "coordinates": [[19.93, 50.06], [19.94, 50.07]],
                        },
                        "properties": {"summary": {"distance": 1500, "duration": 1200}},
                    }
                ]
            },
        )
    )

    response = client_with_key().post(
        "/api/routes/walking",
        json={"place_id": "krakow:museum", "start": {"lat": 50.06, "lng": 19.93}},
    )

    assert response.status_code == 200
    assert response.json()["distance_m"] == 1500
    assert response.json()["geometry"]["coordinates"] == [[19.93, 50.06], [19.94, 50.07]]
    assert json.loads(route.calls.last.request.content)["coordinates"] == [
        [19.93, 50.06],
        [19.94, 50.07],
    ]


@pytest.mark.parametrize("response_status,expected_status", [(404, 404), (429, 429), (503, 502)])
@respx.mock
def test_provider_failure_is_reported(response_status: int, expected_status: int) -> None:
    respx.post(f"{ORS_URL}/v2/directions/foot-walking/geojson").mock(
        return_value=httpx.Response(response_status)
    )
    response = client_with_key().post(
        "/api/routes/walking",
        json={"place_id": "krakow:museum", "start": {"lat": 50.06, "lng": 19.93}},
    )
    assert response.status_code == expected_status


@respx.mock
def test_no_route_and_invalid_coordinates() -> None:
    respx.post(f"{ORS_URL}/v2/directions/foot-walking/geojson").mock(
        return_value=httpx.Response(200, json={"features": []})
    )
    client = client_with_key()
    assert (
        client.post(
            "/api/routes/walking",
            json={"place_id": "krakow:museum", "start": {"lat": 50.06, "lng": 19.93}},
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/api/routes/walking",
            json={"place_id": "krakow:museum", "start": {"lat": 200, "lng": 19.93}},
        ).status_code
        == 422
    )


@respx.mock
def test_missing_key_never_calls_provider() -> None:
    response = client_with_key(None).get("/api/routes/origins", params={"q": "Rynek"})
    assert response.status_code == 503
    assert not respx.calls


@respx.mock
def test_provider_timeout_returns_bad_gateway() -> None:
    respx.get(f"{ORS_URL}/geocode/search").mock(side_effect=httpx.ConnectTimeout("timed out"))
    response = client_with_key().get("/api/routes/origins", params={"q": "Rynek"})
    assert response.status_code == 502
    assert response.json()["detail"] == "Routing provider unavailable"
