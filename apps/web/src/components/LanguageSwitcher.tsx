"use client";

import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";
import { LOCALES, type Locale } from "@/i18n/config";

export function LanguageSwitcher({
  current,
  groupLabel,
  names
}: {
  current: Locale;
  groupLabel: string;
  names: Record<Locale, string>;
}) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const query = searchParams.toString();

  // Swaps the /<locale>/ segment while keeping the rest of the URL intact.
  const hrefFor = (locale: Locale) => {
    const segments = pathname.split("/");
    segments[1] = locale;
    return `${segments.join("/")}${query ? `?${query}` : ""}`;
  };

  return (
    <div role="group" aria-label={groupLabel} className="flex items-center gap-1">
      {LOCALES.map((locale) => {
        const active = locale === current;
        return (
          <Link
            key={locale}
            href={hrefFor(locale)}
            hrefLang={locale}
            aria-current={active ? "true" : undefined}
            className={`border-2 px-3 py-1 text-sm font-bold uppercase ${
              active
                ? "border-white bg-white text-[#0063af]"
                : "border-transparent hover:border-white"
            }`}
          >
            <span aria-hidden="true">{locale}</span>
            <span className="sr-only">{names[locale]}</span>
          </Link>
        );
      })}
    </div>
  );
}
