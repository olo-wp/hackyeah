import type { Dictionary } from "./pl";

export const en: Dictionary = {
  localeTag: "en-GB",
  localeName: "English",
  switchTo: "Switch language to Polish",

  metadata: {
    title: "RouteAble — Kraków without barriers",
    description:
      "Concrete information about barriers and facilities in Kraków, with sources, the date they were checked and a confidence level."
  },

  common: {
    siteName: "RouteAble",
    tagline: "Kraków without barriers",
    skipToContent: "Skip to content",
    logoAlt: "RouteAble logo — a dragon in a wheelchair against the Kraków skyline"
  },

  nav: {
    label: "Main menu",
    search: "Find a place",
    howItWorks: "How it works",
    sources: "Data sources"
  },

  a11y: {
    contrastOn: "High contrast",
    contrastOff: "Normal contrast",
    textSizeGroup: "Text size",
    sizeDefault: "Default text size",
    sizeLarger: "Larger text",
    sizeLargest: "Largest text",
    languageGroup: "Language selection"
  },

  breadcrumbs: {
    label: "Breadcrumb",
    home: "Home"
  },

  search: {
    label: "Where do you want to go?",
    placeholder: "e.g. National Museum",
    submit: "Search",
    requirementsLegend: "Your requirements",
    requirementsHint:
      "Requirements only highlight the information that matters to you. RouteAble never rules a place out because of them.",
    preferences: {
      step_free_required: "I need a step-free entrance",
      elevator_required: "I need a lift",
      accessible_toilet_required: "I need an accessible toilet",
      avoid_cobblestone: "I want to avoid cobblestones"
    }
  },

  home: {
    title: "Check how accessible a place in Kraków is",
    lead: "RouteAble does not label a place “accessible” or “not accessible”. It shows concrete barriers and facilities, and for every piece of information its source, the date it was checked and a confidence level — the decision stays yours.",
    resultsHeading: "Search results",
    emptyPrompt: "Enter a place name to start searching.",
    noResults: "No places found for “{query}”.",
    errorStatus: "Could not load results ({status}).",
    errorConnection: "Could not reach the API.",
    showDetails: "Show accessibility details",
    legendHeading: "How to read the information",
    legend: {
      confirmed: {
        title: "Confirmed",
        text: "At least one source confirms this information."
      },
      unknown: { title: "No data", text: "No source holds this information." },
      conflicting: { title: "Conflicting data", text: "Sources report different things." },
      stale: {
        title: "Possibly outdated",
        text: "This information has not been checked for a long time."
      }
    },
    unknownNoticeStrong: "Missing data does not mean accessible.",
    unknownNoticeRest:
      "When sources disagree we show both versions instead of picking one for you.",
    sourcesHeading: "Data sources",
    sourceCards: {
      osm: {
        name: "OpenStreetMap",
        text: "Locations, entrances, lifts, surfaces and accessibility tags.",
        license: "ODbL 1.0"
      },
      krakow: {
        name: "Kraków Open Data",
        text: "Municipal datasets about public buildings.",
        license: "CC BY 4.0"
      },
      website: {
        name: "Official venue websites",
        text: "Accessibility statements — only from allowlisted domains.",
        license: "site terms of use"
      }
    },
    licensePrefix: "Licence:"
  },

  place: {
    metaSources: "Sources",
    metaEvidence: "Individual facts",
    metaLastChecked: "Last checked",
    requirementsHeading: "Your requirements",
    showSources: "Show sources",
    noSources: "No source holds this information.",
    evidenceValue: "Value",
    evidenceCheckedAt: "Checked",
    evidenceLicense: "Licence",
    confidencePrefix: "confidence"
  },

  groups: {
    entrance: "Entrance",
    interior: "Moving around inside",
    facilities: "Facilities",
    surroundings: "Surroundings"
  },

  features: {
    step_free_entrance: "Step-free entrance",
    entrance_steps: "Number of steps",
    ramp: "Ramp",
    threshold_cm: "Threshold",
    door_width_cm: "Door width",
    elevator: "Lift",
    interior_stairs: "Stairs on the route",
    accessible_toilet: "Accessible toilet",
    seating: "Seating",
    surface: "Surface",
    curb: "Kerb",
    accessible_parking: "Accessible parking"
  },

  status: {
    confirmed: "confirmed",
    unknown: "no data",
    conflicting: "conflicting data",
    stale: "possibly outdated"
  },

  confidence: {
    high: "high",
    medium: "medium",
    low: "low"
  },

  value: {
    yes: "yes",
    no: "no",
    noData: "no data",
    needsVerification: "needs verification"
  },

  preferenceResult: {
    meets_preference: "met",
    does_not_meet_preference: "not met",
    unknown: "no data — this does not mean it is accessible",
    needs_verification: "sources disagree — needs verification"
  },

  categories: {
    museum: "museum",
    hotel: "hotel",
    restaurant: "restaurant",
    attraction: "attraction",
    event_venue: "event venue",
    other: "other"
  },

  surfaces: {
    asphalt: "asphalt",
    concrete: "concrete",
    paving_stones: "paving stones",
    cobblestone: "cobblestone",
    gravel: "gravel",
    unpaved: "unpaved",
    unknown: "unknown"
  },

  providers: {
    heading: "Data source status",
    osm: "OpenStreetMap",
    krakow: "Kraków Open Data",
    website: "Official venue website"
  },

  providerStatus: {
    success: "fetched",
    cached: "from cache",
    failed: "source unavailable — cached data used",
    not_applicable: "no data for this place"
  },

  footer: {
    description:
      "A platform that aggregates and verifies accessibility information about places in Kraków. It does not label a place “accessible” or “not accessible” — it shows facts, sources and how reliable they are.",
    aboutHeading: "About this service",
    links: {
      sources: "Data sources and licences",
      accessibility: "Accessibility statement",
      confidence: "How the confidence level is calculated",
      portal: "Kraków Open Data Portal",
      osmLicense: "OpenStreetMap — ODbL licence"
    },
    brandHeading: "Kraków without barriers",
    brandTagline: "An open city for everyone",
    note: "Data comes from OpenStreetMap, municipal open data and official venue websites. Missing data does not mean accessible."
  }
};
