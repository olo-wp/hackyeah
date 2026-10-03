import type { Locale } from "@/i18n/config";
import type { Dictionary } from "@/i18n";

export function SiteFooter({ dict }: { locale: Locale; dict: Dictionary }) {
  return (
    <footer className="kr-band mt-16">
      <div className="container-kr py-6">
        <p className="text-sm font-bold">
          {dict.common.siteName} &copy; {new Date().getFullYear()}
        </p>
      </div>
    </footer>
  );
}
