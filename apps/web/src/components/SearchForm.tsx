const PREFERENCES = [
  { name: "step_free_required", label: "Potrzebuję wejścia bez schodów" },
  { name: "elevator_required", label: "Potrzebuję windy" },
  { name: "accessible_toilet_required", label: "Potrzebuję dostępnej toalety" },
  { name: "avoid_cobblestone", label: "Chcę unikać kostki brukowej" }
] as const;

export function SearchForm({ defaultQuery = "" }: { defaultQuery?: string }) {
  return (
    <form action="/" method="get" className="kr-card p-6">
      <div>
        <label htmlFor="q" className="block text-lg font-bold">
          Gdzie chcesz się dostać?
        </label>
        <div className="mt-2 flex flex-wrap gap-2">
          <input
            id="q"
            name="q"
            type="search"
            required
            minLength={2}
            defaultValue={defaultQuery}
            placeholder="np. Muzeum Narodowe"
            className="min-w-0 flex-1 border-2 border-[var(--color-rule)] px-3 py-2.5 text-lg focus:border-[#0063af]"
          />
          <button type="submit" className="kr-btn">
            Szukaj
          </button>
        </div>
      </div>

      <fieldset className="mt-6">
        <legend className="text-lg font-bold">Twoje wymagania</legend>
        <p className="mt-1 text-sm text-[var(--color-muted)]">
          Wymagania służą wyłącznie do wyróżnienia istotnych informacji. RouteAble nie
          odrzuca na ich podstawie żadnego miejsca.
        </p>
        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          {PREFERENCES.map((preference) => (
            <div key={preference.name} className="flex items-center gap-3">
              <input
                id={preference.name}
                name={preference.name}
                type="checkbox"
                value="true"
                className="h-5 w-5 accent-[#0063af]"
              />
              <label htmlFor={preference.name}>{preference.label}</label>
            </div>
          ))}
        </div>
      </fieldset>
    </form>
  );
}
