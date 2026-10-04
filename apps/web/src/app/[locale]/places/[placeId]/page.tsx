import { notFound } from "next/navigation";
import { Breadcrumbs } from "@/components/Breadcrumbs";
import { CommunityAnswers } from "@/components/CommunityAnswers";
import { FeatureGroup } from "@/components/FeatureGroup";
import { RoutePlanner } from "@/components/RoutePlanner";
import { getDictionary } from "@/i18n";
import { isLocale } from "@/i18n/config";
import { ApiError, getCommunitySummary, getPlaceAccessibility } from "@/lib/api";
import type {
  AccessibilityPreferences,
  CommunitySummary,
  PreferenceEvaluation
} from "@/lib/types";

type SearchParams = Promise<Record<string, string | string[] | undefined>>;

const RESULT_ICONS: Record<PreferenceEvaluation["result"], string> = {
  meets_preference: "✓",
  does_not_meet_preference: "✕",
  unknown: "?",
  needs_verification: "⚠"
};

function readPreferences(params: Awaited<SearchParams>): AccessibilityPreferences {
  const isSet = (key: string) => params[key] === "true";

  return {
    step_free_required: isSet("step_free_required"),
    elevator_required: isSet("elevator_required"),
    accessible_toilet_required: isSet("accessible_toilet_required"),
    avoid_cobblestone: isSet("avoid_cobblestone")
  };
}

export default async function PlacePage({
  params,
  searchParams
}: {
  params: Promise<{ locale: string; placeId: string }>;
  searchParams: SearchParams;
}) {
  const { locale, placeId } = await params;
  if (!isLocale(locale)) notFound();

  const dict = getDictionary(locale);
  const preferences = readPreferences(await searchParams);

  let data;
  try {
    data = await getPlaceAccessibility(decodeURIComponent(placeId), preferences);
  } catch (cause) {
    if (cause instanceof ApiError && cause.status === 404) notFound();
    throw cause;
  }

  const { place, profile, preference_evaluation: evaluations } = data;
  const labels = dict.features;

  let community: CommunitySummary | null = null;
  try {
    community = await getCommunitySummary(decodeURIComponent(placeId));
  } catch {
    community = null;
  }

  return (
    <>
      <Breadcrumbs
        locale={locale}
        labels={dict.breadcrumbs}
        items={[{ href: `/${locale}`, label: dict.nav.search }, { label: place.name }]}
      />

      <header className="mt-6">
        <h1 className="kr-heading text-3xl sm:text-4xl">{place.name}</h1>
        {place.address ? <p className="mt-2 text-lg">{place.address}</p> : null}
        <p className="mt-2 text-sm text-[var(--color-muted)]">
          {dict.place.metaSources}: {profile.metadata.source_count} ·{" "}
          {dict.place.metaEvidence}: {profile.metadata.evidence_count}
          {profile.metadata.last_updated
            ? ` · ${dict.place.metaLastChecked}: ${new Date(
                profile.metadata.last_updated
              ).toLocaleString(dict.localeTag)}`
            : ""}
        </p>
      </header>

      {evaluations.length > 0 ? (
        <section className="mt-8">
          <h2 className="kr-card-blue px-4 py-3 text-xl font-bold">
            {dict.place.requirementsHeading}
          </h2>
          <ul className="kr-card border-t-0">
            {evaluations.map((evaluation) => (
              <li
                key={evaluation.key}
                className="flex flex-wrap items-baseline justify-between gap-2 border-b border-[var(--color-rule)] px-4 py-3 last:border-b-0"
              >
                <span className="font-bold">
                  <span aria-hidden="true">{RESULT_ICONS[evaluation.result]} </span>
                  {labels[evaluation.key as keyof typeof labels] ?? evaluation.key}
                </span>
                <span className="text-sm text-[var(--color-muted)]">
                  {dict.preferenceResult[evaluation.result]}
                </span>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      <FeatureGroup
        title={dict.groups.entrance}
        dict={dict}
        community={community ?? undefined}
        features={[
          { label: labels.step_free_entrance, feature: profile.entrance.step_free },
          { label: labels.entrance_steps, feature: profile.entrance.steps },
          { label: labels.ramp, feature: profile.entrance.ramp },
          { label: `${labels.threshold_cm} (cm)`, feature: profile.entrance.threshold_cm },
          { label: `${labels.door_width_cm} (cm)`, feature: profile.entrance.door_width_cm }
        ]}
      />

      <FeatureGroup
        title={dict.groups.interior}
        dict={dict}
        community={community ?? undefined}
        features={[
          { label: labels.elevator, feature: profile.interior.elevator },
          { label: labels.interior_stairs, feature: profile.interior.stairs }
        ]}
      />

      <FeatureGroup
        title={dict.groups.facilities}
        dict={dict}
        community={community ?? undefined}
        features={[
          { label: labels.accessible_toilet, feature: profile.facilities.accessible_toilet },
          { label: labels.seating, feature: profile.facilities.seating }
        ]}
      />

      <FeatureGroup
        title={dict.groups.surroundings}
        dict={dict}
        community={community ?? undefined}
        features={[
          { label: labels.surface, feature: profile.surroundings.surface },
          { label: labels.curb, feature: profile.surroundings.curb },
          {
            label: labels.accessible_parking,
            feature: profile.surroundings.accessible_parking
          }
        ]}
      />
      <RoutePlanner place={place} dict={dict} />

      <CommunityAnswers locale={locale} placeId={place.id} dict={dict.community} />
    </>
  );
}
