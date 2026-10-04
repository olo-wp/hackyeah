import type { Dictionary } from "@/i18n";
import { communityChoices, communityValueKey } from "@/lib/community";
import type {
  AccessibilityFeature,
  CommunityFeatureKey,
  CommunityFeatureSummary,
  CommunitySummary
} from "@/lib/types";
import { StatusBadge } from "./StatusBadge";

type Surfaces = Dictionary["surfaces"];

function renderValue(feature: AccessibilityFeature, dict: Dictionary): string {
  if (feature.status === "conflicting") return dict.value.needsVerification;
  if (feature.value === null || feature.value === undefined) return dict.value.noData;
  if (typeof feature.value === "boolean") return feature.value ? dict.value.yes : dict.value.no;

  if (feature.key === "surface" && typeof feature.value === "string") {
    return dict.surfaces[feature.value as keyof Surfaces] ?? feature.value;
  }

  return String(feature.value);
}

export function FeatureRow({
  label,
  feature,
  dict,
  community
}: {
  label: string;
  feature: AccessibilityFeature;
  dict: Dictionary;
  community?: CommunityFeatureSummary;
}) {
  const formatDate = (value: string) => new Date(value).toLocaleDateString(dict.localeTag);

  return (
    <li className="border-b border-[var(--color-rule)] px-4 py-4 last:border-b-0">
      <div className="flex flex-wrap items-baseline justify-between gap-3">
        <h3 className="text-lg font-bold">{label}</h3>
        <StatusBadge status={feature.status} labels={dict.status} />
      </div>

      <p className="mt-1 text-lg">{renderValue(feature, dict)}</p>

      {feature.conflict_reason ? (
        <p className="mt-2 border-l-4 border-[#8a4b00] bg-[#fdf0e0] px-3 py-2 text-sm text-[#8a4b00]">
          {feature.conflict_reason}
        </p>
      ) : null}

      {feature.evidence.length > 0 ? (
        <details className="mt-3">
          <summary className="link-kr cursor-pointer text-sm font-bold">
            {dict.place.showSources} ({feature.evidence.length})
            {feature.confidence
              ? ` · ${dict.place.confidencePrefix}: ${dict.confidence[feature.confidence]}`
              : ""}
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
                  {dict.place.evidenceValue}: {String(item.value)} ·{" "}
                  {dict.place.evidenceCheckedAt}: {formatDate(item.retrieved_at)}
                  {item.source.license
                    ? ` · ${dict.place.evidenceLicense}: ${item.source.license}`
                    : ""}
                </p>
              </li>
            ))}
          </ul>
        </details>
      ) : (
        <p className="mt-2 text-sm text-[var(--color-muted)]">{dict.place.noSources}</p>
      )}

      {community && community.total_responses > 0 ? (
        <div className="kr-card mt-3 bg-[#eef1f3] px-3 py-2">
          <p className="text-sm font-bold text-[var(--color-muted)]">
            {dict.community.answersHeading}
          </p>
          <ul className="mt-1 flex flex-wrap gap-2">
            {communityChoices(feature.key as CommunityFeatureKey, dict)
              .filter((choice) => (community.distribution[choice.key] ?? 0) > 0)
              .map((choice) => {
                const isTop =
                  community.top_value !== null &&
                  communityValueKey(community.top_value) === choice.key;
                return (
                  <li
                    key={choice.key}
                    className={`border border-[var(--color-rule)] bg-white px-2 py-0.5 text-sm ${
                      isTop ? "font-bold" : "text-[var(--color-muted)]"
                    }`}
                  >
                    {choice.label}: {community.distribution[choice.key] ?? 0}
                  </li>
                );
              })}
          </ul>
        </div>
      ) : null}
    </li>
  );
}

export function FeatureGroup({
  title,
  features,
  dict,
  community
}: {
  title: string;
  features: Array<{ label: string; feature: AccessibilityFeature }>;
  dict: Dictionary;
  community?: CommunitySummary;
}) {
  return (
    <section className="mt-8">
      <h2 className="kr-card-blue px-4 py-3 text-xl font-bold">{title}</h2>
      <ul className="kr-card border-t-0">
        {features.map(({ label, feature }) => (
          <FeatureRow
            key={feature.key}
            label={label}
            feature={feature}
            dict={dict}
            community={community?.features.find((f) => f.feature_key === feature.key)}
          />
        ))}
      </ul>
    </section>
  );
}
