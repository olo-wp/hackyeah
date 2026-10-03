import Image from "next/image";
import type { Dictionary } from "@/i18n";

export function SearchResultsLoading({ dict }: { dict: Dictionary }) {
  return (
    <div className="flex flex-col items-center gap-3 px-4 py-10 text-center">
      {/* `unoptimized` keeps the GIF animated — the image optimizer would flatten it. */}
      <Image
        src="/img/smok-ladowanie.gif"
        alt={dict.home.loadingAlt}
        width={160}
        height={160}
        unoptimized
        className="kr-keep-colour"
      />
      <p className="text-lg font-bold">{dict.home.loading}</p>
      <p className="max-w-md text-sm text-[var(--color-muted)]">{dict.home.loadingHint}</p>
    </div>
  );
}
