import Link from "next/link";
import { format, type Dictionary } from "@/i18n";
import type { Locale } from "@/i18n/config";
import { ApiError, searchPlaces } from "@/lib/api";
import type { PlaceSearchResult } from "@/lib/types";

/** Async server component so the page can stream a loading state around it. */
export async function SearchResults({
  query,
  locale,
  dict,
  preferences,
  hrefForPlace,
  linkLabel
}: {
  query: string;
  locale: Locale;
  dict: Dictionary;
  preferences: string;
  hrefForPlace?: (id: string) => string;
  linkLabel?: string;
}) {
  let result: PlaceSearchResult | null = null;
  let error: string | null = null;

  try {
    result = await searchPlaces(query);
  } catch (cause) {
    error =
      cause instanceof ApiError
        ? format(dict.home.errorStatus, { status: cause.status })
        : dict.home.errorConnection;
  }

  if (error) {
    return (
      <p className="border-l-4 border-[#8a4b00] bg-[#fdf0e0] px-4 py-3 text-[#8a4b00]">{error}</p>
    );
  }

  if (!result || result.results.length === 0) {
    return (
      <p className="px-4 py-4 text-[var(--color-muted)]">
        {format(dict.home.noResults, { query })}
      </p>
    );
  }

  const placeHref =
    hrefForPlace ??
    ((id: string) =>
      `/${locale}/places/${encodeURIComponent(id)}${preferences ? `?${preferences}` : ""}`);
  const detailsLabel = linkLabel ?? dict.home.showDetails;

  return (
    <ul>
      {result.results.map((place) => (
        <li key={place.id} className="border-b border-[var(--color-rule)] px-4 py-4 last:border-b-0">
          <h3 className="text-lg font-bold">
            <Link href={placeHref(place.id)} className="link-kr">
              {place.name}
            </Link>
          </h3>
          <p className="text-sm text-[var(--color-muted)]">
            {dict.categories[place.category] ?? place.category}
            {place.address ? ` · ${place.address}` : ""}
          </p>
          <Link href={placeHref(place.id)} className="link-kr mt-2 inline-block text-sm font-bold">
            {detailsLabel}
            <span aria-hidden="true"> ▷</span>
          </Link>
        </li>
      ))}
    </ul>
  );
}
