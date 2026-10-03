import Link from "next/link";
import type { Dictionary } from "@/i18n";
import type {
  CommunityFeatureKey,
  CommunitySummary,
  CommunityValue,
  DoorstepLevel
} from "@/lib/types";

type CommunityDict = Dictionary["community"];

const DOORSTEP_LEVELS: DoorstepLevel[] = ["none", "small", "high"];

function choiceLabels(featureKey: CommunityFeatureKey, dict: CommunityDict): {
  key: string;
  label: string;
}[] {
  if (featureKey === "doorstep") {
    return DOORSTEP_LEVELS.map((level) => ({ key: level, label: dict.doorstepLevels[level] }));
  }
  return [
    { key: "true", label: dict.answers.yes },
    { key: "false", label: dict.answers.no }
  ];
}

function valueKey(value: CommunityValue): string {
  if (typeof value === "boolean") return value ? "true" : "false";
  return value;
}

/** Read-only tally of community answers shown on the place page. */
export function CommunityAnswers({
  locale,
  placeId,
  summary,
  dict
}: {
  locale: string;
  placeId: string;
  summary: CommunitySummary;
  dict: CommunityDict;
}) {
  return (
    <section className="mt-8">
      <h2 className="kr-card-blue px-4 py-3 text-xl font-bold">{dict.answersHeading}</h2>
      <p className="kr-card border-t-0 px-4 py-3 text-sm text-[var(--color-muted)]">{dict.intro}</p>

      <div className="mt-px space-y-px">
        {summary.features.map((feature) => {
          const choices = choiceLabels(feature.feature_key, dict);
          const topKey = feature.top_value !== null ? valueKey(feature.top_value) : null;
          return (
            <div key={feature.feature_key} className="kr-card border-t-0 px-4 py-4">
              <h3 className="text-lg font-bold">{dict.features[feature.feature_key]}</h3>
              <p className="mt-1 text-sm text-[var(--color-muted)]">
                {dict.responses}: {feature.total_responses}
              </p>

              {feature.total_responses > 0 ? (
                <ul className="mt-3 flex flex-wrap gap-2">
                  {choices.map((choice) => {
                    const count = feature.distribution[choice.key] ?? 0;
                    const isTop = topKey === choice.key;
                    return (
                      <li
                        key={choice.key}
                        className={`border-2 border-[var(--color-rule)] px-2 py-0.5 text-sm ${
                          isTop ? "font-bold" : ""
                        }`}
                      >
                        {choice.label}: {count}
                        {isTop ? ` · ${dict.topBadge}` : ""}
                      </li>
                    );
                  })}
                </ul>
              ) : (
                <p className="mt-3 text-sm text-[var(--color-muted)]">{dict.noResponses}</p>
              )}
            </div>
          );
        })}
      </div>

      <div className="mt-4">
        <Link
          href={`/${locale}/contribute?place=${encodeURIComponent(placeId)}`}
          className="kr-btn inline-block"
        >
          {dict.heading}
        </Link>
      </div>
    </section>
  );
}
