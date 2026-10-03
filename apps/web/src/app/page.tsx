import Link from "next/link";
import { SearchForm } from "@/components/SearchForm";
import { ApiError, searchPlaces } from "@/lib/api";
import type { PlaceSearchResult } from "@/lib/types";

type SearchParams = Promise<Record<string, string | string[] | undefined>>;

const PREFERENCE_KEYS = [
  "step_free_required",
  "elevator_required",
  "accessible_toilet_required",
  "avoid_cobblestone"
] as const;

function readString(params: Awaited<SearchParams>, key: string): string | undefined {
  const value = params[key];
  return typeof value === "string" ? value : undefined;
}

function preferenceQuery(params: Awaited<SearchParams>): string {
  const query = new URLSearchParams();
  for (const key of PREFERENCE_KEYS) {
    if (readString(params, key) === "true") query.set(key, "true");
  }
  return query.toString();
}

export default async function HomePage({ searchParams }: { searchParams: SearchParams }) {
  const params = await searchParams;
  const query = readString(params, "q")?.trim() ?? "";

  let result: PlaceSearchResult | null = null;
  let error: string | null = null;

  if (query.length >= 2) {
    try {
      result = await searchPlaces(query);
    } catch (cause) {
      error =
        cause instanceof ApiError
          ? `Nie udało się pobrać wyników (${cause.status}).`
          : "Nie udało się połączyć z API.";
    }
  }

  const preferences = preferenceQuery(params);

  return (
    <>
      <h1 className="text-2xl font-bold">Sprawdź dostępność miejsca</h1>
      <p className="mt-2 text-slate-700">
        RouteAble nie ocenia miejsca jako „dostępne” lub „niedostępne”. Pokazuje konkretne
        bariery i udogodnienia wraz ze źródłami.
      </p>

      <div className="mt-6">
        <SearchForm defaultQuery={query} />
      </div>

      <section className="mt-8" aria-live="polite">
        <h2 className="text-lg font-semibold">Wyniki</h2>

        {error ? <p className="mt-2 text-red-700">{error}</p> : null}

        {!error && query.length < 2 ? (
          <p className="mt-2 text-slate-700">Wpisz nazwę miejsca, aby rozpocząć wyszukiwanie.</p>
        ) : null}

        {result && result.results.length === 0 ? (
          <p className="mt-2 text-slate-700">Nie znaleziono miejsc dla zapytania „{query}”.</p>
        ) : null}

        <ul className="mt-2">
          {result?.results.map((place) => (
            <li key={place.id} className="border-b border-slate-200 py-3">
              <Link
                href={`/places/${encodeURIComponent(place.id)}${preferences ? `?${preferences}` : ""}`}
                className="font-medium text-blue-800 underline"
              >
                {place.name}
              </Link>
              <p className="text-sm text-slate-600">
                {place.category}
                {place.address ? ` · ${place.address}` : ""}
              </p>
            </li>
          ))}
        </ul>
      </section>
    </>
  );
}
