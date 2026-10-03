import Image from "next/image";
import Link from "next/link";
import type { Locale } from "@/i18n/config";
import type { Dictionary } from "@/i18n";

export function SiteFooter({ locale, dict }: { locale: Locale; dict: Dictionary }) {
  const links = [
    { href: `/${locale}#zrodla`, label: dict.footer.links.sources },
    { href: `/${locale}#dostepnosc`, label: dict.footer.links.accessibility },
    { href: `/${locale}#jak-to-dziala`, label: dict.footer.links.confidence },
    { href: "https://otwartedane.um.krakow.pl/", label: dict.footer.links.portal },
    { href: "https://www.openstreetmap.org/copyright", label: dict.footer.links.osmLicense }
  ];

  return (
    <footer className="kr-band mt-16">
      <div className="container-kr py-10">
        <h2 className="text-xl font-bold">{dict.common.siteName}</h2>
        <p className="mt-2 max-w-3xl text-sm">{dict.footer.description}</p>

        <h3 className="mt-8 text-lg font-bold">{dict.footer.aboutHeading}</h3>
        <ul className="mt-2">
          {links.map((link) => (
            <li key={link.href} className="border-b border-white/60">
              <Link href={link.href} className="block py-2 text-sm hover:underline">
                {link.label}
              </Link>
            </li>
          ))}
        </ul>

        <div className="mt-8 flex flex-wrap items-end justify-between gap-6">
          <div>
            <h3 className="text-lg font-bold">{dict.footer.brandHeading}</h3>
            <p className="mt-1 text-sm">{dict.footer.brandTagline}</p>
            <p className="mt-3 max-w-2xl text-sm">{dict.footer.note}</p>
          </div>

          <Image
            src="/logo.png"
            alt={dict.common.logoAlt}
            width={96}
            height={96}
            className="kr-keep-colour bg-white p-2"
          />
        </div>
      </div>
    </footer>
  );
}
