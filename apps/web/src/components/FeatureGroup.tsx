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

export function FeatureRow({ label, feature }: { label: string; feature: AccessibilityFeature }) {
  const sources = [...new Set(feature.evidence.map((item) => item.source.name))];

  return (
    <li className="border-b border-slate-200 py-3">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h3 className="font-medium">{label}</h3>
        <StatusBadge status={feature.status} />
      </div>

      <p className="mt-1">{renderValue(feature)}</p>

      {feature.conflict_reason ? (
        <p className="mt-1 text-sm text-slate-700">{feature.conflict_reason}</p>
      ) : null}

      <p className="mt-1 text-sm text-slate-600">
        {feature.confidence ? `Wiarygodność: ${CONFIDENCE_LABEL[feature.confidence]}. ` : ""}
        {sources.length > 0 ? `Źródła: ${sources.join(", ")}.` : "Brak źródeł."}
      </p>
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
    <section className="mt-6">
      <h2 className="text-lg font-semibold">{title}</h2>
      <ul className="mt-2">
        {features.map(({ label, feature }) => (
          <FeatureRow key={feature.key} label={label} feature={feature} />
        ))}
      </ul>
    </section>
  );
}
