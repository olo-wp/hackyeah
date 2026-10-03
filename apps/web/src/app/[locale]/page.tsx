import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { SearchForm } from "@/components/SearchForm";
import { format, getDictionary } from "@/i18n";
import { isLocale } from "@/i18n/config";
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

export default async function HomePage({
  params,
  searchParams
}: {
  params: Promise<{ locale: string }>;
  searchParams: SearchParams;
}) {
  const { locale } = await params;
  if (!isLocale(locale)) notFound();

  const dict = getDictionary(locale);
  const resolved = await searchParams;
  const query = readString(resolved, "q")?.trim() ?? "";

  let result: PlaceSearchResult | null = null;
  let error: string | null = null;

  if (query.length >= 2) {
    try {
      result = await searchPlaces(query);
    } catch (cause) {
      error =
        cause instanceof ApiError
          ? format(dict.home.errorStatus, { status: cause.status })
          : dict.home.errorConnection;
    }
  }

  const preferences = preferenceQuery(resolved);
  const placeHref = (id: string) =>
    `/${locale}/places/${encodeURIComponent(id)}${preferences ? `?${preferences}` : ""}`;

  const legend = [
    { icon: "✓", ...dict.home.legend.confirmed },
    { icon: "?", ...dict.home.legend.unknown },
    { icon: "⚠", ...dict.home.legend.conflicting },
    { icon: "◷", ...dict.home.legend.stale }
  ];

  const sourceCards = [
    dict.home.sourceCards.osm,
    dict.home.sourceCards.krakow,
    dict.home.sourceCards.website
  ];

  return (
    <>
      <section className="kr-card flex flex-col items-center gap-6 p-6 sm:flex-row sm:p-8">
        <Image
          src="/logo.png"
          alt={dict.common.logoAlt}
          width={200}
          height={200}
          priority
          className="kr-keep-colour shrink-0"
        />
        <div>
          <h1 className="kr-heading text-3xl sm:text-4xl">{dict.home.title}</h1>
          <p className="mt-3 max-w-3xl text-lg">{dict.home.lead}</p>
        </div>
      </section>

      <div className="mt-8">
        <SearchForm locale={locale} dict={dict} defaultQuery={query} />
      </div>

      <section className="mt-8" aria-live="polite">
        <h2 className="kr-card-blue px-4 py-3 text-xl font-bold">{dict.home.resultsHeading}</h2>

        <div className="kr-card border-t-0">
          {error ? (
            <p className="border-l-4 border-[#8a4b00] bg-[#fdf0e0] px-4 py-3 text-[#8a4b00]">
              {error}
            </p>
          ) : null}

          {!error && query.length < 2 ? (
            <p className="px-4 py-4 text-[var(--color-muted)]">{dict.home.emptyPrompt}</p>
          ) : null}

          {result && result.results.length === 0 ? (
            <p className="px-4 py-4 text-[var(--color-muted)]">
              {format(dict.home.noResults, { query })}
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
                  {dict.categories[place.category] ?? place.category}
                  {place.address ? ` · ${place.address}` : ""}
                </p>
                <Link
                  href={placeHref(place.id)}
                  className="link-kr mt-2 inline-block text-sm font-bold"
                >
                  {dict.home.showDetails}
                  <span aria-hidden="true"> ▷</span>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section id="jak-to-dziala" className="mt-12">
        <h2 className="kr-heading text-3xl">{dict.home.legendHeading}</h2>
        <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {legend.map((item) => (
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
          <strong>{dict.home.unknownNoticeStrong}</strong> {dict.home.unknownNoticeRest}
        </p>
      </section>

      <section id="zrodla" className="mt-12">
        <h2 className="kr-heading text-3xl">{dict.home.sourcesHeading}</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          {sourceCards.map((source) => (
            <div key={source.name} className="kr-card-blue p-5">
              <h3 className="text-lg font-bold">{source.name}</h3>
              <p className="mt-2 text-sm">{source.text}</p>
              <p className="mt-3 text-sm font-bold">
                {dict.home.licensePrefix} {source.license}
              </p>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
