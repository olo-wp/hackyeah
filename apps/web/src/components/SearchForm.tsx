"use client";

import { useRouter } from "next/navigation";
import type { FormEvent } from "react";
import type { Locale } from "@/i18n/config";
import type { Dictionary } from "@/i18n";

const PREFERENCE_KEYS = [
  "step_free_required",
  "elevator_required",
  "accessible_toilet_required",
  "avoid_cobblestone"
] as const;

export function SearchForm({
  locale,
  dict,
  defaultQuery = "",
  basePath,
  showPreferences = true
}: {
  locale: Locale;
  dict: Dictionary;
  defaultQuery?: string;
  basePath?: string;
  showPreferences?: boolean;
}) {
  const router = useRouter();
  const target = basePath ?? `/${locale}`;

  // A native GET submit reloads the route and resets the scroll position, so
  // navigate through the router instead. The plain `action` stays as a no-JS fallback.
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const query = String(data.get("q") ?? "").trim();
    if (query.length < 2) return;

    const params = new URLSearchParams({ q: query });
    if (showPreferences) {
      for (const key of PREFERENCE_KEYS) {
        if (data.get(key) === "true") params.set(key, "true");
      }
    }
    router.push(`${target}?${params.toString()}`, { scroll: false });
  }

  return (
    <form
      action={target}
      method="get"
      onSubmit={handleSubmit}
      className="kr-card p-6"
    >
      <div>
        <label htmlFor="q" className="block text-lg font-bold">
          {dict.search.label}
        </label>
        <div className="mt-2 flex flex-wrap gap-2">
          <input
            id="q"
            name="q"
            type="search"
            required
            minLength={2}
            defaultValue={defaultQuery}
            placeholder={dict.search.placeholder}
            className="min-w-0 flex-1 border-2 border-[var(--color-rule)] px-3 py-2.5 text-lg focus:border-[#0064b6]"
          />
          <button type="submit" className="kr-btn">
            {dict.search.submit}
          </button>
        </div>
      </div>

      {showPreferences ? (
        <fieldset className="mt-6">
          <legend className="text-lg font-bold">{dict.search.requirementsLegend}</legend>
          <div className="mt-3 grid gap-3 sm:grid-cols-2">
            {PREFERENCE_KEYS.map((key) => (
              <div key={key} className="flex items-center gap-3">
                <input
                  id={key}
                  name={key}
                  type="checkbox"
                  value="true"
                  className="h-5 w-5 accent-[#0064b6]"
                />
                <label htmlFor={key}>{dict.search.preferences[key]}</label>
              </div>
            ))}
          </div>
          <p className="mt-3 text-sm text-[var(--color-muted)]">{dict.search.requirementsHint}</p>
        </fieldset>
      ) : null}
    </form>
  );
}
