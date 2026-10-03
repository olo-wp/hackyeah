import type { ProviderStatus } from "@/lib/types";

const LABELS: Record<ProviderStatus["status"], string> = {
  success: "pobrano",
  cached: "z pamięci podręcznej",
  failed: "źródło niedostępne — użyto danych z pamięci podręcznej",
  not_applicable: "brak danych dla tego miejsca"
};

export function ProviderStatusList({ statuses }: { statuses: ProviderStatus[] }) {
  return (
    <section className="mt-8">
      <h2 className="text-lg font-semibold">Stan źródeł</h2>
      <ul className="mt-2 text-sm text-slate-700">
        {statuses.map((status) => (
          <li key={status.provider} className="py-1">
            <span className="font-medium">{status.provider}</span>: {LABELS[status.status]}
            {status.last_fetched_at
              ? ` (${new Date(status.last_fetched_at).toLocaleString("pl-PL")})`
              : ""}
          </li>
        ))}
      </ul>
    </section>
  );
}
