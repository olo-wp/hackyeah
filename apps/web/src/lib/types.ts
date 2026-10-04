/** Mirrors the snake_case JSON returned by the Python API. */

export type FeatureStatus = "confirmed" | "unknown" | "conflicting" | "stale";
export type ConfidenceLevel = "high" | "medium" | "low";

export type PlaceCategory =
  | "museum"
  | "hotel"
  | "restaurant"
  | "attraction"
  | "event_venue"
  | "other";

export interface GeoLocation {
  lat: number;
  lng: number;
}

export interface RouteOrigin {
  label: string;
  location: GeoLocation;
}

export interface WalkingRoute {
  geometry: { type: "LineString"; coordinates: [number, number][] };
  distance_m: number;
  duration_s: number;
}

export interface Place {
  id: string;
  name: string;
  category: PlaceCategory;
  address: string | null;
  location: GeoLocation;
  external_ids: {
    osm?: string | null;
    city_dataset?: string | null;
    website?: string | null;
  };
}

export interface DataSource {
  id: string;
  type: string;
  name: string;
  url: string | null;
  license: string | null;
}

export interface Evidence {
  id: string;
  place_id: string;
  feature_key: string;
  source: DataSource;
  value: unknown;
  retrieved_at: string;
  observed_at: string | null;
  verification_status: string;
}

export interface AccessibilityFeature<T = unknown> {
  key: string;
  value: T | null;
  status: FeatureStatus;
  confidence: ConfidenceLevel | null;
  evidence: Evidence[];
  conflict_reason: string | null;
}

export interface AccessibilityProfile {
  place_id: string;
  entrance: {
    step_free: AccessibilityFeature<boolean>;
    steps: AccessibilityFeature<number>;
    ramp: AccessibilityFeature<boolean>;
    threshold_cm: AccessibilityFeature<number>;
    door_width_cm: AccessibilityFeature<number>;
  };
  interior: {
    elevator: AccessibilityFeature<boolean>;
    stairs: AccessibilityFeature<boolean>;
  };
  facilities: {
    accessible_toilet: AccessibilityFeature<boolean>;
    seating: AccessibilityFeature<boolean>;
  };
  surroundings: {
    surface: AccessibilityFeature<string>;
    curb: AccessibilityFeature<boolean>;
    accessible_parking: AccessibilityFeature<boolean>;
  };
  metadata: {
    source_count: number;
    evidence_count: number;
    last_updated: string | null;
  };
}

export interface ProviderStatus {
  provider: string;
  status: "success" | "failed" | "cached" | "not_applicable";
  last_fetched_at: string | null;
  error: string | null;
}

export interface PlaceSearchResult {
  results: Place[];
  provider_status: ProviderStatus[];
}

export interface PreferenceEvaluation {
  key: string;
  preference: unknown;
  observed_value: unknown;
  result: "meets_preference" | "does_not_meet_preference" | "unknown" | "needs_verification";
}

export interface PlaceAccessibilityResult {
  place: Place;
  profile: AccessibilityProfile;
  preference_evaluation: PreferenceEvaluation[];
  provider_status: ProviderStatus[];
}

export interface AccessibilityPreferences {
  step_free_required?: boolean;
  elevator_required?: boolean;
  accessible_toilet_required?: boolean;
  avoid_cobblestone?: boolean;
  min_door_width_cm?: number;
}

export type CommunityFeatureKey =
  | "step_free_entrance"
  | "entrance_steps"
  | "ramp"
  | "threshold_cm"
  | "door_width_cm"
  | "elevator"
  | "interior_stairs"
  | "accessible_toilet"
  | "seating"
  | "surface"
  | "curb"
  | "accessible_parking";

export type CommunityValue = boolean | string;

export interface CommunityFeatureSummary {
  feature_key: CommunityFeatureKey;
  total_responses: number;
  distribution: Record<string, number>;
  top_value: CommunityValue | null;
  latest_value: CommunityValue | null;
  last_submitted_at: string | null;
}

export interface CommunitySummary {
  place_id: string;
  features: CommunityFeatureSummary[];
}
