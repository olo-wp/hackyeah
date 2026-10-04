import type { Dictionary } from "@/i18n";
import type { CommunityFeatureKey, CommunityValue } from "./types";

/** Vote options per feature; `null` marks a yes/no question. Mirrors the API. */
export const COMMUNITY_OPTIONS: Record<CommunityFeatureKey, string[] | null> = {
  step_free_entrance: null,
  entrance_steps: ["none", "few", "some", "many"],
  ramp: null,
  threshold_cm: ["none", "small", "high"],
  door_width_cm: ["narrow", "wide"],
  elevator: null,
  interior_stairs: null,
  accessible_toilet: null,
  seating: null,
  surface: ["asphalt", "concrete", "paving_stones", "cobblestone", "gravel", "unpaved"],
  curb: null,
  accessible_parking: null
};

export type CommunityChoice = { key: string; label: string; value: CommunityValue };

export function communityChoices(
  featureKey: CommunityFeatureKey,
  dict: Dictionary
): CommunityChoice[] {
  const options = COMMUNITY_OPTIONS[featureKey];
  const c = dict.community;
  if (options === null) {
    return [
      { key: "true", label: c.answers.yes, value: true },
      { key: "false", label: c.answers.no, value: false }
    ];
  }

  const labelFor = (key: string): string => {
    if (featureKey === "surface") return dict.surfaces[key as keyof Dictionary["surfaces"]] ?? key;
    if (featureKey === "entrance_steps") return c.steps[key as keyof typeof c.steps] ?? key;
    if (featureKey === "threshold_cm") return c.threshold[key as keyof typeof c.threshold] ?? key;
    if (featureKey === "door_width_cm") return c.doorWidth[key as keyof typeof c.doorWidth] ?? key;
    return key;
  };

  return options.map((key) => ({ key, label: labelFor(key), value: key }));
}

export function communityValueKey(value: CommunityValue): string {
  if (typeof value === "boolean") return value ? "true" : "false";
  return value;
}
