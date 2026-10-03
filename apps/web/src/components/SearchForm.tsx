const PREFERENCES = [
  { name: "step_free_required", label: "Potrzebuję wejścia bez schodów" },
  { name: "elevator_required", label: "Potrzebuję windy" },
  { name: "accessible_toilet_required", label: "Potrzebuję dostępnej toalety" },
  { name: "avoid_cobblestone", label: "Chcę unikać kostki brukowej" }
] as const;

export function SearchForm({ defaultQuery = "" }: { defaultQuery?: string }) {
  return (
    <form action="/" method="get" className="space-y-4">
      <div>
        <label htmlFor="q" className="block font-medium">
          Gdzie chcesz się dostać?
        </label>
        <input
          id="q"
          name="q"
          type="search"
          required
          minLength={2}
          defaultValue={defaultQuery}
          placeholder="np. Muzeum Narodowe"
          className="mt-1 w-full rounded border border-slate-400 px-3 py-2"
        />
      </div>

      <fieldset className="space-y-2">
        <legend className="font-medium">Twoje wymagania</legend>
        {PREFERENCES.map((preference) => (
          <div key={preference.name} className="flex items-center gap-2">
            <input
              id={preference.name}
              name={preference.name}
              type="checkbox"
              value="true"
              className="h-4 w-4"
            />
            <label htmlFor={preference.name}>{preference.label}</label>
          </div>
        ))}
      </fieldset>

      <button
        type="submit"
        className="rounded bg-blue-700 px-4 py-2 font-medium text-white hover:bg-blue-800"
      >
        Szukaj
      </button>
    </form>
  );
}
