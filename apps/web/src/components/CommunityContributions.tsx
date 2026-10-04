"use client";

import { useEffect, useId, useState, useTransition } from "react";
import type { Dictionary } from "@/i18n";
import { submitCommunityContribution } from "@/lib/actions";
import { communityChoices, communityValueKey } from "@/lib/community";
import type { CommunityFeatureSummary, CommunitySummary } from "@/lib/types";

function CommunityQuestion({
  locale,
  placeId,
  feature,
  dict
}: {
  locale: string;
  placeId: string;
  feature: CommunityFeatureSummary;
  dict: Dictionary;
}) {
  const c = dict.community;
  const choices = communityChoices(feature.feature_key, dict);
  const [selected, setSelected] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [isError, setIsError] = useState(false);
  const [answered, setAnswered] = useState(false);
  const [isPending, startTransition] = useTransition();

  const topKey = feature.top_value !== null ? communityValueKey(feature.top_value) : null;
  const groupName = useId();
  // One answer per browser session, kept anonymous (no server-side identity).
  const storageKey = `routeable:community:${placeId}:${feature.feature_key}`;

  useEffect(() => {
    setAnswered(sessionStorage.getItem(storageKey) !== null);
  }, [storageKey]);

  function handleSubmit() {
    const choice = choices.find((item) => item.key === selected);
    if (!choice) return;
    startTransition(async () => {
      try {
        await submitCommunityContribution(locale, placeId, feature.feature_key, choice.value);
        sessionStorage.setItem(storageKey, choice.key);
        setIsError(false);
        setStatus(c.success);
        setSelected(null);
        setAnswered(true);
      } catch {
        setIsError(true);
        setStatus(c.error);
      }
    });
  }

  return (
    <fieldset className="kr-card border-t-0 px-4 py-4">
      <legend className="text-lg font-bold">{dict.features[feature.feature_key]}</legend>

      <div
        role="radiogroup"
        aria-label={dict.features[feature.feature_key]}
        className="mt-2 flex flex-wrap gap-x-6 gap-y-2"
      >
        {choices.map((choice) => (
          <label key={choice.key} className="inline-flex items-center gap-2">
            <input
              type="radio"
              name={groupName}
              value={choice.key}
              checked={selected === choice.key}
              onChange={() => setSelected(choice.key)}
              disabled={isPending || answered}
              className="h-5 w-5 accent-[#0064b6]"
            />
            <span>{choice.label}</span>
          </label>
        ))}
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-4">
        <button
          type="button"
          onClick={handleSubmit}
          disabled={selected === null || isPending || answered}
          className="kr-btn disabled:opacity-50"
        >
          {isPending ? c.submitting : c.submit}
        </button>
        <span className="text-sm text-[var(--color-muted)]">
          {c.responses}: {feature.total_responses}
        </span>
      </div>

      {answered ? (
        <p className="mt-2 text-sm text-[var(--color-muted)]">{c.alreadyAnswered}</p>
      ) : null}

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
                {isTop ? ` · ${c.topBadge}` : ""}
              </li>
            );
          })}
        </ul>
      ) : (
        <p className="mt-3 text-sm text-[var(--color-muted)]">{c.noResponses}</p>
      )}

      <p
        role="status"
        aria-live="polite"
        className={`mt-2 min-h-[1.25rem] text-sm ${isError ? "text-[#8a4b00]" : "text-[#1b5e20]"}`}
      >
        {status ?? ""}
      </p>
    </fieldset>
  );
}

export function CommunityContributions({
  locale,
  placeId,
  summary,
  dict,
  title
}: {
  locale: string;
  placeId: string;
  summary: CommunitySummary;
  dict: Dictionary;
  title: string;
}) {
  return (
    <section className="mt-8">
      <h2 className="kr-card-blue px-4 py-3 text-xl font-bold">{title}</h2>
      <div className="mt-px space-y-px">
        {summary.features.map((feature) => (
          <CommunityQuestion
            key={feature.feature_key}
            locale={locale}
            placeId={placeId}
            feature={feature}
            dict={dict}
          />
        ))}
      </div>
    </section>
  );
}
