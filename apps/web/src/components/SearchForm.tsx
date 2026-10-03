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
  defaultQuery = ""
}: {
  locale: Locale;
  dict: Dictionary;
  defaultQuery?: string;
}) {
  return (
    <form action={`/${locale}`} method="get" className="kr-card p-6">
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
    </form>
  );
}
