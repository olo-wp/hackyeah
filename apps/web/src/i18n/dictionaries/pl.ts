export const pl = {
  localeTag: "pl-PL",
  localeName: "Polski",
  switchTo: "Zmień język na angielski",

  metadata: {
    title: "RouteAble — Kraków bez barier",
    description:
      "Konkretne informacje o barierach i udogodnieniach w Krakowie, wraz ze źródłami, datą sprawdzenia i poziomem wiarygodności."
  },

  common: {
    siteName: "RouteAble",
    tagline: "Kraków bez barier",
    skipToContent: "Przejdź do treści",
    logoAlt: "Logo RouteAble — smok na wózku na tle panoramy Krakowa",
    krakowLogoAlt: "Logo Miasta Krakowa"
  },

  nav: {
    label: "Menu główne",
    search: "Szukaj miejsca",
    howItWorks: "Jak to działa",
    sources: "Źródła danych"
  },

  a11y: {
    contrastOn: "Wysoki kontrast",
    contrastOff: "Zwykły kontrast",
    textSizeGroup: "Rozmiar tekstu",
    sizeDefault: "Domyślny rozmiar tekstu",
    sizeLarger: "Większy tekst",
    sizeLargest: "Największy tekst",
    languageGroup: "Wybór języka"
  },

  breadcrumbs: {
    label: "Ścieżka nawigacji",
    home: "Start"
  },

  search: {
    label: "Gdzie chcesz się dostać?",
    placeholder: "np. Muzeum Narodowe",
    submit: "Szukaj",
    requirementsLegend: "Potrzebuję:",
    requirementsHint:
      "Wymagania służą wyłącznie do wyróżnienia istotnych informacji. RouteAble nie odrzuca na ich podstawie żadnego miejsca.",
    preferences: {
      step_free_required: "wejścia bez schodów",
      elevator_required: "windy",
      accessible_toilet_required: "dostępnej toalety",
      avoid_cobblestone: "trasy bez kostki brukowej"
    }
  },

  home: {
    title: "Sprawdź dostępność miejsca w Krakowie",
    lead: "Znajdź miejsca i trasy dopasowane do swoich potrzeb. Sprawdź szczegółowe informacje o dostępności, zanim wyruszysz w drogę.",
    resultsHeading: "Wyniki wyszukiwania",
    loading: "Szukam miejsc…",
    loadingHint: "Odpytujemy OpenStreetMap, dane miejskie i strony obiektów — to może chwilę potrwać.",
    loadingAlt: "Smok na hulajnodze — trwa wyszukiwanie",
    emptyPrompt: "Wpisz nazwę miejsca, aby rozpocząć wyszukiwanie.",
    noResults: "Nie znaleziono miejsc dla zapytania „{query}”.",
    errorStatus: "Nie udało się pobrać wyników ({status}).",
    errorConnection: "Nie udało się połączyć z API.",
    showDetails: "Pokaż szczegóły dostępności",
    showRoute: "Pokaż trasę",
    legendHeading: "Jak czytać informacje",
    legend: {
      confirmed: {
        title: "Potwierdzone",
        text: "Co najmniej jedno źródło potwierdza informację."
      },
      unknown: { title: "Brak danych", text: "Żadne źródło nie zawiera tej informacji." },
      conflicting: { title: "Dane sprzeczne", text: "Źródła podają różne informacje." },
      stale: {
        title: "Możliwe nieaktualne",
        text: "Informacja nie była dawno sprawdzana."
      }
    },
    unknownNoticeStrong: "Brak danych nie oznacza dostępności.",
    unknownNoticeRest:
      "Jeżeli źródła się nie zgadzają, pokazujemy obie wersje zamiast wybierać jedną za Ciebie.",
    sourcesHeading: "Źródła danych",
    sourceCards: {
      osm: {
        name: "OpenStreetMap",
        text: "Lokalizacje, wejścia, windy, nawierzchnie i tagi dostępności.",
        license: "ODbL 1.0"
      },
      krakow: {
        name: "Otwarte Dane Miasta Krakowa",
        text: "Miejskie zbiory danych o obiektach publicznych.",
        license: "CC BY 4.0"
      },
      website: {
        name: "Oficjalne strony obiektów",
        text: "Deklaracje dostępności — wyłącznie z domen na liście dozwolonych.",
        license: "warunki danego serwisu"
      }
    },
    licensePrefix: "Licencja:"
  },

  place: {
    metaSources: "Źródła",
    metaEvidence: "Pojedyncze informacje",
    metaLastChecked: "Ostatnie sprawdzenie",
    requirementsHeading: "Twoje wymagania",
    showSources: "Pokaż źródła",
    noSources: "Żadne źródło nie zawiera tej informacji.",
    evidenceValue: "Wartość",
    evidenceCheckedAt: "Sprawdzono",
    evidenceLicense: "Licencja",
    confidencePrefix: "wiarygodność"
  },

  route: {
    heading: "Trasa piesza",
    disclaimer: "Dostępność trasy nie jest zweryfikowana. Sprawdź informacje o miejscu przed podróżą.",
    currentLocation: "Użyj mojej lokalizacji",
    locationDenied: "Nie udało się pobrać lokalizacji. Wpisz adres początku trasy.",
    startAddress: "Adres początku trasy",
    addressPlaceholder: "np. Rynek Główny, Kraków",
    searchAddress: "Znajdź adres",
    addressResults: "Wybierz adres",
    noAddresses: "Nie znaleziono adresu. Spróbuj wpisać go inaczej.",
    addressError: "Nie udało się wyszukać adresów. Spróbuj ponownie.",
    routeError: "Nie udało się wyznaczyć trasy. Sprawdź punkt startowy i spróbuj ponownie.",
    noRoute: "Nie znaleziono trasy pieszej między tymi miejscami.",
    notConfigured: "Wyznaczanie trasy nie jest skonfigurowane.",
    calculating: "Wyznaczam trasę…",
    searchPending: "Szukam adresów…",
    summary: "Trasa: {distance} km, około {minutes} min",
    mapUnavailable: "Mapa jest niedostępna. Możesz nadal przeczytać szczegóły miejsca.",
    mapLabel: "Mapa trasy do {place}"
  },

  groups: {
    entrance: "Wejście",
    interior: "Poruszanie się wewnątrz",
    facilities: "Udogodnienia",
    surroundings: "Otoczenie"
  },

  features: {
    step_free_entrance: "Wejście bez schodów",
    entrance_steps: "Liczba stopni",
    ramp: "Podjazd",
    threshold_cm: "Próg",
    door_width_cm: "Szerokość wejścia",
    elevator: "Winda",
    interior_stairs: "Schody na trasie",
    accessible_toilet: "Dostępna toaleta",
    seating: "Miejsca odpoczynku",
    surface: "Nawierzchnia",
    curb: "Krawężnik",
    accessible_parking: "Miejsce parkingowe"
  },

  status: {
    confirmed: "potwierdzone",
    unknown: "brak danych",
    conflicting: "dane sprzeczne",
    stale: "możliwe nieaktualne"
  },

  confidence: {
    high: "wysoka",
    medium: "średnia",
    low: "niska"
  },

  value: {
    yes: "tak",
    no: "nie",
    noData: "brak danych",
    needsVerification: "wymaga weryfikacji"
  },

  preferenceResult: {
    meets_preference: "spełnione",
    does_not_meet_preference: "niespełnione",
    unknown: "brak danych — to nie znaczy, że jest dostępne",
    needs_verification: "źródła są sprzeczne — wymaga weryfikacji"
  },

  categories: {
    museum: "muzeum",
    hotel: "hotel",
    restaurant: "restauracja",
    attraction: "atrakcja",
    event_venue: "obiekt wydarzeń",
    other: "inne"
  },

  surfaces: {
    asphalt: "asfalt",
    concrete: "beton",
    paving_stones: "kostka betonowa",
    cobblestone: "kostka brukowa",
    gravel: "żwir",
    unpaved: "nieutwardzona",
    unknown: "nieznana"
  },

  providers: {
    heading: "Stan źródeł danych",
    osm: "OpenStreetMap",
    krakow: "Otwarte Dane Miasta Krakowa",
    website: "Oficjalna strona obiektu"
  },

  providerStatus: {
    success: "pobrano",
    cached: "z pamięci podręcznej",
    failed: "źródło niedostępne — użyto danych z pamięci podręcznej",
    not_applicable: "brak danych dla tego miejsca"
  },

  footer: {
    description:
      "Platforma agregująca i weryfikująca informacje o dostępności miejsc w Krakowie. Nie ocenia miejsca jako „dostępne” lub „niedostępne” — pokazuje fakty, źródła i poziom ich wiarygodności.",
    aboutHeading: "O serwisie",
    links: {
      sources: "Źródła danych i licencje",
      accessibility: "Deklaracja dostępności",
      confidence: "Jak powstaje ocena wiarygodności",
      portal: "Portal Otwarte Dane Miasta Krakowa",
      osmLicense: "OpenStreetMap — licencja ODbL"
    },
    brandHeading: "Kraków bez barier",
    brandTagline: "Otwarte miasto dla każdego",
    note: "Dane pochodzą z OpenStreetMap, otwartych danych miejskich i oficjalnych stron obiektów. Brak danych nie oznacza dostępności."
  }
};

/** Shape every locale must provide — missing keys fail the build. */
export type Dictionary = typeof pl;
