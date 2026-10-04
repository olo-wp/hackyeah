import { notFound } from "next/navigation";
import { Suspense } from "react";
import { Breadcrumbs } from "@/components/Breadcrumbs";
import { CommunityContributions } from "@/components/CommunityContributions";
import { SearchForm } from "@/components/SearchForm";
import { SearchResults } from "@/components/SearchResults";
import { SearchResultsLoading } from "@/components/SearchResultsLoading";
import { getDictionary } from "@/i18n";
import { isLocale } from "@/i18n/config";
import { getCommunitySummary, getPlace } from "@/lib/api";
import type { CommunitySummary } from "@/lib/types";

type SearchParams = Promise<Record<string, string | string[] | undefined>>;

function readString(params: Awaited<SearchParams>, key: string): string | undefined {
  const value = params[key];
  return typeof value === "string" ? value : undefined;
}

export default async function ContributePage({
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
  const placeId = readString(resolved, "place");
  const hasQuery = query.length >= 2;
  const basePath = `/${locale}/contribute`;

  let selected: { id: string; name: string; summary: CommunitySummary } | null = null;
  let selectionFailed = false;
  if (placeId) {
    const id = decodeURIComponent(placeId);
    const [place, summary] = await Promise.allSettled([
      getPlace(id),
      getCommunitySummary(id)
    ]);
    if (place.status === "fulfilled" && summary.status === "fulfilled") {
      selected = { id, name: place.value.name, summary: summary.value };
    } else {
      selectionFailed = true;
    }
  }

  const crumbs = selected
    ? [{ href: basePath, label: dict.nav.contribute }, { label: selected.name }]
    : [{ label: dict.nav.contribute }];

  return (
    <>
      <Breadcrumbs locale={locale} labels={dict.breadcrumbs} items={crumbs} />

      <header className="mt-6">
        <h1 className="kr-heading text-3xl sm:text-4xl">{dict.community.heading}</h1>
        <p className="mt-3 max-w-3xl text-lg">{dict.community.intro}</p>
      </header>

      <div className="mt-8">
        <SearchForm
          locale={locale}
          dict={dict}
          defaultQuery={selected ? "" : query}
          basePath={basePath}
          showPreferences={false}
        />
      </div>

      {selected ? (
        <CommunityContributions
          locale={locale}
          placeId={selected.id}
          summary={selected.summary}
          dict={dict}
          title={selected.name}
        />
      ) : selectionFailed ? (
        <p className="mt-8 border-l-4 border-[#8a4b00] bg-[#fdf0e0] px-4 py-3 text-[#8a4b00]">
          {dict.community.notFound}
        </p>
      ) : hasQuery ? (
        <section className="mt-8" aria-live="polite">
          <h2 className="kr-card-blue px-4 py-3 text-xl font-bold">{dict.home.resultsHeading}</h2>
          <div className="kr-card border-t-0">
            <Suspense key={query} fallback={<SearchResultsLoading dict={dict} />}>
              <SearchResults
                query={query}
                locale={locale}
                dict={dict}
                preferences=""
                hrefForPlace={(id) => `${basePath}?place=${encodeURIComponent(id)}`}
                linkLabel={dict.community.answerCta}
              />
            </Suspense>
          </div>
        </section>
      ) : (
        <p className="mt-8 kr-card px-4 py-4 text-[var(--color-muted)]">
          {dict.community.selectPrompt}
        </p>
      )}
    </>
  );
}
