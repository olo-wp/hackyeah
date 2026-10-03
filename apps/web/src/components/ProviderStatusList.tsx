import type { ProviderStatus } from "@/lib/types";

const LABELS: Record<ProviderStatus["status"], { icon: string; text: string }> = {
  success: { icon: "✓", text: "pobrano" },
  cached: { icon: "◷", text: "z pamięci podręcznej" },
  failed: { icon: "⚠", text: "źródło niedostępne — użyto danych z pamięci podręcznej" },
  not_applicable: { icon: "–", text: "brak danych dla tego miejsca" }
};

const PROVIDER_NAMES: Record<string, string> = {
  osm: "OpenStreetMap",
  krakow: "Otwarte Dane Miasta Krakowa",
  website: "Oficjalna strona obiektu"
};

export function ProviderStatusList({ statuses }: { statuses: ProviderStatus[] }) {
  return (
    <section id="zrodla" className="mt-8">
      <h2 className="kr-card-blue px-4 py-3 text-xl font-bold">Stan źródeł danych</h2>
      <ul className="kr-card border-t-0">
        {statuses.map((status) => {
          const label = LABELS[status.status];
          return (
            <li
              key={status.provider}
              className="flex flex-wrap items-baseline justify-between gap-2 border-b border-[var(--color-rule)] px-4 py-3 text-sm last:border-b-0"
            >
              <span className="font-bold">
                <span aria-hidden="true">{label.icon} </span>
                {PROVIDER_NAMES[status.provider] ?? status.provider}
              </span>
              <span className="text-[var(--color-muted)]">
                {label.text}
                {status.last_fetched_at
                  ? ` · ${new Date(status.last_fetched_at).toLocaleString("pl-PL")}`
                  : ""}
              </span>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
