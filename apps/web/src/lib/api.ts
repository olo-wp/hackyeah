import type {
  AccessibilityPreferences,
  CommunityFeatureKey,
  CommunitySummary,
  DoorstepLevel,
  PlaceAccessibilityResult,
  PlaceSearchResult
} from "./types";

const API_URL = (process.env.ROUTEABLE_API_URL ?? "http://localhost:3001").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function get<T>(path: string, params: Record<string, string> = {}): Promise<T> {
  const query = new URLSearchParams(params).toString();
  const response = await fetch(`${API_URL}${path}${query ? `?${query}` : ""}`, {
    cache: "no-store",
    headers: { Accept: "application/json" }
  });

  if (!response.ok) {
    throw new ApiError(`Request to ${path} failed`, response.status);
  }

  return (await response.json()) as T;
}

export function searchPlaces(query: string, city = "Kraków"): Promise<PlaceSearchResult> {
  return get<PlaceSearchResult>("/api/places/search", { q: query, city });
}

export function getPlaceAccessibility(
  placeId: string,
  preferences: AccessibilityPreferences = {}
): Promise<PlaceAccessibilityResult> {
  const params = Object.fromEntries(
    Object.entries(preferences)
      .filter(([, value]) => value !== undefined && value !== false)
      .map(([key, value]) => [key, String(value)])
  );

  return get<PlaceAccessibilityResult>(
    `/api/places/${encodeURIComponent(placeId)}/accessibility`,
    params
  );
}

export function getCommunitySummary(placeId: string): Promise<CommunitySummary> {
  return get<CommunitySummary>(`/api/places/${encodeURIComponent(placeId)}/community`);
}

export async function postCommunityContribution(
  placeId: string,
  featureKey: CommunityFeatureKey,
  value: boolean | DoorstepLevel
): Promise<void> {
  const response = await fetch(`${API_URL}/api/places/${encodeURIComponent(placeId)}/community`, {
    method: "POST",
    cache: "no-store",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ feature_key: featureKey, value })
  });

  if (!response.ok) {
    throw new ApiError("Request to submit a community contribution failed", response.status);
  }
}
