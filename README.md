# RouteAble

> Kraków bez barier — accessibility facts with sources, confidence and conflicts.

RouteAble nie mówi, że miejsce jest „dostępne” albo „niedostępne”. Pokazuje konkretne
bariery i udogodnienia, a przy każdej informacji: źródło, datę sprawdzenia, poziom
wiarygodności i ewentualne sprzeczności między źródłami.

Trzy zasady, na których opiera się cały system:

```text
fakty zamiast etykiet
unknown != accessible
konflikty muszą być widoczne
```

## Stack

| Warstwa | Technologia |
| --- | --- |
| Backend (API, MCP, providery, silnik) | **Python 3.12**, FastAPI, Pydantic v2, httpx, psycopg 3 |
| Frontend | **TypeScript**, Next.js 15 (App Router), Tailwind CSS |
| Baza danych | Zewnętrzny PostgreSQL 18 |
| Zarządzanie zależnościami | `uv` (workspace Pythona), `npm` (workspace frontendu) |

## Struktura repozytorium

```text
RouteAble/
├── apps/
│   ├── api/                          # FastAPI — REST API (Python)
│   ├── mcp/                          # MCP server dla agentów AI (Python)
│   └── web/                          # Next.js + TypeScript
├── packages/
│   ├── accessibility-model/          # routeable_model — wspólny model danych
│   ├── accessibility-engine/         # routeable_engine — normalizacja, konflikty, confidence
│   ├── provider-core/                # routeable_provider_core — kontrakt providera + rejestr
│   ├── provider-osm/                 # routeable_provider_osm — OpenStreetMap
│   ├── provider-krakow-open-data/    # routeable_provider_krakow — dane miejskie
│   ├── provider-websites/            # routeable_provider_websites — oficjalne strony (allowlist)
│   └── database/                     # routeable_database — schemat, migracje, repozytoria
├── docs/
│   ├── ARCHITECTURE.md
│   └── MVP_PLAN.md
├── docker-compose.yml
├── pyproject.toml                    # workspace uv (backend)
├── package.json                      # workspace npm (frontend)
└── Makefile
```

Każdy pakiet Pythona ma układ `src/<moduł>` i jest instalowany jako osobna dystrybucja
w workspace `uv`, dzięki czemu zależności między warstwami są jawne.

## Szybki start

Wymagania: Python 3.12+, [uv](https://docs.astral.sh/uv/), Node.js 20+.

```bash
cp .env.example .env

uv sync        # backend (wszystkie pakiety Pythona)
npm install    # frontend
```

Bez `DATABASE_URL` API startuje na magazynie w pamięci — wystarczy do dema.

```bash
# terminal 1 — API      http://localhost:3001/docs
uv run routeable-api

# terminal 2 — frontend http://localhost:3000
npm run dev

# opcjonalnie — serwer MCP (stdio)
uv run routeable-mcp
```

Z własną bazą PostgreSQL 18: ustaw w `.env` adres istniejącej bazy
(login i hasło użytkownika PostgreSQL, nazwa bazy):

```env
DATABASE_URL=postgresql://LOGIN:HASLO@34.158.225.184:5432/NAZWA_BAZY
```

Znaki specjalne w loginie i haśle zakoduj jako URL, np. `@` → `%40`.
Jeśli serwer wymaga TLS, dodaj do adresu `?sslmode=require`.
Plik `.env` jest ignorowany przez Git.

Migracje przy lokalnym uruchamianiu bez kontenerów:

```bash
uv run --env-file .env routeable-migrate
```

Jeśli sieć używa firmowego CA i build kontenerów kończy się błędem
`invalid peer certificate: UnknownIssuer`, wyeksportuj z Windows zaufany
certyfikat główny jako Base-64 X.509 (PEM) poza repozytorium. Następnie
w PowerShell uruchom:

```powershell
$env:ROUTEABLE_CA_CERT = "C:\certs\company-root.crt"
docker compose -f docker-compose.yml -f docker-compose.ca.yml up --build
```

Przekaż certyfikat CA, nie klucz prywatny. Build korzysta z niego do weryfikacji
TLS; obrazów nie należy budować z wyłączoną weryfikacją certyfikatów.

Całość w kontenerach (Compose automatycznie odczytuje `.env`):

```bash
docker compose up --build -d
docker compose logs -f api
```

Compose nie uruchamia lokalnego PostgreSQL. API i MCP korzystają z tego samego
`DATABASE_URL`. Kontener API przy każdym starcie wykonuje `routeable-migrate`,
a dopiero po powodzeniu uruchamia serwer. MCP czeka na gotowość API.
Migracje wykonują się przy starcie kontenera, nie podczas budowania obrazu.
Użytkownik bazy musi mieć uprawnienia do tworzenia tabel i indeksów w docelowym schemacie.
Obecna migracja używa `CREATE TABLE/INDEX IF NOT EXISTS`, więc może być ponawiana.

## Polecenia

```bash
make install     # uv sync + npm install
make test        # pytest
make lint        # ruff
make typecheck   # mypy + tsc
make up / down   # docker compose
```

## REST API

```http
GET  /health
GET  /api/places/search?q=muzeum&city=Kraków&limit=10
GET  /api/places/{place_id}
GET  /api/places/{place_id}/accessibility?step_free_required=true&elevator_required=true
GET  /api/places/{place_id}/accessibility/evidence?feature=elevator
POST /api/reports
GET  /api/reports?place_id=osm:node:123456
```

Dokumentacja OpenAPI: `http://localhost:3001/docs`.

`place_id` ma postać `<provider>:<external_id>`, np. `osm:node:123456`
albo `krakow:mnk-gmach-glowny`.

## MCP

Serwer MCP udostępnia tę samą warstwę danych agentom AI:

```text
search_places
get_place_accessibility
get_accessibility_evidence
report_accessibility_issue
```

MCP nie ma własnej logiki biznesowej — korzysta z tego samego `AccessibilityService`,
co REST API.

## Źródła danych

| Provider | Typ źródła | Status |
| --- | --- | --- |
| `osm` | OpenStreetMap (Nominatim + Overpass) | na żywo |
| `krakow` | Otwarte Dane Miasta Krakowa | snapshot demonstracyjny |
| `website` | Oficjalne strony obiektów | tylko domeny z allowlisty |
| `google_search` | Wyszukiwanie Google przez Gemini | informacje o dostępności każdego miejsca, ze źródłami |

Website Provider nigdy nie pobiera adresu podanego przez użytkownika — URL powstaje
wyłącznie z konfiguracji allowlisty (ochrona przed SSRF).

### Klasyfikacja AI i wyszukiwanie Google

Ustaw `GEMINI_API_KEY` w `.env` (klucz z Google AI Studio). `GEMINI_MODEL` wybiera
model; domyślnie `gemini-3.5-flash-lite`. `GEMINI_TIMEOUT_S=60` określa timeout pojedynczego
wywołania modelu, a `GEMINI_MAX_INPUT_CHARS=60000` ogranicza tekst do klasyfikacji.
Compose przekazuje te ustawienia do API i MCP. Klucz pozostaje po stronie backendu.

Jeżeli wybrany model odpowiada `404`, API przechodzi na `GEMINI_FALLBACK_MODEL`
(domyślnie `gemini-3.5-flash-lite`) i zapamiętuje zmianę do restartu procesu.
Pusta wartość `GEMINI_FALLBACK_MODEL=` wyłącza to zachowanie. Nazwę modelu można
podać jako `gemini-3.5-flash-lite` albo `models/gemini-3.5-flash-lite`.
Przy błędach `400`, `403` i `429` API zachowuje błąd Google i nie zmienia modelu.
Dowody zawierają nazwę modelu rzeczywiście użytego do klasyfikacji i wyszukiwania.

Gemini klasyfikuje surowe tagi OSM i tekst deklaracji dostępności. Nie ma reguł
regex ani sztywnego mapowania tagów na fakty o dostępności. Miejski snapshot zawiera
już ustrukturyzowane fakty i jest odczytywany bez ponownej klasyfikacji.

Niezależny provider `google_search` bada każde miejsce według nazwy, adresu i
współrzędnych, również gdy OSM nie zawiera informacji o dostępności. Najpierw
Gemini używa narzędzia Google Search; następne wywołanie klasyfikuje wyłącznie
fragmenty powiązane ze źródłami przez `groundingSupports`. Rozdzielenie tych etapów
umożliwia użycie modeli obsługujących wyszukiwanie i JSON w osobnych wywołaniach.
W dowodach zapisujemy URL, fragment wspierający fakt, nazwę modelu oraz metadane
groundingu (w tym `searchEntryPoint` do prezentacji sugestii Google przez klienta).
Fakty AI mają status `automatically_extracted`, nie `verified`.

Brak informacji pozostaje `unknown`, a sprzeczne obserwacje trafiają do silnika
konfliktów. Niepoprawne wartości, wymyślone URL-e i cytaty nieobecne w dokumencie
są odrzucane. Brak klucza, błąd modelu lub odpowiedź bez wykonanego Google Search
pojawiają się jako `failed` w `provider_status`; nie ma powrotu do regexów.
Wyniki są buforowane według `PROVIDER_CACHE_TTL_HOURS` (domyślnie 24 godziny).
Wcześniej zebrane dane OSM/WWW mogą pozostać w cache do jego wygaśnięcia.

Dokumentacja integracji: [Google Search grounding](https://ai.google.dev/gemini-api/docs/generate-content/google-search)
i [structured outputs](https://ai.google.dev/gemini-api/docs/generate-content/structured-output).

## Dokumentacja

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — architektura techniczna
- [docs/MVP_PLAN.md](docs/MVP_PLAN.md) — zakres i scenariusze MVP
