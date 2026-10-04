import asyncio

import pytest
from fastapi.testclient import TestClient

from routeable_api.config import Settings
from routeable_api.dependencies import get_service
from routeable_api.main import create_app
from routeable_engine import AccessibilityService, InMemoryEvidenceStore
from routeable_model import GeoLocation, Place, PlaceCategory
from routeable_provider_core import ProviderRegistry

PLACE = Place(
    id="krakow:test",
    name="Test Place",
    category=PlaceCategory.MUSEUM,
    location=GeoLocation(lat=50.06, lng=19.94),
)


@pytest.fixture
def ctx() -> tuple[TestClient, InMemoryEvidenceStore]:
    store = InMemoryEvidenceStore()
    service = AccessibilityService(registry=ProviderRegistry([]), store=store)
    app = create_app(Settings(database_url=None))
    app.dependency_overrides[get_service] = lambda: service
    return TestClient(app), store


def _save_place(store: InMemoryEvidenceStore) -> None:
    asyncio.run(store.save_place(PLACE))


def test_submit_boolean_contribution(ctx: tuple[TestClient, InMemoryEvidenceStore]) -> None:
    client, store = ctx
    _save_place(store)

    response = client.post(
        "/api/places/krakow:test/community",
        json={"feature_key": "accessible_parking", "value": True},
    )

    assert response.status_code == 202
    body = response.json()
    assert body["feature_key"] == "accessible_parking"
    assert body["value"] is True
    assert body["id"]
    assert body["submitted_at"]


def test_submit_threshold_contribution(ctx: tuple[TestClient, InMemoryEvidenceStore]) -> None:
    client, store = ctx
    _save_place(store)

    response = client.post(
        "/api/places/krakow:test/community",
        json={"feature_key": "threshold_cm", "value": "small"},
    )

    assert response.status_code == 202
    assert response.json()["value"] == "small"


def test_submit_surface_contribution(ctx: tuple[TestClient, InMemoryEvidenceStore]) -> None:
    client, store = ctx
    _save_place(store)

    response = client.post(
        "/api/places/krakow:test/community",
        json={"feature_key": "surface", "value": "cobblestone"},
    )

    assert response.status_code == 202
    assert response.json()["value"] == "cobblestone"


def test_boolean_feature_rejects_string_value(
    ctx: tuple[TestClient, InMemoryEvidenceStore],
) -> None:
    client, store = ctx
    _save_place(store)

    response = client.post(
        "/api/places/krakow:test/community",
        json={"feature_key": "accessible_parking", "value": "small"},
    )

    assert response.status_code == 422


def test_threshold_feature_rejects_boolean_value(
    ctx: tuple[TestClient, InMemoryEvidenceStore],
) -> None:
    client, store = ctx
    _save_place(store)

    response = client.post(
        "/api/places/krakow:test/community",
        json={"feature_key": "threshold_cm", "value": True},
    )

    assert response.status_code == 422


def test_contribution_for_unknown_place_is_404(
    ctx: tuple[TestClient, InMemoryEvidenceStore],
) -> None:
    client, _ = ctx

    response = client.post(
        "/api/places/krakow:missing/community",
        json={"feature_key": "ramp", "value": True},
    )

    assert response.status_code == 404


def test_summary_reflects_counts(ctx: tuple[TestClient, InMemoryEvidenceStore]) -> None:
    client, store = ctx
    _save_place(store)

    for value in ("small", "small", "high"):
        client.post(
            "/api/places/krakow:test/community",
            json={"feature_key": "threshold_cm", "value": value},
        )

    response = client.get("/api/places/krakow:test/community")

    assert response.status_code == 200
    summary = response.json()
    threshold = next(f for f in summary["features"] if f["feature_key"] == "threshold_cm")
    assert threshold["total_responses"] == 3
    assert threshold["distribution"] == {"small": 2, "high": 1}
    assert threshold["top_value"] == "small"
