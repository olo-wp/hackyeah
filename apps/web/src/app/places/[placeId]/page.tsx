import Link from "next/link";
import { notFound } from "next/navigation";
import { FeatureGroup } from "@/components/FeatureGroup";
import { ProviderStatusList } from "@/components/ProviderStatusList";
import { ApiError, getPlaceAccessibility } from "@/lib/api";
import type { AccessibilityPreferences } from "@/lib/types";

type SearchParams = Promise<Record<string, string | string[] | undefined>>;

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
      <nav aria-label="Okruszki">
        <Link href="/" className="text-blue-800 underline">
          ← Wróć do wyszukiwania
        </Link>
      </nav>

      <h1 className="mt-4 text-2xl font-bold">{place.name}</h1>
      {place.address ? <p className="text-slate-700">{place.address}</p> : null}
      <p className="mt-1 text-sm text-slate-600">
        Źródła: {profile.metadata.source_count} · Informacje: {profile.metadata.evidence_count}
        {profile.metadata.last_updated
          ? ` · Ostatnia aktualizacja: ${new Date(profile.metadata.last_updated).toLocaleString("pl-PL")}`
          : ""}
      </p>

      {evaluations.length > 0 ? (
        <section className="mt-6">
          <h2 className="text-lg font-semibold">Twoje wymagania</h2>
          <ul className="mt-2 text-sm">
            {evaluations.map((evaluation) => (
              <li key={evaluation.key} className="py-1">
                {evaluation.key}: {evaluation.result}
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      <FeatureGroup
        title="Wejście"
        features={[
          { label: "Wejście bez schodów", feature: profile.entrance.step_free },
          { label: "Liczba stopni", feature: profile.entrance.steps },
          { label: "Podjazd", feature: profile.entrance.ramp },
          { label: "Próg (cm)", feature: profile.entrance.threshold_cm },
          { label: "Szerokość wejścia (cm)", feature: profile.entrance.door_width_cm }
        ]}
      />

      <FeatureGroup
        title="Wewnątrz"
        features={[
          { label: "Winda", feature: profile.interior.elevator },
          { label: "Schody na trasie", feature: profile.interior.stairs }
        ]}
      />

      <FeatureGroup
        title="Udogodnienia"
        features={[
          { label: "Dostępna toaleta", feature: profile.facilities.accessible_toilet },
          { label: "Miejsca odpoczynku", feature: profile.facilities.seating }
        ]}
      />

      <FeatureGroup
        title="Otoczenie"
        features={[
          { label: "Nawierzchnia", feature: profile.surroundings.surface },
          { label: "Krawężnik", feature: profile.surroundings.curb },
          { label: "Miejsce parkingowe", feature: profile.surroundings.accessible_parking }
        ]}
      />

      <ProviderStatusList statuses={providers} />
    </>
  );
}
