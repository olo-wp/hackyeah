"""Offline Gemini tests. Live tests using the owner's paid key are disabled.

Do not load .env or use real credentials here. Every HTTP request must be mocked.
"""

import json
from unittest.mock import AsyncMock

import httpx
import pytest
import respx

from routeable_model import ExternalPlace, FeatureKey, GeoLocation, PlaceCategory
from routeable_provider_core import GeminiAccessibilityClassifier, SourceDocument
from routeable_provider_osm import OsmProvider
from routeable_provider_websites import GoogleSearchProvider, WebsiteProvider, html_to_text

ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent"
)
SOURCE = "https://example.org/accessibility"
PLACE = ExternalPlace(
    external_id="node:123",
    provider_name="osm",
    name="Muzeum Testowe",
    category=PlaceCategory.MUSEUM,
    address="ul. Testowa 1, Kraków",
    location=GeoLocation(lat=50.06, lng=19.93),
)


@pytest.fixture(autouse=True)
def block_live_api_calls(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    # Unregistered requests fail locally; they must never reach a paid API.
    with respx.mock(assert_all_mocked=True, assert_all_called=False):
        yield


async def test_unmocked_api_request_is_blocked():
    async with httpx.AsyncClient() as client:
        with pytest.raises(AssertionError, match="not mocked"):
            await client.post(ENDPOINT, headers={"x-goog-api-key": "test-key"}, json={})


def response(text: str, metadata: dict | None = None, finish: str = "STOP") -> dict:
    return {
        "candidates": [
            {
                "finishReason": finish,
                "content": {"parts": [{"text": text}]},
                "groundingMetadata": metadata or {},
            }
        ]
    }


def fact(key: str, value: object, url: str = SOURCE, snippet: str = "Brak windy.") -> dict:
    return {
        "feature_key": key,
        "value_json": json.dumps(value),
        "source_url": url,
        "snippet": snippet,
    }


@respx.mock
async def test_classifies_negation_and_rejects_unsubstantiated_or_invalid_facts():
    route = respx.post(ENDPOINT).mock(
        return_value=httpx.Response(
            200,
            json=response(
                json.dumps(
                    {
                        "facts": [
                            fact("elevator", False),
                            fact("ramp", True, snippet="Jest podjazd."),
                            fact("seating", True, url="https://invented.example/"),
                            fact("door_width_cm", True),
                            fact("entrance_steps", -1),
                            fact("surface", "unknown"),
                            fact("accessible_toilet", "true"),
                            fact("curb", None),
                            fact("made_up_feature", True),
                        ]
                    }
                )
            ),
        )
    )
    classifier = GeminiAccessibilityClassifier("test-key")
    try:
        evidence = await classifier.classify(PLACE, [SourceDocument(SOURCE, "Brak windy.")])
    finally:
        await classifier.aclose()
    assert [(item.feature_key, item.value) for item in evidence] == [(FeatureKey.ELEVATOR, False)]
    assert evidence[0].verification_status == "automatically_extracted"
    assert evidence[0].source_url == SOURCE
    payload = json.loads(route.calls[0].request.content)
    assert payload["generationConfig"]["responseFormat"]["text"]["mimeType"] == "APPLICATION_JSON"
    assert "tools" not in payload
    assert route.calls[0].request.headers["x-goog-api-key"] == "test-key"


@respx.mock
async def test_search_classifies_only_cited_segments_and_preserves_conflicts():
    other = "https://example.org/old-statement"
    metadata = {
        "webSearchQueries": ["Muzeum Testowe Kraków dostępność winda"],
        "groundingChunks": [{"web": {"uri": SOURCE}}, {"web": {"uri": other}}],
        "groundingSupports": [
            {"segment": {"text": "Brak windy."}, "groundingChunkIndices": [0]},
            {"segment": {"text": "Jest winda."}, "groundingChunkIndices": [1]},
        ],
        "searchEntryPoint": {"renderedContent": "<div>Search suggestions</div>"},
    }
    route = respx.post(ENDPOINT).mock(
        side_effect=[
            httpx.Response(
                200, json=response("Brak windy. Jest winda. Uncited speculation.", metadata)
            ),
            httpx.Response(
                200,
                json=response(
                    json.dumps(
                        {
                            "facts": [
                                fact("elevator", False),
                                fact("elevator", True, url=other, snippet="Jest winda."),
                            ]
                        }
                    )
                ),
            ),
        ]
    )
    classifier = GeminiAccessibilityClassifier("test-key")
    provider = GoogleSearchProvider(classifier)
    try:
        evidence = await provider.get_accessibility_data(PLACE)
    finally:
        await provider.aclose()
    assert [item.value for item in evidence] == [False, True]
    assert [item.source_url for item in evidence] == [SOURCE, other]
    assert evidence[0].raw_data["grounding_metadata"] == metadata
    research = json.loads(route.calls[0].request.content)
    assert research["tools"] == [{"google_search": {}}]
    assert "Kraków" in research["contents"][0]["parts"][0]["text"]
    classification = json.loads(route.calls[1].request.content)
    assert "Uncited speculation" not in classification["contents"][0]["parts"][0]["text"]


@respx.mock
async def test_search_without_search_execution_is_failed():
    respx.post(ENDPOINT).mock(return_value=httpx.Response(200, json=response("Model knowledge")))
    classifier = GeminiAccessibilityClassifier("test-key")
    try:
        with pytest.raises(RuntimeError, match="required Google Search"):
            await classifier.search_accessibility(PLACE)
    finally:
        await classifier.aclose()


@respx.mock
async def test_search_without_cited_facts_stays_unknown():
    route = respx.post(ENDPOINT).mock(
        return_value=httpx.Response(
            200, json=response("No information", {"webSearchQueries": ["museum accessibility"]})
        )
    )
    classifier = GeminiAccessibilityClassifier("test-key")
    try:
        assert await classifier.search_accessibility(PLACE) == []
    finally:
        await classifier.aclose()
    assert route.call_count == 1


@pytest.mark.parametrize(
    "upstream",
    [
        httpx.Response(429, json={"error": "sensitive upstream body"}),
        httpx.Response(200, json=response("{broken JSON")),
        httpx.Response(200, json=response('{"facts": []}', finish="MAX_TOKENS")),
        httpx.Response(200, json={"promptFeedback": {"blockReason": "SAFETY"}}),
    ],
)
@respx.mock
async def test_upstream_failures_are_explicit(upstream):
    respx.post(ENDPOINT).mock(return_value=upstream)
    classifier = GeminiAccessibilityClassifier("test-key")
    try:
        with pytest.raises(RuntimeError) as error:
            await classifier.classify(PLACE, [SourceDocument(SOURCE, "Brak windy.")])
    finally:
        await classifier.aclose()
    assert "sensitive upstream body" not in str(error.value)


async def test_missing_key_is_explicit():
    classifier = GeminiAccessibilityClassifier(None)
    try:
        with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
            await classifier.classify(PLACE, [SourceDocument(SOURCE, "Brak windy.")])
    finally:
        await classifier.aclose()


@respx.mock
async def test_osm_passes_raw_tags_to_ai_instead_of_mapping_wheelchair_to_step_free():
    respx.post("https://overpass-api.de/api/interpreter").mock(
        return_value=httpx.Response(
            200, json={"elements": [{"tags": {"wheelchair": "yes", "description": "3 steps"}}]}
        )
    )
    classifier = AsyncMock()
    classifier.classify.return_value = []
    provider = OsmProvider(classifier=classifier)
    try:
        assert await provider.get_accessibility_data(PLACE) == []
    finally:
        await provider.aclose()
    call = classifier.classify.call_args
    assert call.args[0] == PLACE
    assert json.loads(call.args[1][0].text)["wheelchair"] == "yes"
    assert call.args[1][0].url == "https://www.openstreetmap.org/node/123"


@respx.mock
async def test_website_passes_visible_text_to_ai(tmp_path):
    path = tmp_path / "allowlist.json"
    path.write_text(
        json.dumps(
            {
                "sites": [
                    {
                        "domain": "example.org",
                        "allowed": True,
                        "place_ids": ["osm:node:123"],
                        "accessibility_pages": ["/accessibility"],
                    }
                ]
            }
        )
    )
    respx.get(SOURCE).mock(
        return_value=httpx.Response(
            200, text="<p>Brak <b>windy</b>.</p><script>Jest winda.</script>"
        )
    )
    classifier = AsyncMock()
    classifier.classify.return_value = []
    provider = WebsiteProvider(allowlist_path=path, classifier=classifier)
    try:
        assert await provider.get_accessibility_data(PLACE) == []
    finally:
        await provider.aclose()
    document = classifier.classify.call_args.args[1][0]
    assert "Brak" in document.text and "windy" in document.text
    assert "Jest winda" not in document.text
    assert document.url == SOURCE


def test_html_parsing_without_regex():
    assert html_to_text("<style>hidden</style><p>Wejście&nbsp;bez schodów</p>") == (
        "Wejście bez schodów"
    )


@respx.mock
async def test_bounds_input_and_preserves_valid_measurements():
    route = respx.post(ENDPOINT).mock(
        return_value=httpx.Response(
            200, json=response(json.dumps({"facts": [fact("door_width_cm", 90, snippet="90 cm")]}))
        )
    )
    classifier = GeminiAccessibilityClassifier("test-key", max_input_chars=5)
    try:
        evidence = await classifier.classify(PLACE, [SourceDocument(SOURCE, "90 cm" + "x" * 1000)])
    finally:
        await classifier.aclose()
    assert evidence[0].value == 90
    payload = json.loads(route.calls[0].request.content)
    documents = json.loads(payload["contents"][0]["parts"][0]["text"])["documents"]
    assert documents == [{"url": SOURCE, "text": "90 cm"}]


@respx.mock
async def test_google_search_enriches_profile_when_osm_has_no_data_and_is_cached():
    from types import SimpleNamespace

    from routeable_engine import AccessibilityService, InMemoryEvidenceStore
    from routeable_model import DataSource, SourceType
    from routeable_provider_core import ProviderRegistry

    metadata = {
        "webSearchQueries": ["Muzeum Testowe Kraków dostępność"],
        "groundingChunks": [{"web": {"uri": SOURCE}}],
        "groundingSupports": [
            {
                "segment": {"text": "Brak windy."},
                "groundingChunkIndices": [0],
            }
        ],
    }
    route = respx.post(ENDPOINT).mock(
        side_effect=[
            httpx.Response(200, json=response("Brak windy.", metadata)),
            httpx.Response(200, json=response(json.dumps({"facts": [fact("elevator", False)]}))),
        ]
    )
    owner = SimpleNamespace(
        name="osm",
        source=DataSource(id="osm", type=SourceType.OPENSTREETMAP, name="OSM"),
        get_place=AsyncMock(return_value=PLACE),
        get_accessibility_data=AsyncMock(return_value=[]),
        aclose=AsyncMock(),
    )
    classifier = GeminiAccessibilityClassifier("test-key")
    registry = ProviderRegistry([owner, GoogleSearchProvider(classifier)])
    service = AccessibilityService(registry, InMemoryEvidenceStore())
    try:
        first = await service.get_place_accessibility("osm:node:123")
        second = await service.get_place_accessibility("osm:node:123")
    finally:
        await registry.aclose()
    evidence = first.profile.interior.elevator.evidence
    assert first.profile.interior.elevator.value is False
    assert evidence[0].source.type == "google_search"
    assert evidence[0].source.url == SOURCE
    assert first.profile.entrance.step_free.status == "unknown"
    assert all(status.status == "cached" for status in second.provider_status)
    assert route.call_count == 2


@respx.mock
async def test_upstream_diagnostics_are_kept_without_key_or_full_body():
    route = respx.post(ENDPOINT).mock(
        return_value=httpx.Response(
            400,
            json={
                "error": {
                    "status": "INVALID_ARGUMENT",
                    "message": "Invalid schema for test-key",
                    "details": [{"private": "do not expose full details"}],
                },
            },
        )
    )
    classifier = GeminiAccessibilityClassifier("test-key")
    try:
        with pytest.raises(RuntimeError) as error:
            await classifier.classify(PLACE, [SourceDocument(SOURCE, "Brak windy.")])
    finally:
        await classifier.aclose()
    assert "HTTP 400" in str(error.value)
    assert "INVALID_ARGUMENT" in str(error.value)
    assert "Invalid schema" in str(error.value)
    assert "test-key" not in str(error.value)
    assert "do not expose full details" not in str(error.value)
    assert route.call_count == 1


@respx.mock
async def test_fact_count_limit_is_enforced_locally_without_rejected_wire_constraint():
    route = respx.post(ENDPOINT).mock(
        return_value=httpx.Response(
            200,
            json=response(
                json.dumps(
                    {
                        "facts": [fact("elevator", False)] * 61,
                    }
                )
            ),
        )
    )
    classifier = GeminiAccessibilityClassifier("test-key")
    try:
        with pytest.raises(RuntimeError, match="invalid accessibility JSON"):
            await classifier.classify(PLACE, [SourceDocument(SOURCE, "Brak windy.")])
    finally:
        await classifier.aclose()
    config = json.loads(route.calls[0].request.content)["generationConfig"]
    assert config["responseFormat"]["text"]["mimeType"] == "APPLICATION_JSON"
    assert "maxItems" not in config["responseFormat"]["text"]["schema"]["properties"]["facts"]


@respx.mock
async def test_unavailable_model_switches_once_and_records_actual_model():
    old = respx.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent"
    ).mock(
        return_value=httpx.Response(
            404,
            json={
                "error": {
                    "status": "NOT_FOUND",
                    "message": "Model is no longer available to new users",
                },
            },
        )
    )
    replacement = respx.post(ENDPOINT).mock(
        return_value=httpx.Response(
            200,
            json=response(json.dumps({"facts": [fact("elevator", False)]})),
        )
    )
    classifier = GeminiAccessibilityClassifier("test-key", model=" models/gemini-2.5-flash-lite ")
    try:
        first = await classifier.classify(PLACE, [SourceDocument(SOURCE, "Brak windy.")])
        second = await classifier.classify(PLACE, [SourceDocument(SOURCE, "Brak windy.")])
    finally:
        await classifier.aclose()
    assert first[0].raw_data["model"] == "gemini-3.5-flash-lite"
    assert second[0].value is False
    assert old.call_count == 1
    assert replacement.call_count == 2
    assert old.calls[0].request.content == replacement.calls[0].request.content


@pytest.mark.parametrize("status", [400, 403, 429])
@respx.mock
async def test_does_not_switch_model_for_parameter_permission_or_quota_errors(status):
    old = respx.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent"
    ).mock(return_value=httpx.Response(status, json={"error": {"message": "Upstream failure"}}))
    replacement = respx.post(ENDPOINT).mock(
        return_value=httpx.Response(200, json=response("unused"))
    )
    classifier = GeminiAccessibilityClassifier("test-key", model="gemini-2.5-flash-lite")
    try:
        with pytest.raises(RuntimeError, match=f"HTTP {status}"):
            await classifier.classify(PLACE, [SourceDocument(SOURCE, "Brak windy.")])
    finally:
        await classifier.aclose()
    assert old.call_count == 1
    assert replacement.call_count == 0


@respx.mock
async def test_fallback_can_be_disabled():
    route = respx.post(ENDPOINT).mock(
        return_value=httpx.Response(
            404,
            json={
                "error": {"status": "NOT_FOUND", "message": "Model unavailable"},
            },
        )
    )
    classifier = GeminiAccessibilityClassifier("test-key", fallback_model=None)
    try:
        with pytest.raises(RuntimeError, match="HTTP 404"):
            await classifier.classify(PLACE, [SourceDocument(SOURCE, "Brak windy.")])
    finally:
        await classifier.aclose()
    assert route.call_count == 1


@respx.mock
async def test_failed_fallback_is_not_repeated_indefinitely():
    old = respx.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent"
    ).mock(return_value=httpx.Response(404))
    replacement = respx.post(ENDPOINT).mock(
        return_value=httpx.Response(
            404,
            json={
                "error": {"status": "NOT_FOUND", "message": "Replacement unavailable"},
            },
        )
    )
    classifier = GeminiAccessibilityClassifier("test-key", model="gemini-2.5-flash-lite")
    try:
        with pytest.raises(RuntimeError, match="Replacement unavailable"):
            await classifier.classify(PLACE, [SourceDocument(SOURCE, "Brak windy.")])
    finally:
        await classifier.aclose()
    assert old.call_count == 1
    assert replacement.call_count == 1
