import Image from "next/image";
import Link from "next/link";
import { Suspense } from "react";
import type { Locale } from "@/i18n/config";
import type { Dictionary } from "@/i18n";
import { AccessibilityToolbar } from "./AccessibilityToolbar";
import { LanguageSwitcher } from "./LanguageSwitcher";

export function SiteHeader({ locale, dict }: { locale: Locale; dict: Dictionary }) {
  const nav = [
    { href: `/${locale}`, label: dict.nav.search },
    { href: `/${locale}#jak-to-dziala`, label: dict.nav.howItWorks },
    { href: `/${locale}#zrodla`, label: dict.nav.sources }
  ];

  return (
    <header className="kr-band">
      <div className="container-kr">
        <div className="flex flex-col items-center gap-3 pt-5 sm:flex-row sm:justify-center">
          <Link href={`/${locale}`} className="flex items-center gap-4">
            <Image
              src="/krakow-logo.png"
              alt={dict.common.krakowLogoAlt}
              width={180}
              height={60}
              priority
              className="kr-keep-colour h-12 w-auto sm:h-14"
            />
            <span className="h-12 w-px bg-white/50" aria-hidden="true" />
            <span className="text-left">
              <span className="block text-2xl font-bold leading-tight sm:text-3xl">
                {dict.common.siteName}
              </span>
              <span className="block text-sm">{dict.common.tagline}</span>
            </span>
          </Link>
        </div>

        <nav aria-label={dict.nav.label} className="mt-4">
          <ul className="flex flex-wrap items-center justify-center gap-x-8 gap-y-2">
            {nav.map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className="inline-block border-b-2 border-transparent py-1 font-bold hover:border-white"
                >
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        <div className="flex flex-wrap items-center justify-center gap-4 py-2">
          <AccessibilityToolbar labels={dict.a11y} />
          <Suspense fallback={null}>
            <LanguageSwitcher
              current={locale}
              groupLabel={dict.a11y.languageGroup}
              names={{ pl: "Polski", en: "English" }}
            />
          </Suspense>
        </div>
      </div>
    </header>
  );
}
