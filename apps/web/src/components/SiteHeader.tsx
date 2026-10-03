import Image from "next/image";
import Link from "next/link";
import { AccessibilityToolbar } from "./AccessibilityToolbar";

const NAV = [
  { href: "/", label: "Szukaj miejsca" },
  { href: "/#jak-to-dziala", label: "Jak to działa" },
  { href: "/#zrodla", label: "Źródła danych" }
];

export function SiteHeader() {
  return (
    <header className="kr-band">
      <div className="container-kr">
        <div className="flex flex-col items-center gap-3 pt-5 sm:flex-row sm:justify-center">
          <Link href="/" className="flex items-center gap-3">
            <Image
              src="/logo.png"
              alt=""
              width={64}
              height={64}
              priority
              className="kr-keep-colour bg-white p-1"
            />
            <span className="text-left">
              <span className="block text-2xl font-bold leading-tight sm:text-3xl">RouteAble</span>
              <span className="block text-sm">Kraków bez barier</span>
            </span>
          </Link>
        </div>

        <nav aria-label="Menu główne" className="mt-4">
          <ul className="flex flex-wrap items-center justify-center gap-x-8 gap-y-2">
            {NAV.map((item) => (
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

        <AccessibilityToolbar />
      </div>
    </header>
  );
}
