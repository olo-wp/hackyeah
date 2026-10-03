import { notFound } from "next/navigation";
import { Breadcrumbs } from "@/components/Breadcrumbs";
import { FeatureGroup } from "@/components/FeatureGroup";
import { ProviderStatusList } from "@/components/ProviderStatusList";
import { ApiError, getPlaceAccessibility } from "@/lib/api";
import type { AccessibilityPreferences, PreferenceEvaluation } from "@/lib/types";

type SearchParams = Promise<Record<string, string | string[] | undefined>>;

const FEATURE_LABELS: Record<string, string> = {
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
};

const RESULT_LABELS: Record<PreferenceEvaluation["result"], { icon: string; text: string }> = {
  meets_preference: { icon: "✓", text: "spełnione" },
  does_not_meet_preference: { icon: "✕", text: "niespełnione" },
  unknown: { icon: "?", text: "brak danych — to nie znaczy, że jest dostępne" },
  needs_verification: { icon: "⚠", text: "źródła są sprzeczne — wymaga weryfikacji" }
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
  params: Promise<{ placeId: string }>;
  searchParams: SearchParams;
}) {
  const { placeId } = await params;
  const preferences = readPreferences(await searchParams);

  let data;
  try {
    data = await getPlaceAccessibility(decodeURIComponent(placeId), preferences);
  } catch (cause) {
    if (cause instanceof ApiError && cause.status === 404) notFound();
    throw cause;
  }

  const { place, profile, preference_evaluation: evaluations, provider_status: providers } = data;

  return (
    <>
      <Breadcrumbs items={[{ href: "/", label: "Szukaj miejsca" }, { label: place.name }]} />

      <header className="mt-6">
        <h1 className="kr-heading text-3xl sm:text-4xl">{place.name}</h1>
        {place.address ? <p className="mt-2 text-lg">{place.address}</p> : null}
        <p className="mt-2 text-sm text-[var(--color-muted)]">
          Źródła: {profile.metadata.source_count} · Pojedyncze informacje:{" "}
          {profile.metadata.evidence_count}
          {profile.metadata.last_updated
            ? ` · Ostatnie sprawdzenie: ${new Date(profile.metadata.last_updated).toLocaleString("pl-PL")}`
            : ""}
        </p>
      </header>

      {evaluations.length > 0 ? (
        <section className="mt-8">
          <h2 className="kr-card-blue px-4 py-3 text-xl font-bold">Twoje wymagania</h2>
          <ul className="kr-card border-t-0">
            {evaluations.map((evaluation) => {
              const label = RESULT_LABELS[evaluation.result];
              return (
                <li
                  key={evaluation.key}
                  className="flex flex-wrap items-baseline justify-between gap-2 border-b border-[var(--color-rule)] px-4 py-3 last:border-b-0"
                >
                  <span className="font-bold">
                    <span aria-hidden="true">{label.icon} </span>
                    {FEATURE_LABELS[evaluation.key] ?? evaluation.key}
                  </span>
                  <span className="text-sm text-[var(--color-muted)]">{label.text}</span>
                </li>
              );
            })}
          </ul>
        </section>
      ) : null}

      <FeatureGroup
        title="Wejście"
        features={[
          { label: FEATURE_LABELS.step_free_entrance, feature: profile.entrance.step_free },
          { label: FEATURE_LABELS.entrance_steps, feature: profile.entrance.steps },
          { label: FEATURE_LABELS.ramp, feature: profile.entrance.ramp },
          { label: `${FEATURE_LABELS.threshold_cm} (cm)`, feature: profile.entrance.threshold_cm },
          {
            label: `${FEATURE_LABELS.door_width_cm} (cm)`,
            feature: profile.entrance.door_width_cm
          }
        ]}
      />

      <FeatureGroup
        title="Poruszanie się wewnątrz"
        features={[
          { label: FEATURE_LABELS.elevator, feature: profile.interior.elevator },
          { label: FEATURE_LABELS.interior_stairs, feature: profile.interior.stairs }
        ]}
      />

      <FeatureGroup
        title="Udogodnienia"
        features={[
          { label: FEATURE_LABELS.accessible_toilet, feature: profile.facilities.accessible_toilet },
          { label: FEATURE_LABELS.seating, feature: profile.facilities.seating }
        ]}
      />

      <FeatureGroup
        title="Otoczenie"
        features={[
          { label: FEATURE_LABELS.surface, feature: profile.surroundings.surface },
          { label: FEATURE_LABELS.curb, feature: profile.surroundings.curb },
          {
            label: FEATURE_LABELS.accessible_parking,
            feature: profile.surroundings.accessible_parking
          }
        ]}
      />

      <ProviderStatusList statuses={providers} />
    </>
  );
}
