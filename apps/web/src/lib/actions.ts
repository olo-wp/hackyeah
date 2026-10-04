"use server";

import { revalidatePath } from "next/cache";
import { postCommunityContribution } from "./api";
import type { CommunityFeatureKey, CommunityValue } from "./types";

export async function submitCommunityContribution(
  locale: string,
  placeId: string,
  featureKey: CommunityFeatureKey,
  value: CommunityValue
): Promise<void> {
  await postCommunityContribution(placeId, featureKey, value);
  revalidatePath(`/${locale}/places/${placeId}`);
  revalidatePath(`/${locale}/contribute`);
}
