import type { Dictionary } from "@/i18n";
import type { ProviderStatus } from "@/lib/types";

const ICONS: Record<ProviderStatus["status"], string> = {
  success: "✓",
  cached: "◷",
  failed: "⚠",
  not_applicable: "–"
};

export function ProviderStatusList({
  statuses,
  dict
}: {
  statuses: ProviderStatus[];
  dict: Dictionary;
}) {
  const providerName = (provider: string) =>
    dict.providers[provider as keyof Dictionary["providers"]] ?? provider;

  return (
    <section id="zrodla" className="mt-8">
      <h2 className="kr-card-blue px-4 py-3 text-xl font-bold">{dict.providers.heading}</h2>
      <ul className="kr-card border-t-0">
        {statuses.map((status) => (
          <li
            key={status.provider}
            className="flex flex-wrap items-baseline justify-between gap-2 border-b border-[var(--color-rule)] px-4 py-3 text-sm last:border-b-0"
          >
            <span className="font-bold">
              <span aria-hidden="true">{ICONS[status.status]} </span>
              {providerName(status.provider)}
            </span>
            <span className="text-[var(--color-muted)]">
              {dict.providerStatus[status.status]}
              {status.last_fetched_at
                ? ` · ${new Date(status.last_fetched_at).toLocaleString(dict.localeTag)}`
                : ""}
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}
