# RouteAble — Technical Architecture

## 1. Cel dokumentu

Ten dokument opisuje proponowaną architekturę techniczną MVP aplikacji **RouteAble**
(„Kraków bez barier”).

Stack:

```text
backend   Python 3.12 — FastAPI, Pydantic v2, httpx, psycopg 3
frontend  TypeScript — Next.js, React, Tailwind CSS
baza      PostgreSQL
```

System ma agregować informacje o dostępności miejsc z wielu źródeł, normalizować je do wspólnego modelu, wykrywać konflikty, oceniać wiarygodność danych i udostępniać je:

- aplikacji webowej,
- agentom AI,
- systemom hotelowym,
- systemom rezerwacyjnym,
- innym aplikacjom poprzez API / MCP.

Główna zasada architektoniczna:

```text
Data acquisition != Data presentation
```

Pozyskiwanie danych musi być oddzielone od sposobu ich prezentowania użytkownikowi.

---

# 2. High-level architecture

```text
                              ┌─────────────────────┐
                              │       Web App       │
                              │   Next.js / React   │
                              └──────────┬──────────┘
                                         │
                                         │ HTTP
                                         ▼
                              ┌─────────────────────┐
                              │     Backend API     │
                              │                     │
                              │ Search / Places /   │
                              │ Accessibility       │
                              └──────────┬──────────┘
                                         │
                        ┌────────────────┼────────────────┐
                        │                │                │
                        ▼                ▼                ▼
                ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
                │ MCP Server   │ │ Place Service│ │ Report       │
                │              │ │              │ │ Service      │
                └──────┬───────┘ └──────┬───────┘ └──────────────┘
                       │                │
                       └────────┬───────┘
                                │
                                ▼
                 ┌─────────────────────────────┐
                 │ Accessibility Data Service  │
                 │                             │
                 │ aggregation                 │
                 │ normalization               │
                 │ conflict detection          │
                 │ confidence calculation      │
                 └─────────────┬───────────────┘
                               │
             ┌─────────────────┼──────────────────┐
             │                 │                  │
             ▼                 ▼                  ▼
      ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
      │ OSM Provider │  │ Kraków Open  │  │ Website      │
      │              │  │ Data Provider│  │ Provider     │
      └──────────────┘  └──────────────┘  └──────────────┘
             │                 │                  │
             └─────────────────┼──────────────────┘
                               │
                               ▼
                    ┌────────────────────┐
                    │ Normalized Storage │
                    │                    │
                    │ PostgreSQL         │
                    │ + PostGIS optional │
                    └────────────────────┘
```

---

# 3. Główne komponenty

## 3.1 Web App

Frontend odpowiada wyłącznie za:

- wyszukiwanie miejsc,
- wybór preferencji użytkownika,
- prezentowanie wyników,
- prezentowanie barier i udogodnień,
- prezentowanie źródeł,
- prezentowanie poziomu wiarygodności,
- prezentowanie brakujących lub sprzecznych danych.

Frontend nie powinien implementować własnej logiki określającej dostępność.

Przykładowy stack:

```text
Next.js
React
TypeScript
Tailwind CSS
MapLibre / Leaflet
```

Mapa powinna być elementem pomocniczym.

Każda informacja widoczna na mapie musi posiadać alternatywę tekstową.

---

# 4. Backend API

Backend odpowiada za komunikację pomiędzy frontendem a warstwą danych.

Przykładowe endpointy:

```http
GET /api/places/search
GET /api/places/:placeId
GET /api/places/:placeId/accessibility
GET /api/places/:placeId/accessibility/evidence

POST /api/reports
```

---

## 4.1 Search places

```http
GET /api/places/search?q=museum&city=krakow
```

Przykładowa odpowiedź:

```json
{
  "results": [
    {
      "id": "osm:node:123456",
      "name": "Example Museum",
      "category": "museum",
      "location": {
        "lat": 50.0614,
        "lng": 19.9366
      }
    }
  ]
}
```

---

## 4.2 Accessibility endpoint

```http
GET /api/places/osm:node:123456/accessibility
```

Przykład odpowiedzi:

```json
{
  "place_id": "osm:node:123456",
  "features": {
    "step_free_entrance": {
      "value": true,
      "status": "confirmed",
      "confidence": "high"
    },
    "elevator": {
      "value": true,
      "status": "confirmed",
      "confidence": "medium"
    },
    "accessible_toilet": {
      "value": null,
      "status": "unknown",
      "confidence": null
    },
    "surface": {
      "value": "cobblestone",
      "status": "confirmed",
      "confidence": "medium"
    }
  }
}
```

---

# 5. MCP Server

MCP Server stanowi dodatkowy interfejs do Accessibility Data Layer.

Pozwala agentom AI korzystać z danych bez znajomości wewnętrznej architektury systemu.

```text
AI Agent
   │
   │ MCP
   ▼
MCP Server
   │
   ▼
Accessibility Data Service
```

MCP nie powinien posiadać własnej kopii logiki biznesowej.

Logika powinna znajdować się w:

```text
Accessibility Data Service
```

Dzięki temu:

```text
Web App
REST API
MCP
```

korzystają z tej samej logiki.

---

# 6. MCP tools

Minimalny zakres MVP:

```text
search_places
get_place_accessibility
get_accessibility_evidence
```

Opcjonalnie:

```text
report_accessibility_issue
```

---

# 7. MCP Tool — `search_places`

## Input

```json
{
  "query": "museum",
  "location": {
    "city": "Kraków"
  },
  "limit": 10
}
```

## Output

```json
{
  "places": [
    {
      "id": "osm:node:123456",
      "name": "Example Museum",
      "category": "museum",
      "address": "Example Street 1, Kraków",
      "location": {
        "lat": 50.0614,
        "lng": 19.9366
      }
    }
  ]
}
```

---

# 8. MCP Tool — `get_place_accessibility`

## Input

```json
{
  "place_id": "osm:node:123456",
  "preferences": {
    "step_free_entrance": true,
    "elevator": true,
    "accessible_toilet": true,
    "min_door_width_cm": 80
  }
}
```

Preferencje nie powinny oznaczać, że system automatycznie klasyfikuje obiekt jako dostępny lub niedostępny.

Służą do:

- wyróżnienia istotnych cech,
- uporządkowania odpowiedzi,
- wskazania potencjalnych barier.

---

## Output

```json
{
  "place": {
    "id": "osm:node:123456",
    "name": "Example Museum"
  },
  "accessibility": {
    "entrance": {
      "step_free": {
        "value": true,
        "status": "confirmed",
        "confidence": "high"
      },
      "steps": {
        "value": 0,
        "status": "confirmed",
        "confidence": "high"
      },
      "ramp": {
        "value": true,
        "status": "confirmed",
        "confidence": "medium"
      },
      "door_width_cm": {
        "value": null,
        "status": "unknown",
        "confidence": null
      }
    },
    "interior": {
      "elevator": {
        "value": true,
        "status": "confirmed",
        "confidence": "high"
      }
    },
    "facilities": {
      "accessible_toilet": {
        "value": true,
        "status": "confirmed",
        "confidence": "medium"
      }
    },
    "surroundings": {
      "surface": {
        "value": "cobblestone",
        "status": "confirmed",
        "confidence": "medium"
      }
    }
  }
}
```

---

# 9. MCP Tool — `get_accessibility_evidence`

Tool zwraca surowe dowody stojące za konkretnymi informacjami.

## Input

```json
{
  "place_id": "osm:node:123456",
  "feature": "elevator"
}
```

## Output

```json
{
  "feature": "elevator",
  "evidence": [
    {
      "source": {
        "type": "official_website",
        "name": "Example Museum",
        "url": "https://example.com/accessibility"
      },
      "value": true,
      "retrieved_at": "2026-10-03T10:00:00Z",
      "confidence": "high"
    },
    {
      "source": {
        "type": "openstreetmap",
        "id": "node:123456"
      },
      "value": true,
      "retrieved_at": "2026-10-03T10:05:00Z",
      "confidence": "medium"
    }
  ]
}
```

---

# 10. MCP Tool — `report_accessibility_issue`

Opcjonalny tool MVP.

Pozwala zgłosić:

- nieaktualne dane,
- brakującą informację,
- błędną informację,
- konflikt danych.

## Input

```json
{
  "place_id": "osm:node:123456",
  "feature": "elevator",
  "issue_type": "incorrect_information",
  "message": "Elevator was unavailable during my visit."
}
```

---

# 11. Normalized Accessibility Model

Najważniejszą częścią systemu powinien być wspólny model danych.

Wszystkie providery mapują swoje dane do tego modelu.

---

## 11.1 Place

```python
class PlaceCategory(StrEnum):
    MUSEUM = "museum"
    HOTEL = "hotel"
    RESTAURANT = "restaurant"
    ATTRACTION = "attraction"
    EVENT_VENUE = "event_venue"
    OTHER = "other"


class GeoLocation(BaseModel):
    lat: float
    lng: float


class ExternalIds(BaseModel):
    osm: str | None = None
    city_dataset: str | None = None
    website: str | None = None


class Place(BaseModel):
    id: str
    name: str
    category: PlaceCategory = PlaceCategory.OTHER
    address: str | None = None
    location: GeoLocation
    external_ids: ExternalIds = Field(default_factory=ExternalIds)
```

---

# 12. Accessibility feature

Każda pojedyncza informacja powinna być osobnym obiektem.

```python
T = TypeVar("T")


class AccessibilityFeature(BaseModel, Generic[T]):
    key: FeatureKey
    value: T | None = None
    status: FeatureStatus = FeatureStatus.UNKNOWN
    confidence: ConfidenceLevel | None = None
    evidence: list[Evidence] = Field(default_factory=list)
    conflict_reason: str | None = None
```

---

# 13. Evidence

```python
class VerificationStatus(StrEnum):
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    SELF_REPORTED = "self_reported"
    AUTOMATICALLY_EXTRACTED = "automatically_extracted"


class Evidence(BaseModel):
    id: str
    place_id: str
    feature_key: FeatureKey
    source: DataSource
    value: Any = None
    retrieved_at: datetime
    observed_at: datetime | None = None
    verification_status: VerificationStatus
    raw_data: Any | None = None
```

---

# 14. Data Source

```python
class SourceType(StrEnum):
    OPENSTREETMAP = "openstreetmap"
    CITY_OPEN_DATA = "city_open_data"
    OFFICIAL_WEBSITE = "official_website"
    USER_REPORT = "user_report"
    PARTNER_API = "partner_api"
    DEMO_DATA = "demo_data"


class DataSource(BaseModel):
    id: str
    type: SourceType
    name: str
    url: str | None = None
    license: str | None = None
```

---

# 15. Accessibility profile

```python
class EntranceFeatures(BaseModel):
    step_free: AccessibilityFeature[bool]
    steps: AccessibilityFeature[int]
    ramp: AccessibilityFeature[bool]
    threshold_cm: AccessibilityFeature[float]
    door_width_cm: AccessibilityFeature[float]


class InteriorFeatures(BaseModel):
    elevator: AccessibilityFeature[bool]
    stairs: AccessibilityFeature[bool]


class FacilityFeatures(BaseModel):
    accessible_toilet: AccessibilityFeature[bool]
    seating: AccessibilityFeature[bool]


class SurroundingFeatures(BaseModel):
    surface: AccessibilityFeature[SurfaceValue]
    curb: AccessibilityFeature[bool]
    accessible_parking: AccessibilityFeature[bool]


class AccessibilityProfile(BaseModel):
    place_id: str
    entrance: EntranceFeatures
    interior: InteriorFeatures
    facilities: FacilityFeatures
    surroundings: SurroundingFeatures
    metadata: ProfileMetadata = Field(default_factory=ProfileMetadata)
```

`SurfaceValue` jest osobnym enumem:

```python
class SurfaceValue(StrEnum):
    ASPHALT = "asphalt"
    CONCRETE = "concrete"
    PAVING_STONES = "paving_stones"
    COBBLESTONE = "cobblestone"
    GRAVEL = "gravel"
    UNPAVED = "unpaved"
    UNKNOWN = "unknown"
```

---

# 16. Status danych

System powinien mieć cztery podstawowe statusy.

```python
class FeatureStatus(StrEnum):
    CONFIRMED = "confirmed"
    UNKNOWN = "unknown"
    CONFLICTING = "conflicting"
    STALE = "stale"
```

### `confirmed`

Co najmniej jedno źródło zawiera informację i nie wykryto konfliktu.

### `unknown`

Nie posiadamy informacji.

### `conflicting`

Dwa lub więcej źródeł podają sprzeczne informacje.

### `stale`

Posiadamy informację, ale nie była aktualizowana przez określony czas.

---

# 17. Confidence model

Na MVP nie potrzebujemy ML ani skomplikowanego scoringu.

Wystarczy deterministyczny system reguł.

```text
HIGH
MEDIUM
LOW
```

---

## 17.1 Przykładowe bazowe wartości źródeł

```python
SOURCE_CONFIDENCE: dict[SourceType, float] = {
    SourceType.CITY_OPEN_DATA: 0.9,
    SourceType.OFFICIAL_WEBSITE: 0.9,
    SourceType.PARTNER_API: 0.9,
    SourceType.OPENSTREETMAP: 0.7,
    SourceType.USER_REPORT: 0.4,
    SourceType.DEMO_DATA: 0.3,
}
```

Nie powinny być traktowane jako uniwersalne wartości produkcyjne.

Na etapie MVP służą jedynie do demonstracji mechanizmu.

---

## 17.2 Freshness modifier

Przykład:

```text
< 30 dni       → 1.0
30–90 dni      → 0.9
90–365 dni     → 0.75
> 365 dni      → 0.5
```

---

## 17.3 Multiple-source modifier

Jeżeli kilka niezależnych źródeł potwierdza tę samą informację:

```text
+ confidence
```

Przykład:

```text
Official website:
elevator = true

OpenStreetMap:
elevator = true
```

Status:

```text
confirmed
```

Confidence:

```text
high
```

---

# 18. Conflict detection

Przykład:

```text
Source A:
step_free = true

Source B:
steps = 3
```

Jeśli nie ma dodatkowej informacji o alternatywnym wejściu, system powinien oznaczyć:

```text
status = conflicting
```

---

## 18.1 Prosty algorytm

```python
def resolve_feature(key: FeatureKey, evidence: list[Evidence]) -> AccessibilityFeature[Any]:
    if not evidence:
        return AccessibilityFeature(key=key, value=None, status=FeatureStatus.UNKNOWN)

    distinct = {json.dumps(item.value, sort_keys=True, default=str): item.value
                for item in evidence}

    if len(distinct) > 1:
        return AccessibilityFeature(
            key=key,
            value=None,
            status=FeatureStatus.CONFLICTING,
            evidence=evidence,
        )

    return AccessibilityFeature(
        key=key,
        value=next(iter(distinct.values())),
        status=FeatureStatus.CONFIRMED,
        evidence=evidence,
    )
```

W produkcji należy uwzględnić bardziej złożone zależności pomiędzy cechami.

---

# 19. Important rule: unknown != accessible

Nigdy nie wykonujemy mapowania:

```text
missing data
    ↓
accessible
```

Poprawne zachowanie:

```text
missing data
    ↓
unknown
```

Przykład:

```json
{
  "door_width_cm": {
    "value": null,
    "status": "unknown",
    "confidence": null
  }
}
```

---

# 20. Data Providers

Każde źródło danych powinno implementować wspólny interfejs.

```python
@runtime_checkable
class AccessibilityProvider(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def source(self) -> DataSource: ...

    async def search_places(
        self, query: str, options: SearchOptions | None = None
    ) -> list[ExternalPlace]: ...

    async def get_place(self, external_id: str) -> ExternalPlace | None: ...

    async def get_accessibility_data(
        self, place: ExternalPlace
    ) -> list[RawAccessibilityEvidence]: ...

    async def aclose(self) -> None: ...
```

---

# 21. Provider architecture

```text
AccessibilityDataService
          │
          │
    ProviderRegistry
          │
    ┌─────┼──────────────┐
    │     │              │
    ▼     ▼              ▼
   OSM   Kraków        Website
Provider Provider      Provider
```

---

# 22. Provider Registry

```python
class ProviderRegistry:
    def __init__(self, providers: list[AccessibilityProvider] | None = None) -> None:
        self._by_name = {provider.name: provider for provider in providers or []}

    def get(self, name: str) -> AccessibilityProvider | None:
        return self._by_name.get(name)

    def get_providers(self) -> list[AccessibilityProvider]:
        return list(self._by_name.values())
```

Dzięki temu można dodać nowe źródło bez zmiany logiki agregacji.

---

# 23. OpenStreetMap Provider

Pierwszym providerem powinien być OpenStreetMap.

Przykładowe tagi istotne dla projektu:

```text
wheelchair
wheelchair:description

entrance
entrance:step_count

step_count

ramp
ramp:wheelchair

door
width

highway
surface

toilets
toilets:wheelchair

elevator
```

Nie należy zakładać, że wszystkie obiekty posiadają kompletne tagi.

---

# 24. OSM normalization

Przykład:

```text
OSM

wheelchair=yes
toilets:wheelchair=yes
```

Normalizacja:

```json
{
  "accessibleToilet": {
    "value": true
  }
}
```

---

# 25. Website Provider

Website Provider odpowiada za informacje publikowane na oficjalnych stronach obiektów.

Przykładowy pipeline:

```text
Official website
       │
       ▼
HTML fetch
       │
       ▼
Relevant content extraction
       │
       ▼
Accessibility information extraction
       │
       ▼
Structured evidence
```

---

# 26. Website extraction

Przykład tekstu:

```text
Wejście do muzeum od strony ulicy X jest bezstopniowe.

W budynku znajduje się winda.

Toaleta dostosowana dla osób poruszających się
na wózkach znajduje się na parterze.
```

Wynik:

```json
[
  {
    "feature": "step_free_entrance",
    "value": true
  },
  {
    "feature": "elevator",
    "value": true
  },
  {
    "feature": "accessible_toilet",
    "value": true
  }
]
```

Każda wartość musi zachować referencję do źródła.

---

# 27. Scraping rules

Scraping nie powinien działać jako:

```text
crawl everything
```

Lepszy model:

```text
allowlisted providers
```

Przykład konfiguracji:

```yaml
providers:
  - domain: muzeum-example.pl

    allowed: true

    refresh_interval: 24h

    accessibility_pages:
      - /accessibility
      - /dla-osob-z-niepelnosprawnosciami
```

Dla każdego źródła należy przechowywać:

```text
source
license / terms
retrieval method
last retrieval
refresh interval
```

---

# 28. Data ingestion flow

```text
Provider
   │
   ▼
Raw data
   │
   ▼
Raw Evidence
   │
   ▼
Normalization
   │
   ▼
Evidence Store
   │
   ▼
Feature Resolver
   │
   ▼
Conflict Detection
   │
   ▼
Confidence Engine
   │
   ▼
Accessibility Profile
```

---

# 29. Suggested database

Na MVP:

```text
PostgreSQL
```

Dostęp z Pythona przez `psycopg` 3 (sterownik async) — patrz `packages/database`.

Opcjonalnie:

```text
PostGIS
```

jeżeli chcemy wykonywać zapytania przestrzenne.

---

# 30. Database tables

Minimalny schemat:

```text
places
sources
evidence
accessibility_features
provider_syncs
user_reports
```

---

# 31. `places`

```sql
CREATE TABLE places (
    id UUID PRIMARY KEY,

    name TEXT NOT NULL,

    category TEXT,

    address TEXT,

    latitude DOUBLE PRECISION,

    longitude DOUBLE PRECISION,

    created_at TIMESTAMP NOT NULL,

    updated_at TIMESTAMP NOT NULL
);
```

---

# 32. `sources`

```sql
CREATE TABLE sources (
    id UUID PRIMARY KEY,

    type TEXT NOT NULL,

    name TEXT NOT NULL,

    url TEXT,

    license TEXT,

    provider TEXT,

    created_at TIMESTAMP NOT NULL
);
```

---

# 33. `evidence`

```sql
CREATE TABLE evidence (
    id UUID PRIMARY KEY,

    place_id UUID NOT NULL,

    source_id UUID NOT NULL,

    feature_key TEXT NOT NULL,

    value JSONB,

    verification_status TEXT,

    retrieved_at TIMESTAMP NOT NULL,

    observed_at TIMESTAMP,

    raw_data JSONB,

    FOREIGN KEY (place_id)
        REFERENCES places(id),

    FOREIGN KEY (source_id)
        REFERENCES sources(id)
);
```

---

# 34. `accessibility_features`

Tabela może przechowywać zmaterializowany aktualny stan.

```sql
CREATE TABLE accessibility_features (
    id UUID PRIMARY KEY,

    place_id UUID NOT NULL,

    feature_key TEXT NOT NULL,

    value JSONB,

    status TEXT NOT NULL,

    confidence TEXT,

    calculated_at TIMESTAMP NOT NULL,

    FOREIGN KEY (place_id)
        REFERENCES places(id)
);
```

`evidence` jest źródłem prawdy.

`accessibility_features` jest wynikiem agregacji.

---

# 35. Data provenance

Każdy feature powinien umożliwiać przejście:

```text
feature
   ↓
evidence
   ↓
source
   ↓
original URL / dataset
```

Przykład:

```text
Elevator: TRUE

↓ evidence

official website
retrieved: 2026-10-03

↓ source

https://example.com/accessibility
```

---

# 36. Place identity resolution

Ten sam obiekt może istnieć w kilku źródłach.

Przykład:

```text
OpenStreetMap:
node/123

City Open Data:
object_id=ABC

Official website:
museum.example.com
```

System musi wiedzieć, że jest to ten sam obiekt.

---

## MVP approach

Na hackathon wystarczy:

```text
manual mapping
+
basic matching
```

Możliwe kryteria:

```text
normalized name
+
distance < X meters
+
address similarity
```

Nie trzeba budować pełnego entity resolution engine.

---

# 37. Cache

Nie wszystkie zewnętrzne źródła powinny być odpytywane przy każdym requestcie użytkownika.

Proponowany flow:

```text
User request
    │
    ▼
Normalized DB
    │
    ├── fresh → return
    │
    └── stale → schedule/provider refresh
```

Na MVP można zastosować prosty TTL.

Przykład:

```text
OSM               24 h
official website  24 h
city open data    24 h
```

Wartości powinny być konfigurowalne per provider.

---

# 38. Provider sync

```python
class ProviderSync(BaseModel):
    provider: str
    started_at: datetime
    finished_at: datetime | None = None
    status: SyncStatus
    processed_items: int = 0
    error: str | None = None
```

Pozwala pokazać:

```text
last successful sync
```

dla danego źródła.

---

# 39. Provider failure

Brak działania providera nie może powodować błędnej informacji:

```text
source unavailable
    ↓
accessible
```

Poprawny flow:

```text
source unavailable
    ↓
use cached evidence
    ↓
mark freshness
    ↓
potentially stale
```

---

# 40. Search architecture

Na MVP możemy użyć:

```text
OpenStreetMap / Nominatim / existing dataset
```

do wyszukiwania miejsc.

Potencjalny flow:

```text
query
 │
 ▼
Place Search Service
 │
 ├── local database
 │
 └── external provider
 │
 ▼
Place candidates
```

---

# 41. User preferences

Nie przechowujemy informacji:

```text
user_disability = wheelchair
```

jeżeli nie jest to potrzebne.

Przechowujemy preferencje funkcjonalne:

```json
{
  "step_free_required": true,
  "elevator_required": true,
  "min_door_width_cm": 80,
  "accessible_toilet_required": false,
  "avoid_cobblestone": true
}
```

Jest to bardziej prywatne i jednocześnie bardziej użyteczne.

---

# 42. Preference evaluation

System może wskazywać potencjalne problemy.

Przykład:

```text
Preference:

min_door_width = 80 cm

Data:

door_width = 75 cm
```

Wynik:

```json
{
  "feature": "door_width_cm",
  "value": 75,
  "preference": 80,
  "match": false
}
```

Nie powinno to automatycznie oznaczać:

```text
PLACE NOT ACCESSIBLE
```

---

# 43. Accessibility evaluation

Przykładowy model:

```python
class PreferenceResult(StrEnum):
    MEETS_PREFERENCE = "meets_preference"
    DOES_NOT_MEET_PREFERENCE = "does_not_meet_preference"
    UNKNOWN = "unknown"
    NEEDS_VERIFICATION = "needs_verification"


class PreferenceEvaluation(BaseModel):
    key: FeatureKey
    preference: Any = None
    observed_value: Any = None
    result: PreferenceResult
```

---

# 44. Example complete response

```json
{
  "place": {
    "id": "place_123",
    "name": "Example Museum"
  },

  "features": {
    "step_free_entrance": {
      "value": true,
      "status": "confirmed",
      "confidence": "high"
    },

    "elevator": {
      "value": true,
      "status": "confirmed",
      "confidence": "high"
    },

    "door_width_cm": {
      "value": null,
      "status": "unknown",
      "confidence": null
    },

    "surface": {
      "value": "cobblestone",
      "status": "confirmed",
      "confidence": "medium"
    }
  },

  "preference_evaluation": [
    {
      "key": "step_free_entrance",
      "preference": true,
      "observed_value": true,
      "result": "meets_preference"
    },

    {
      "key": "door_width_cm",
      "preference": 80,
      "observed_value": null,
      "result": "unknown"
    }
  ],

  "metadata": {
    "source_count": 3,
    "evidence_count": 11,
    "last_updated": "2026-10-03T11:00:00Z"
  }
}
```

---

# 45. Repository structure

Monorepo polyglot: backend w Pythonie (workspace `uv`), frontend w TypeScripcie
(workspace `npm`).

```text
RouteAble/

├── apps/
│
│   ├── api/                                  # FastAPI — REST API
│   │   ├── src/routeable_api/
│   │   │   ├── routers/
│   │   │   ├── config.py
│   │   │   ├── container.py
│   │   │   ├── dependencies.py
│   │   │   └── main.py
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   │
│   ├── mcp/                                  # MCP server dla agentów AI
│   │   ├── src/routeable_mcp/
│   │   │   ├── server.py
│   │   │   └── __main__.py
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   │
│   └── web/                                  # Next.js + TypeScript
│       ├── src/
│       │   ├── app/
│       │   ├── components/
│       │   └── lib/
│       ├── Dockerfile
│       └── package.json
│
├── packages/
│
│   ├── accessibility-model/                  # routeable_model
│   │   ├── src/routeable_model/
│   │   └── pyproject.toml
│   │
│   ├── accessibility-engine/                 # routeable_engine
│   │   ├── src/routeable_engine/
│   │   ├── tests/
│   │   └── pyproject.toml
│   │
│   ├── provider-core/                        # routeable_provider_core
│   │
│   ├── provider-osm/                         # routeable_provider_osm
│   │
│   ├── provider-krakow-open-data/            # routeable_provider_krakow
│   │
│   ├── provider-websites/                    # routeable_provider_websites
│   │
│   └── database/                             # routeable_database
│       ├── src/routeable_database/
│       │   └── schema/001_init.sql
│       └── pyproject.toml
│
├── docs/
│   ├── MVP_PLAN.md
│   └── ARCHITECTURE.md
│
├── docker-compose.yml
│
├── pyproject.toml                            # workspace uv (backend)
│
├── package.json                              # workspace npm (frontend)
│
├── Makefile
│
└── README.md
```

Każdy pakiet Pythona ma układ `src/<moduł>` i własny `pyproject.toml`, dzięki czemu
zależności między warstwami są jawne i wymuszane przez narzędzia.

---

# 46. Package responsibilities

| Katalog | Moduł Pythona | Odpowiedzialność |
| --- | --- | --- |
| `accessibility-model` | `routeable_model` | wspólne modele Pydantic, enumy, schematy |
| `accessibility-engine` | `routeable_engine` | normalizacja, conflict detection, confidence, preference evaluation, `AccessibilityService` |
| `provider-core` | `routeable_provider_core` | protokół providera, rejestr, klient HTTP, helpery geo |
| `provider-osm` | `routeable_provider_osm` | OpenStreetMap: Nominatim + Overpass, mapowanie tagów |
| `provider-krakow-open-data` | `routeable_provider_krakow` | dane miejskie Krakowa |
| `provider-websites` | `routeable_provider_websites` | pobieranie i ekstrakcja ze stron z allowlisty |
| `database` | `routeable_database` | schemat SQL, migracje, repozytoria psycopg |

---

## `accessibility-model`

Wspólne:

```text
modele Pydantic
enumy
schematy
```

---

## `accessibility-engine`

Logika:

```text
normalization
conflict detection
confidence calculation
preference evaluation
```

---

## `provider-core`

Definicje:

```text
Provider protocol
Provider registry
shared provider utilities
```

---

## `provider-osm`

Integracja:

```text
OpenStreetMap
Overpass
Nominatim
```

---

## `provider-websites`

Odpowiada za:

```text
fetching
parsing
accessibility information extraction
```

dla obsługiwanych źródeł.

---

## `database`

```text
schema
migrations
repositories
```

---

# 47. Example service structure

```text
AccessibilityService

├── search_places()
│
├── get_place_accessibility()
│
├── get_evidence()
│
├── _collect_evidence()
│
├── build_accessibility_profile()
│
├── resolve_feature()
│
├── calculate_confidence()
│
└── evaluate_preferences()
```

---

# 48. Request sequence

Przykład:

```text
User
 │
 │ search "museum"
 ▼
Web App
 │
 ▼
Backend API
 │
 ▼
Place Service
 │
 ▼
Search Provider
 │
 ▼
Places
 │
 ▼
Web App
```

Następnie:

```text
User
 │
 │ opens place
 ▼
Web App
 │
 ▼
Backend API
 │
 ▼
Accessibility Service
 │
 ├─────────► DB
 │
 ├─────────► OSM Provider
 │
 ├─────────► City Provider
 │
 └─────────► Website Provider
 │
 ▼
Evidence
 │
 ▼
Normalize
 │
 ▼
Conflict detection
 │
 ▼
Confidence
 │
 ▼
API response
 │
 ▼
Web App
```

---

# 49. MCP sequence

```text
AI Agent
   │
   │ get_place_accessibility
   ▼
MCP Server
   │
   ▼
Accessibility Service
   │
   ▼
Normalized Accessibility Profile
   │
   ▼
MCP Server
   │
   ▼
AI Agent
```

---

# 50. Security

MVP powinno posiadać przynajmniej:

```text
HTTPS

input validation

rate limiting

request size limits

sanitized external content

timeouts for external requests

provider allowlist
```

Website Provider nie powinien pozwalać użytkownikowi przesłać dowolnego URL do pobrania.

Niebezpieczny model:

```text
scrape_url("http://anything.com")
```

Lepszy:

```text
place_id
    ↓
known source configuration
    ↓
allowed URL
```

Ogranicza to m.in. ryzyko SSRF.

---

# 51. User-generated reports

Jeżeli dodamy zgłoszenia użytkowników:

```text
POST /reports
```

nie powinny automatycznie nadpisywać potwierdzonych danych.

Flow:

```text
User report
     │
     ▼
Unverified evidence
     │
     ▼
moderation / multiple confirmations
     │
     ▼
possible confidence increase
```

---

# 52. Accessibility of frontend

Technicznie należy uwzględnić:

```text
semantic HTML

keyboard navigation

visible focus states

ARIA only where needed

screen-reader labels

sufficient contrast

no color-only status indicators

text equivalent for map information
```

Status:

```text
confirmed
unknown
conflicting
stale
```

powinien być przekazywany tekstem i ikoną, nie wyłącznie kolorem.

---

# 53. Deployment

Na MVP system może działać jako kilka prostych usług.

```text
Frontend
    ↓
Vercel / Cloudflare / similar

Backend + MCP
    ↓
Container hosting

Database
    ↓
Managed PostgreSQL
```

Alternatywnie całość można uruchomić przez Docker Compose.

---

# 54. Local development

Całość w kontenerach:

```text
docker compose up --build
```

Usługi:

```text
web
api
mcp
postgres
```

Lokalnie, bez kontenerów:

```bash
uv sync                 # backend — wszystkie pakiety Pythona
npm install             # frontend

uv run routeable-api    # REST API
uv run routeable-mcp    # MCP server
npm run dev             # Next.js
```

Bez `DATABASE_URL` API startuje na magazynie w pamięci — wystarczy do dema.

Opcjonalnie:

```text
redis
```

jeżeli potrzebny będzie cache lub kolejka.

---

# 55. Environment variables

Przykład:

```env
DATABASE_URL=

NOMINATIM_URL=
OSM_OVERPASS_URL=

API_PORT=3001
WEB_PORT=3000

MCP_TRANSPORT=stdio
FASTMCP_HOST=127.0.0.1
FASTMCP_PORT=3002

ROUTEABLE_API_URL=http://localhost:3001

USER_AGENT=

WEB_PROVIDER_TIMEOUT_MS=5000
PROVIDER_CACHE_TTL_HOURS=24
STALE_AFTER_DAYS=180

CORS_ORIGINS=["http://localhost:3000"]
RATE_LIMIT=120/minute
```

---

# 56. Logging

Każdy request do providera powinien logować:

```text
provider
source
place_id
duration
status
retrieved_at
```

Bez przechowywania niepotrzebnych danych osobowych użytkowników.

---

# 57. Metrics

Przykładowe metryki:

```text
provider_request_count

provider_error_count

provider_response_time

accessibility_query_count

unknown_feature_ratio

conflict_ratio

stale_data_ratio
```

---

# 58. MVP observability

Na hackathon wystarczy prosty panel lub logi pokazujące:

```text
OSM
last sync: OK

Website provider
last sync: OK

Kraków Open Data
last sync: FAILED

cached data used
```

Jest to szczególnie wartościowe podczas prezentowania odporności na niedostępne źródła.

---

# 59. Minimal implementation scope

## Must have

```text
Place Search

OpenStreetMap Provider

1 dodatkowy provider

Normalized Accessibility Model

Evidence model

Source metadata

Conflict detection

Confidence

REST API

MCP Server

Web UI
```

---

## Nice to have

```text
Website Provider

User reports

Map

Preference evaluation

PostGIS

background refresh
```

---

## Out of scope for MVP

```text
advanced routing

full accessibility navigation

mobile app

machine learning scoring

real-time accessibility monitoring

full city coverage

automatic legal verification of scraping rights

complex authentication system
```

---

# 60. Recommended implementation order

## Phase 1

Zdefiniować:

```text
AccessibilityFeature

Evidence

DataSource

AccessibilityProfile
```

---

## Phase 2

Zaimplementować:

```text
OSMProvider
```

---

## Phase 3

Zaimplementować:

```text
AccessibilityService
```

w tym:

```text
normalize

resolve conflicts

confidence
```

---

## Phase 4

Wystawić:

```text
REST API
```

---

## Phase 5

Zbudować:

```text
Web App
```

---

## Phase 6

Dodać:

```text
MCP Server
```

korzystający z tego samego `AccessibilityService`.

---

## Phase 7

Dodać drugi provider:

```text
Kraków Open Data
```

lub:

```text
Official Website Provider
```

---

## Phase 8

Przygotować trzy przypadki demo:

```text
GOOD DATA

MISSING DATA

CONFLICTING DATA
```

---

# 61. Definition of Done — MVP

MVP jest technicznie gotowe, jeśli:

- [ ] można wyszukać miejsce,
- [ ] miejsce posiada wspólny `place_id`,
- [ ] dane są pobierane z minimum dwóch źródeł,
- [ ] dane są mapowane do wspólnego modelu,
- [ ] każda informacja posiada źródło,
- [ ] każda informacja posiada `retrieved_at`,
- [ ] system rozróżnia `unknown`,
- [ ] system wykrywa podstawowy konflikt,
- [ ] system zwraca `confidence`,
- [ ] frontend pokazuje źródła,
- [ ] frontend pokazuje brak danych,
- [ ] frontend pokazuje konflikty,
- [ ] MCP potrafi pobrać accessibility profile,
- [ ] aplikacja działa z klawiatury,
- [ ] dane z mapy posiadają alternatywę tekstową.

---

# 62. Technical demo checklist

Podczas demonstracji warto pokazać również backend.

### Demo 1

```text
get_place_accessibility(place_id)
```

Response:

```text
step_free = true
elevator = true
toilet = true
door_width = unknown
```

---

### Demo 2

Pokazać evidence:

```text
elevator=true

Source 1:
Official website

Source 2:
OpenStreetMap
```

---

### Demo 3

Pokazać konflikt:

```text
OSM:
wheelchair=yes

Website:
3 steps
```

Response:

```text
status=conflicting
```

---

### Demo 4

Pokazać MCP.

Agent:

```text
Czy to muzeum będzie odpowiednie dla osoby,
która potrzebuje wejścia bez schodów?
```

Agent wykonuje:

```text
get_place_accessibility
```

i otrzymuje strukturalne dane wraz z evidence.

---

# 63. Architectural principles

## 1. Facts over labels

Nie przechowujemy tylko:

```text
accessible=true
```

Przechowujemy:

```text
steps=0

ramp=true

door_width=90

elevator=true

toilet=true
```

---

## 2. Evidence first

Każdy fakt musi mieć możliwość wskazania:

```text
where did this come from?
```

---

## 3. Unknown is a valid state

```text
unknown
```

jest poprawną odpowiedzią.

---

## 4. Conflicts must be visible

System nie powinien ukrywać sprzecznych informacji.

---

## 5. Providers are replaceable

Każde źródło jest adapterem.

```text
Provider → normalized model
```

---

## 6. MCP is an interface, not the database

```text
MCP
 ↓
AccessibilityService
 ↓
Data Layer
```

Nie:

```text
MCP
 ↓
scraper
```

---

# 64. Long-term architecture

Docelowo:

```text
                         ┌────────────────────┐
                         │ Accessibility Data │
                         │     Platform       │
                         └─────────┬──────────┘
                                   │
                 ┌─────────────────┼─────────────────┐
                 │                 │                 │
                 ▼                 ▼                 ▼
              REST API          MCP API          GraphQL
                 │                 │                 │
        ┌────────┼────────┐        │                 │
        │        │        │        │                 │
        ▼        ▼        ▼        ▼                 ▼
      Hotels   Booking   City    AI Agents       Partners
               Systems   Apps
```

Warstwa danych może wtedy funkcjonować niezależnie od aplikacji stworzonej na potrzeby hackathonu.

---

# 65. Core technical value proposition

Najważniejszym elementem technicznym projektu nie jest mapa ani scraper.

Jest nim:

```text
Accessibility Data Intelligence Layer
```

która realizuje pipeline:

```text
Multiple data sources
          │
          ▼
      Ingestion
          │
          ▼
     Normalization
          │
          ▼
       Evidence
          │
          ▼
 Conflict Detection
          │
          ▼
 Confidence Engine
          │
          ▼
 Accessibility Profile
          │
     ┌────┴────┐
     │         │
     ▼         ▼
 REST API     MCP
     │         │
     ▼         ▼
 Web App    AI Agents
```

To pozwala rozwijać rozwiązanie zarówno jako aplikację dla użytkowników, jak i jako niezależną platformę danych o dostępności.