import Link from "next/link";
import type { Locale } from "@/i18n/config";

export interface Crumb {
  href?: string;
  label: string;
}

export function Breadcrumbs({
  items,
  locale,
  labels
}: {
  items: Crumb[];
  locale: Locale;
  labels: { label: string; home: string };
}) {
  return (
    <nav aria-label={labels.label} className="border-b border-[var(--color-rule)] py-3">
      <ol className="flex flex-wrap items-center gap-2 text-sm">
        <li>
          <Link href={`/${locale}`} className="link-kr">
            <span aria-hidden="true">⌂ </span>
            {labels.home}
          </Link>
        </li>
        {items.map((item) => (
          <li key={item.label} className="flex items-center gap-2">
            <span aria-hidden="true" className="text-[var(--color-muted)]">
              ▷
            </span>
            {item.href ? (
              <Link href={item.href} className="link-kr">
                {item.label}
              </Link>
            ) : (
              <span aria-current="page">{item.label}</span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}
