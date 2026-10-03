import Image from "next/image";
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

const STATUS_LEGEND = [
  { icon: "✓", title: "Potwierdzone", text: "Co najmniej jedno źródło potwierdza informację." },
  { icon: "?", title: "Brak danych", text: "Żadne źródło nie zawiera tej informacji." },
  { icon: "⚠", title: "Dane sprzeczne", text: "Źródła podają różne informacje." },
  { icon: "◷", title: "Możliwe nieaktualne", text: "Informacja nie była dawno sprawdzana." }
];

const SOURCES = [
  {
    name: "OpenStreetMap",
    text: "Lokalizacje, wejścia, windy, nawierzchnie i tagi dostępności.",
    license: "ODbL 1.0"
  },
  {
    name: "Otwarte Dane Miasta Krakowa",
    text: "Miejskie zbiory danych o obiektach publicznych.",
    license: "CC BY 4.0"
  },
  {
    name: "Oficjalne strony obiektów",
    text: "Deklaracje dostępności — wyłącznie z domen na liście dozwolonych.",
    license: "warunki danego serwisu"
  }
];

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
  const placeHref = (id: string) =>
    `/places/${encodeURIComponent(id)}${preferences ? `?${preferences}` : ""}`;

  return (
    <>
      <section className="kr-card flex flex-col items-center gap-6 p-6 sm:flex-row sm:p-8">
        <Image
          src="/logo.png"
          alt="Logo RouteAble — smok na wózku na tle panoramy Krakowa"
          width={200}
          height={200}
          priority
          className="kr-keep-colour shrink-0"
        />
        <div>
          <h1 className="kr-heading text-3xl sm:text-4xl">
            Sprawdź dostępność miejsca w Krakowie
          </h1>
          <p className="mt-3 max-w-3xl text-lg">
            RouteAble nie ocenia miejsca jako „dostępne” lub „niedostępne”. Pokazuje konkretne
            bariery i udogodnienia, a przy każdej informacji źródło, datę sprawdzenia i poziom
            wiarygodności — decyzję podejmujesz samodzielnie.
          </p>
        </div>
      </section>

      <div className="mt-8">
        <SearchForm defaultQuery={query} />
      </div>

      <section className="mt-8" aria-live="polite">
        <h2 className="kr-card-blue px-4 py-3 text-xl font-bold">Wyniki wyszukiwania</h2>

        <div className="kr-card border-t-0">
          {error ? (
            <p className="border-l-4 border-[#8a4b00] bg-[#fdf0e0] px-4 py-3 text-[#8a4b00]">
              {error}
            </p>
          ) : null}

          {!error && query.length < 2 ? (
            <p className="px-4 py-4 text-[var(--color-muted)]">
              Wpisz nazwę miejsca, aby rozpocząć wyszukiwanie.
            </p>
          ) : null}

          {result && result.results.length === 0 ? (
            <p className="px-4 py-4 text-[var(--color-muted)]">
              Nie znaleziono miejsc dla zapytania „{query}”.
            </p>
          ) : null}

          <ul>
            {result?.results.map((place) => (
              <li
                key={place.id}
                className="border-b border-[var(--color-rule)] px-4 py-4 last:border-b-0"
              >
                <h3 className="text-lg font-bold">
                  <Link href={placeHref(place.id)} className="link-kr">
                    {place.name}
                  </Link>
                </h3>
                <p className="text-sm text-[var(--color-muted)]">
                  {place.category}
                  {place.address ? ` · ${place.address}` : ""}
                </p>
                <Link href={placeHref(place.id)} className="link-kr mt-2 inline-block text-sm font-bold">
                  Pokaż szczegóły dostępności
                  <span aria-hidden="true"> ▷</span>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section id="jak-to-dziala" className="mt-12">
        <h2 className="kr-heading text-3xl">Jak czytać informacje</h2>
        <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {STATUS_LEGEND.map((item) => (
            <div key={item.title} className="kr-card p-4">
              <p className="text-3xl font-bold text-[#0063af]" aria-hidden="true">
                {item.icon}
              </p>
              <h3 className="mt-1 text-lg font-bold">{item.title}</h3>
              <p className="mt-1 text-sm text-[var(--color-muted)]">{item.text}</p>
            </div>
          ))}
        </div>
        <p className="mt-4 border-l-4 border-[#0063af] bg-[#e8f1f8] px-4 py-3">
          <strong>Brak danych nie oznacza dostępności.</strong> Jeżeli źródła się nie zgadzają,
          pokazujemy obie wersje zamiast wybierać jedną za Ciebie.
        </p>
      </section>

      <section id="zrodla" className="mt-12">
        <h2 className="kr-heading text-3xl">Źródła danych</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          {SOURCES.map((source) => (
            <div key={source.name} className="kr-card-blue p-5">
              <h3 className="text-lg font-bold">{source.name}</h3>
              <p className="mt-2 text-sm">{source.text}</p>
              <p className="mt-3 text-sm font-bold">Licencja: {source.license}</p>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
