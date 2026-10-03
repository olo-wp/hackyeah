import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "RouteAble — dostępność miejsc w Krakowie",
  description:
    "Konkretne informacje o barierach i udogodnieniach, wraz ze źródłami i poziomem wiarygodności."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pl">
      <body>
        <a className="skip-link" href="#main">
          Przejdź do treści
        </a>

        <header className="border-b border-slate-200">
          <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-4">
            <Link href="/" className="text-xl font-bold">
              RouteAble
            </Link>
            <p className="text-sm text-slate-600">Kraków bez barier</p>
          </div>
        </header>

        <main id="main" className="mx-auto max-w-4xl px-4 py-8">
          {children}
        </main>

        <footer className="mx-auto max-w-4xl px-4 py-8 text-sm text-slate-600">
          <p>
            Brak danych nie oznacza dostępności. Każda informacja pokazuje źródło, datę
            sprawdzenia i poziom wiarygodności.
          </p>
        </footer>
      </body>
    </html>
  );
}
