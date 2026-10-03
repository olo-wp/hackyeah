import type { Metadata } from "next";
import { Lato } from "next/font/google";
import { notFound } from "next/navigation";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { getDictionary } from "@/i18n";
import { LOCALES, isLocale } from "@/i18n/config";
import "../globals.css";

const lato = Lato({
  subsets: ["latin", "latin-ext"],
  weight: ["400", "700", "900"],
  variable: "--font-lato",
  display: "swap"
});

export function generateStaticParams() {
  return LOCALES.map((locale) => ({ locale }));
}

export async function generateMetadata({
  params
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  if (!isLocale(locale)) return {};

  const dict = getDictionary(locale);
  return { title: dict.metadata.title, description: dict.metadata.description };
}

// Applied before paint so saved contrast/font-size settings never flash.
const RESTORE_PREFERENCES = `
try {
  var root = document.documentElement;
  root.dataset.fontSize = localStorage.getItem('routeable:font-size') || 'sm';
  root.dataset.contrast = localStorage.getItem('routeable:contrast') || 'normal';
} catch (e) {}
`;

export default async function LocaleLayout({
  children,
  params
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  if (!isLocale(locale)) notFound();

  const dict = getDictionary(locale);

  return (
    <html lang={locale} className={lato.variable} data-font-size="sm" data-contrast="normal">
      <body className="font-sans">
        <script dangerouslySetInnerHTML={{ __html: RESTORE_PREFERENCES }} />

        <a className="skip-link" href="#main">
          {dict.common.skipToContent}
        </a>

        <SiteHeader locale={locale} dict={dict} />

        <main id="main" className="container-kr py-6">
          {children}
        </main>

        <SiteFooter locale={locale} dict={dict} />
      </body>
    </html>
  );
}
