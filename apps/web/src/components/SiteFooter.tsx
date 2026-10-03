import Image from "next/image";
import Link from "next/link";

const LINKS = [
  { href: "/#zrodla", label: "Źródła danych i licencje" },
  { href: "/#dostepnosc", label: "Deklaracja dostępności" },
  { href: "/#jak-to-dziala", label: "Jak powstaje ocena wiarygodności" },
  { href: "https://otwartedane.um.krakow.pl/", label: "Portal Otwarte Dane Miasta Krakowa" },
  { href: "https://www.openstreetmap.org/copyright", label: "OpenStreetMap — licencja ODbL" }
];

export function SiteFooter() {
  return (
    <footer className="kr-band mt-16">
      <div className="container-kr py-10">
        <h2 className="text-xl font-bold">RouteAble</h2>
        <p className="mt-2 max-w-3xl text-sm">
          Platforma agregująca i weryfikująca informacje o dostępności miejsc w Krakowie.
          Nie ocenia miejsca jako „dostępne” lub „niedostępne” — pokazuje fakty, źródła
          i poziom ich wiarygodności.
        </p>

        <h3 className="mt-8 text-lg font-bold">O serwisie</h3>
        <ul className="mt-2">
          {LINKS.map((link) => (
            <li key={link.href} className="border-b border-white/60">
              <Link href={link.href} className="block py-2 text-sm hover:underline">
                {link.label}
              </Link>
            </li>
          ))}
        </ul>

        <div className="mt-8 flex flex-wrap items-end justify-between gap-6">
          <div>
            <h3 className="text-lg font-bold">Kraków bez barier</h3>
            <p className="mt-1 text-sm">Otwarte miasto dla każdego</p>
            <p className="mt-3 text-sm">
              Dane pochodzą z OpenStreetMap, otwartych danych miejskich i oficjalnych stron
              obiektów. Brak danych nie oznacza dostępności.
            </p>
          </div>

          <Image
            src="/logo.png"
            alt="Logo RouteAble — Kraków bez barier"
            width={96}
            height={96}
            className="kr-keep-colour bg-white p-2"
          />
        </div>
      </div>
    </footer>
  );
}
