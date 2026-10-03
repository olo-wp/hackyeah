import type { AccessibilityFeature } from "@/lib/types";
import { StatusBadge } from "./StatusBadge";

const CONFIDENCE_LABEL = {
  high: "wysoka",
  medium: "średnia",
  low: "niska"
} as const;

function renderValue(feature: AccessibilityFeature): string {
  if (feature.status === "conflicting") return "wymaga weryfikacji";
  if (feature.value === null || feature.value === undefined) return "brak danych";
  if (typeof feature.value === "boolean") return feature.value ? "tak" : "nie";
  return String(feature.value);
}

function formatDate(value: string): string {
  return new Date(value).toLocaleDateString("pl-PL");
}

export function FeatureRow({ label, feature }: { label: string; feature: AccessibilityFeature }) {
  return (
    <li className="border-b border-[var(--color-rule)] px-4 py-4 last:border-b-0">
      <div className="flex flex-wrap items-baseline justify-between gap-3">
        <h3 className="text-lg font-bold">{label}</h3>
        <StatusBadge status={feature.status} />
      </div>

      <p className="mt-1 text-lg">{renderValue(feature)}</p>

      {feature.conflict_reason ? (
        <p className="mt-2 border-l-4 border-[#8a4b00] bg-[#fdf0e0] px-3 py-2 text-sm text-[#8a4b00]">
          {feature.conflict_reason}
        </p>
      ) : null}

      {feature.evidence.length > 0 ? (
        <details className="mt-3">
          <summary className="link-kr cursor-pointer text-sm font-bold">
            Pokaż źródła ({feature.evidence.length})
            {feature.confidence ? ` · wiarygodność: ${CONFIDENCE_LABEL[feature.confidence]}` : ""}
          </summary>

          <ul className="mt-2 border border-[var(--color-rule)]">
            {feature.evidence.map((item) => (
              <li
                key={item.id}
                className="border-b border-[var(--color-rule)] px-3 py-2 text-sm last:border-b-0"
              >
                <p className="font-bold">
                  {item.source.url ? (
                    <a
                      href={item.source.url}
                      className="link-kr"
                      rel="noreferrer noopener"
                      target="_blank"
                    >
                      {item.source.name}
                    </a>
                  ) : (
                    item.source.name
                  )}
                </p>
                <p className="text-[var(--color-muted)]">
                  Wartość: {String(item.value)} · Sprawdzono: {formatDate(item.retrieved_at)}
                  {item.source.license ? ` · Licencja: ${item.source.license}` : ""}
                </p>
              </li>
            ))}
          </ul>
        </details>
      ) : (
        <p className="mt-2 text-sm text-[var(--color-muted)]">
          Żadne źródło nie zawiera tej informacji.
        </p>
      )}
    </li>
  );
}

export function FeatureGroup({
  title,
  features
}: {
  title: string;
  features: Array<{ label: string; feature: AccessibilityFeature }>;
}) {
  return (
    <section className="mt-8">
      <h2 className="kr-card-blue px-4 py-3 text-xl font-bold">{title}</h2>
      <ul className="kr-card border-t-0">
        {features.map(({ label, feature }) => (
          <FeatureRow key={feature.key} label={label} feature={feature} />
        ))}
      </ul>
    </section>
  );
}
