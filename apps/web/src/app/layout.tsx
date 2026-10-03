import type { Metadata } from "next";
import { Lato } from "next/font/google";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import "./globals.css";

const lato = Lato({
  subsets: ["latin", "latin-ext"],
  weight: ["400", "700", "900"],
  variable: "--font-lato",
  display: "swap"
});

export const metadata: Metadata = {
  title: "RouteAble — Kraków bez barier",
  description:
    "Konkretne informacje o barierach i udogodnieniach w Krakowie, wraz ze źródłami, datą sprawdzenia i poziomem wiarygodności."
};

// Applied before paint so saved contrast/font-size settings never flash.
const RESTORE_PREFERENCES = `
try {
  var root = document.documentElement;
  root.dataset.fontSize = localStorage.getItem('routeable:font-size') || 'sm';
  root.dataset.contrast = localStorage.getItem('routeable:contrast') || 'normal';
} catch (e) {}
`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pl" className={lato.variable} data-font-size="sm" data-contrast="normal">
      <body className="font-sans">
        <script dangerouslySetInnerHTML={{ __html: RESTORE_PREFERENCES }} />

        <a className="skip-link" href="#main">
          Przejdź do treści
        </a>

        <SiteHeader />

        <main id="main" className="container-kr py-6">
          {children}
        </main>

        <SiteFooter />
      </body>
    </html>
  );
}
