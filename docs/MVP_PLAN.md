# Kraków bez barier — MVP Plan

## 1. Cel MVP

Celem MVP jest stworzenie prostej aplikacji webowej, która pozwala użytkownikowi wyszukać miejsce w Krakowie i sprawdzić, czy odpowiada ono jego indywidualnym potrzebom dotyczącym dostępności.

Aplikacja nie ocenia miejsca jednym komunikatem:

> dostępne / niedostępne

Zamiast tego pokazuje konkretne informacje o barierach i udogodnieniach, np.:

- wejście bez schodów,
- liczba stopni,
- dostępność podjazdu,
- szerokość wejścia,
- dostępność windy,
- dostępna toaleta,
- rodzaj nawierzchni,
- miejsca odpoczynku.

Przy każdej informacji użytkownik powinien również widzieć:

- źródło danych,
- datę ostatniego sprawdzenia,
- poziom wiarygodności,
- status weryfikacji.

---

## 2. Grupa docelowa MVP

W pierwszej wersji skupiamy się na dwóch grupach użytkowników:

- osoby poruszające się na wózkach,
- rodzice korzystający z wózków dziecięcych.

Obie grupy mają podobne wymagania dotyczące:

- schodów,
- progów,
- podjazdów,
- wind,
- szerokości wejścia,
- nawierzchni.

Dzięki temu możemy stworzyć użyteczny prototyp bez próby rozwiązania wszystkich problemów związanych z dostępnością jednocześnie.

---

## 3. Główny scenariusz użytkownika

### Krok 1 — określenie potrzeb

Użytkownik określa istotne dla niego wymagania.

Przykład:

> Poruszam się na wózku.

Preferencje:

- brak schodów,
- wymagany podjazd lub wejście bezstopniowe,
- wymagana winda,
- dostępna toaleta,
- szerokość wejścia minimum 80 cm.

---

### Krok 2 — wyszukanie miejsca

Użytkownik wpisuje nazwę miejsca, np.:

```text
Muzeum Narodowe Kraków
```

Alternatywnie może wybrać obiekt z mapy.

---

### Krok 3 — informacje o dostępności

Aplikacja pokazuje kartę obiektu.

Przykład:

```text
Muzeum X

Wejście
✓ wejście bezstopniowe
✓ podjazd
? szerokość wejścia — brak danych

Poruszanie się wewnątrz
✓ winda
✓ brak schodów na głównej trasie

Udogodnienia
✓ dostępna toaleta
? miejsca odpoczynku — brak danych

Otoczenie
⚠ kostka brukowa przed wejściem
```

---

### Krok 4 — źródła informacji

Każda informacja może zostać rozwinięta.

Przykład:

```text
Winda

Status:
potwierdzone

Źródła:
- oficjalna strona obiektu
- OpenStreetMap

Ostatnie sprawdzenie:
2026-10-03

Wiarygodność:
HIGH
```

---

## 4. Główna idea produktu

System nie powinien przechowywać jedynie prostego pola:

```text
wheelchair_accessible = true
```

Zamiast tego przechowuje szczegółowe informacje opisujące rzeczywiste bariery i udogodnienia.

Przykładowy model:

```yaml
entrance:
  steps: 0
  ramp: true
  threshold_cm: 2
  door_width_cm: 90

interior:
  elevator: true
  stairs: false

facilities:
  accessible_toilet: true
  seating: true

surroundings:
  surface: cobblestone
  curb: true
  accessible_parking: false
```

Dzięki temu decyzję o tym, czy miejsce jest odpowiednie, podejmuje użytkownik, a nie aplikacja.

---

## 5. Źródła danych

MVP powinno wykorzystywać kilka niezależnych źródeł danych.

### OpenStreetMap

Możliwe informacje:

- lokalizacja,
- kategoria miejsca,
- `wheelchair`,
- wejścia,
- windy,
- drogi,
- nawierzchnie,
- elementy infrastruktury.

---

### Publiczne dane Krakowa

Potencjalne źródła:

- Portal Otwarte Dane Miasta Krakowa,
- MSIP,
- inne publiczne API i zbiory miejskie.

---

### Oficjalne strony obiektów

Informacje publikowane przez:

- muzea,
- atrakcje,
- hotele,
- restauracje,
- centra kultury,
- organizatorów wydarzeń.

Dane z takich źródeł mogą być pobierane przez dedykowane adaptery, o ile warunki korzystania z danego źródła pozwalają na automatyczne pobieranie i dalsze wykorzystanie danych.

---

### Dane demonstracyjne

Jeżeli dla części obiektów nie uda się znaleźć wystarczających danych, podczas hackathonu można wykorzystać dane przykładowe.

Muszą być jednoznacznie oznaczone jako:

```text
Demo data / dane przykładowe
```

---

## 6. Accessibility Data Layer

Kluczowym elementem systemu jest warstwa agregująca i normalizująca dane z różnych źródeł.

```text
OpenStreetMap ──────────┐
                       │
Kraków Open Data ───────┤
                       │
Official Websites ──────┼──> Accessibility Data Layer
                       │
User Reports ───────────┤
                       │
Other APIs ─────────────┘
```

Każde źródło może posiadać:

- inny format danych,
- inne nazewnictwo,
- inny poziom szczegółowości,
- inną wiarygodność.

Accessibility Data Layer sprowadza dane do jednego wspólnego modelu.

---

## 7. Rola MCP Server

Nad warstwą danych znajduje się MCP Server.

MCP stanowi standardowy interfejs dostępu do informacji o dostępności.

Dzięki temu dane mogą być wykorzystywane nie tylko przez naszą aplikację, ale także przez:

- agentów AI,
- systemy hotelowe,
- AI Concierge,
- systemy rezerwacyjne,
- aplikacje turystyczne,
- zewnętrzne aplikacje miejskie.

---

## 8. Podstawowe MCP tools

### `search_places`

Wyszukiwanie miejsc.

```text
search_places(
    query,
    location
)
```

Przykład:

```text
search_places(
    query="museum",
    location="Kraków"
)
```

---

### `get_accessibility`

Pobiera szczegółowe informacje o dostępności miejsca.

```text
get_accessibility(
    place_id,
    user_preferences
)
```

---

### `get_accessibility_evidence`

Pobiera informacje o źródłach danych.

```text
get_accessibility_evidence(
    place_id
)
```

---

### `report_accessibility_issue`

Pozwala zgłosić błędne lub nieaktualne informacje.

```text
report_accessibility_issue(
    place_id,
    issue
)
```

---

## 9. Model danych

Każda informacja o dostępności powinna posiadać nie tylko wartość, ale również metadane.

Przykład:

```json
{
  "feature": "elevator",
  "value": true,
  "source": {
    "type": "official_website",
    "url": "https://example.com"
  },
  "retrieved_at": "2026-10-03",
  "confidence": "high",
  "verification_status": "confirmed"
}
```

Podstawowy model:

```text
value
source
retrieved_at
confidence
verification_status
```

---

## 10. Poziom wiarygodności danych

Proponujemy trzy podstawowe poziomy:

### HIGH

Informacja pochodzi np. z:

- oficjalnej strony obiektu,
- zweryfikowanego źródła publicznego,
- kilku zgodnych niezależnych źródeł.

### MEDIUM

Informacja pochodzi np. z:

- OpenStreetMap,
- pojedynczego zewnętrznego źródła,
- starszych danych.

### LOW

Informacja pochodzi np. z:

- niezweryfikowanego zgłoszenia użytkownika,
- źródła o nieznanej aktualności,
- automatycznie wywnioskowanych danych.

---

## 11. Obsługa sprzecznych danych

Jest to jeden z kluczowych elementów systemu.

Przykład:

OpenStreetMap:

```text
wheelchair = yes
```

Oficjalna strona:

```text
Do wejścia prowadzą trzy stopnie.
```

System nie powinien arbitralnie wybierać jednej odpowiedzi.

Użytkownik powinien zobaczyć:

```text
⚠ Dane wymagają weryfikacji

Źródło 1
OpenStreetMap
wheelchair=yes

Źródło 2
Oficjalna strona obiektu
Do wejścia prowadzą trzy stopnie.

Status:
CONFLICTING_INFORMATION
```

Aplikacja nie przedstawia wtedy obiektu jako jednoznacznie dostępnego.

---

## 12. Obsługa braku danych

Brak informacji nie może oznaczać dostępności.

System powinien rozróżniać:

```text
✓ potwierdzone udogodnienie

✕ potwierdzona bariera

? brak danych

⚠ dane sprzeczne

◷ dane potencjalnie nieaktualne
```

Przykład:

```text
Wejście bez schodów:
✓ potwierdzone

Winda:
✓ potwierdzone

Toaleta:
? brak danych

Szerokość wejścia:
? brak danych
```

---

## 13. Frontend MVP

Frontend może składać się z trzech głównych ekranów.

---

### Ekran 1 — Search

Główne pole:

```text
Gdzie chcesz się dostać?
```

Dodatkowo użytkownik może określić swoje preferencje.

Przykład:

```text
[✓] potrzebuję wejścia bez schodów
[✓] potrzebuję windy
[ ] potrzebuję dostępnej toalety
[ ] wejście minimum 80 cm
```

---

### Ekran 2 — Wyniki

Lista wyników + opcjonalna mapa.

Przykład:

```text
Muzeum X

✓ wejście bez schodów
✓ winda
✓ dostępna toaleta
? szerokość wejścia

3 źródła
ostatnia aktualizacja: 2 dni temu
```

Mapa nie powinna być jedynym sposobem prezentowania informacji.

---

### Ekran 3 — Szczegóły miejsca

Informacje mogą być podzielone na sekcje:

```text
Entrance
Interior
Facilities
Surroundings
Transport
Sources
```

Przykład:

```text
Entrance

✓ Step-free entrance
✓ Ramp
? Door width

Interior

✓ Elevator
✓ Step-free main route

Facilities

✓ Accessible toilet
? Seating

Surroundings

⚠ Cobblestone
```

---

## 14. Dostępność cyfrowa aplikacji

MVP powinno już na etapie prototypu uwzględniać podstawowe wymagania WCAG.

Najważniejsze elementy:

- pełna obsługa klawiaturą,
- poprawna struktura nagłówków HTML,
- odpowiednie `aria-label`,
- odpowiedni kontrast,
- czytelne komunikaty tekstowe,
- niewykorzystywanie samego koloru jako informacji,
- tekstowa alternatywa dla mapy,
- możliwość korzystania z aplikacji bez mapy,
- kompatybilność z czytnikiem ekranu.

Mapa jest dodatkiem.

Najważniejsze informacje muszą być dostępne również w postaci tekstowej.

---

## 15. Zakres MVP

Aby rozwiązanie było realne do wykonania podczas hackathonu, ograniczamy zakres.

### Obszar

```text
Kraków
```

### Liczba obiektów

Docelowo:

```text
30–100 miejsc demonstracyjnych
```

### Kategorie

Na początek:

- muzea,
- atrakcje turystyczne,
- restauracje,
- hotele.

### Grupa użytkowników

- osoby poruszające się na wózkach,
- rodzice z wózkami dziecięcymi.

---

## 16. Czego nie robimy w MVP

Na etapie MVP nie budujemy:

- pełnej bazy wszystkich miejsc w Krakowie,
- pełnej nawigacji turn-by-turn,
- własnego systemu mapowego,
- kompletnego audytu dostępności wszystkich obiektów,
- aplikacji mobilnej,
- rozbudowanego systemu kont użytkowników,
- obsługi wszystkich rodzajów niepełnosprawności,
- zaawansowanego systemu społecznościowego,
- automatycznej certyfikacji dostępności.

MVP ma przede wszystkim pokazać, że model:

```text
data acquisition
      ↓
normalization
      ↓
verification
      ↓
presentation
```

działa.

---

## 17. Demo hackathonowe — scenariusz 1

Główny scenariusz:

> Użytkownik porusza się na wózku i chce odwiedzić muzeum w centrum Krakowa.

Użytkownik zaznacza:

```text
✓ brak schodów
✓ winda
✓ dostępna toaleta
```

System wyszukuje miejsca.

Użytkownik wybiera jedno z nich.

Aplikacja pokazuje:

```text
Entrance
✓ step-free
✓ ramp

Inside
✓ elevator

Toilet
✓ accessible

Surface
⚠ cobblestone

Door width
? unknown
```

Następnie użytkownik otwiera:

```text
Sources
```

i widzi:

- OpenStreetMap,
- oficjalną stronę obiektu,
- datę pobrania danych,
- poziom `confidence`.

---

## 18. Demo hackathonowe — scenariusz 2

Drugi scenariusz celowo pokazuje problem ze źródłami.

Przykład:

```text
OpenStreetMap:
wheelchair=yes

Official website:
3 steps at entrance
```

System pokazuje:

```text
⚠ Conflicting information
```

zamiast:

```text
✓ Accessible
```

Użytkownik może zobaczyć oba źródła i samodzielnie podjąć decyzję.

---

## 19. Demo hackathonowe — scenariusz 3

Trzeci przypadek pokazuje brak informacji.

Przykład:

```text
Entrance:
✓ step-free

Elevator:
? unknown

Accessible toilet:
? unknown

Door width:
? unknown
```

System wyraźnie pokazuje, że brak informacji nie jest potwierdzeniem dostępności.

---

## 20. Architektura MVP

```text
                         ┌───────────────┐
                         │    Web App    │
                         └───────┬───────┘
                                 │
                                 ▼
                         ┌───────────────┐
                         │  Backend API  │
                         └───────┬───────┘
                                 │
                                 ▼
                         ┌───────────────┐
                         │  MCP Server   │
                         └───────┬───────┘
                                 │
                                 ▼
                  ┌────────────────────────────┐
                  │ Accessibility Data Layer   │
                  └─────────────┬──────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
        OpenStreetMap     Public Open Data    Websites
              │                 │                 │
              └─────────────────┼─────────────────┘
                                │
                                ▼
                        Normalized Data
                                │
                                ▼
                            Database
```

Najważniejsza zasada:

> Pozyskiwanie danych jest oddzielone od ich prezentowania użytkownikowi.

---

## 21. Przykładowy flow danych

```text
1. User searches for a place
              ↓
2. Backend finds place identifier
              ↓
3. Accessibility Layer checks available sources
              ↓
4. Providers return raw accessibility data
              ↓
5. Data is normalized
              ↓
6. Conflicts are detected
              ↓
7. Confidence is calculated
              ↓
8. MCP / API returns unified response
              ↓
9. Frontend presents facts + sources
```

---

## 22. Adaptery danych

Każde źródło powinno być obsługiwane przez osobny adapter.

Przykład:

```text
providers/

├── osm/
│   └── OSMProvider
│
├── krakow-open-data/
│   └── KrakowOpenDataProvider
│
├── websites/
│   └── WebsiteProvider
│
└── user-reports/
    └── UserReportProvider
```

Każdy adapter zwraca dane w jednym zunifikowanym formacie.

Dzięki temu dodanie nowego źródła nie wymaga przebudowy całej aplikacji.

---

## 23. Skalowanie na kolejne miasta

Dodanie nowego miasta powinno polegać przede wszystkim na dodaniu nowych providerów danych.

Przykład:

```text
Kraków
├── Krakow Open Data
├── OSM
└── local sources

Warszawa
├── Warsaw Open Data
├── OSM
└── local sources

Vienna
├── Vienna Open Data
├── OSM
└── local sources
```

Wspólny model dostępności pozostaje taki sam.

```text
City-specific sources
        ↓
Accessibility Data Model
        ↓
MCP / API
        ↓
Applications
```

---

## 24. Potencjał komercyjny

Produkt nie musi być wyłącznie aplikacją miejską.

Największą wartością może być:

```text
Accessibility Data API / MCP
```

czyli infrastruktura umożliwiająca innym systemom korzystanie ze zunifikowanych danych o dostępności.

---

## 25. Potencjalni klienci

### Hotele

Hotel może odpowiadać gościowi na pytania dotyczące:

- dostępności hotelu,
- pobliskich restauracji,
- atrakcji,
- muzeów,
- transportu,
- okolicy.

---

### AI Concierge

Agent AI może zapytać MCP:

```text
Czy osoba poruszająca się na wózku może odwiedzić to muzeum?
```

System odpowiada na podstawie strukturalnych danych i pokazuje źródła.

---

### Systemy rezerwacyjne

Możliwość filtrowania miejsc na podstawie konkretnych potrzeb.

Zamiast:

```text
wheelchair accessible
```

można posiadać:

```text
step_free_entrance = true
elevator = true
door_width_cm = 90
accessible_toilet = true
```

---

### Organizatorzy wydarzeń

Możliwość prezentowania informacji o:

- wejściu,
- parkingu,
- toalecie,
- poruszaniu się po obiekcie,
- miejscach siedzących.

---

### Zarządcy nieruchomości

Możliwość utrzymywania aktualnego profilu dostępności budynku.

---

## 26. Model biznesowy

### B2C

Darmowa aplikacja dla:

- mieszkańców,
- turystów.

---

### B2B API / MCP

Firmy płacą za dostęp do danych.

Przykładowy model:

```text
Free
- limited requests
- basic data

Business
- monthly subscription
- higher API limits
- full accessibility data

Enterprise
- custom integrations
- SLA
- dedicated data sources
```

---

### Verified Accessibility Profile

Właściciele obiektów mogą utrzymywać zweryfikowany profil dostępności.

Przykład:

```text
Accessibility profile

Verified by property

Last confirmed:
2026-10-02
```

Taki profil może być wykorzystywany przez:

- systemy rezerwacyjne,
- wyszukiwarki,
- hotele,
- AI concierge,
- aplikacje turystyczne.

---

## 27. Plan realizacji MVP

### Etap 1 — Data Model

Definiujemy wspólny format informacji o dostępności.

Zakres:

```text
entrance
interior
facilities
surroundings
sources
confidence
```

---

### Etap 2 — Data Providers

Integrujemy:

- OpenStreetMap,
- jedno publiczne źródło miejskie,
- kilka oficjalnych stron obiektów.

---

### Etap 3 — Normalization Layer

Tworzymy logikę przekształcającą dane z różnych źródeł do jednego formatu.

---

### Etap 4 — Confidence Engine

Tworzymy podstawową logikę oceny:

```text
HIGH
MEDIUM
LOW
```

oraz wykrywania:

```text
CONFIRMED
UNKNOWN
CONFLICTING
STALE
```

---

### Etap 5 — MCP Server

Implementujemy minimum:

```text
search_places

get_accessibility

get_accessibility_evidence
```

Opcjonalnie:

```text
report_accessibility_issue
```

---

### Etap 6 — Backend API

Backend odpowiada za:

- agregację danych,
- normalizację,
- wykrywanie konfliktów,
- obliczanie confidence,
- komunikację z frontendem.

---

### Etap 7 — Frontend

Tworzymy:

- wyszukiwarkę,
- wybór preferencji,
- listę wyników,
- kartę dostępności,
- widok źródeł,
- podstawową mapę.

---

### Etap 8 — Demo Data Set

Przygotowujemy zestaw obiektów demonstracyjnych.

Minimum:

```text
1 miejsce z kompletnymi danymi

1 miejsce z brakującymi danymi

1 miejsce ze sprzecznymi danymi
```

---

### Etap 9 — Accessibility Check

Sprawdzamy:

- keyboard navigation,
- screen reader,
- kontrast,
- tekstową alternatywę dla mapy.

---

### Etap 10 — Demo

Przygotowujemy główny flow:

```text
Preferences
    ↓
Search
    ↓
Results
    ↓
Place details
    ↓
Accessibility facts
    ↓
Sources
    ↓
Confidence
```

---

## 28. Priorytety implementacji

### P0 — wymagane do demo

- wyszukiwanie miejsca,
- dane o dostępności,
- szczegółowe bariery,
- źródła,
- data aktualizacji,
- confidence,
- obsługa braku danych,
- obsługa sprzecznych danych.

---

### P1 — bardzo wartościowe

- mapa,
- filtry preferencji,
- OpenStreetMap integration,
- MCP Server,
- kilka providerów danych.

---

### P2 — jeśli zostanie czas

- zgłoszenia użytkowników,
- profile właścicieli obiektów,
- zaawansowane filtrowanie,
- routing,
- historia zmian danych.

---

## 29. Kryterium sukcesu MVP

MVP można uznać za działające, jeśli użytkownik może:

1. określić swoje potrzeby,
2. wyszukać miejsce,
3. zobaczyć konkretne bariery i udogodnienia,
4. sprawdzić źródło każdej informacji,
5. zobaczyć aktualność danych,
6. zobaczyć poziom ich wiarygodności,
7. zauważyć, kiedy danych brakuje,
8. zauważyć, kiedy źródła sobie przeczą.

---

## 30. Główna wartość rozwiązania

Nie tworzymy kolejnej mapy pokazującej:

```text
♿ Accessible
```

Tworzymy:

```text
Accessibility Intelligence Layer
```

czyli warstwę, która:

```text
zbiera dane
    ↓
normalizuje dane
    ↓
porównuje źródła
    ↓
wykrywa konflikty
    ↓
określa wiarygodność
    ↓
prezentuje konkretne fakty
```

Użytkownik otrzymuje odpowiedź nie na pytanie:

> Czy to miejsce jest dostępne?

ale:

> Jakie bariery i udogodnienia znajdują się w tym miejscu i na ile można ufać tym informacjom?

---

## 31. Vision

Docelowo Accessibility Data Layer może stać się wspólną infrastrukturą wykorzystywaną przez wiele różnych produktów.

```text
                   Accessibility Data Layer
                             │
             ┌───────────────┼───────────────┐
             │               │               │
             ▼               ▼               ▼
          Web App        AI Concierge    Booking System
             │               │               │
             ▼               ▼               ▼
          Tourist          Hotel          Marketplace
```

Dzięki MCP ta sama infrastruktura może być bezpośrednio wykorzystywana przez agentów AI.

---

## 32. Pitch

> **Kraków bez barier to platforma agregująca i weryfikująca informacje o dostępności miejsc. Zamiast mówić użytkownikowi, że miejsce jest „dostępne” lub „niedostępne”, pokazuje konkretne bariery, udogodnienia, źródła informacji i poziom ich wiarygodności, pozwalając użytkownikowi samodzielnie ocenić, czy dane miejsce odpowiada jego potrzebom.**

---

## 33. MVP w jednym diagramie

```text
                         USER
                           │
                           ▼
                 Accessibility needs
                           │
                           ▼
                     Search place
                           │
                           ▼
                      Web App
                           │
                           ▼
                     Backend API
                           │
                           ▼
                       MCP Server
                           │
                           ▼
               Accessibility Data Layer
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
     OpenStreetMap    City Open Data    Websites
          │                │                │
          └────────────────┼────────────────┘
                           │
                           ▼
                    Normalize data
                           │
                           ▼
                   Detect conflicts
                           │
                           ▼
                 Calculate confidence
                           │
                           ▼
                Accessibility response
                           │
                           ▼
      Facts + sources + freshness + confidence
```