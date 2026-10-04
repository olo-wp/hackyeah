import Link from "next/link";
import type { Dictionary } from "@/i18n";

/** Bottom-of-page call to action that links to the contribute page. */
export function CommunityAnswers({
  locale,
  placeId,
  dict
}: {
  locale: string;
  placeId: string;
  dict: Dictionary["community"];
}) {
  return (
    <section className="kr-card mt-8 bg-[#eef1f3] px-4 py-6 text-center">
      <h2 className="kr-heading text-xl font-bold">{dict.heading}</h2>
      <p className="mx-auto mt-2 max-w-2xl text-[var(--color-muted)]">{dict.intro}</p>
      <Link
        href={`/${locale}/contribute?place=${encodeURIComponent(placeId)}`}
        className="kr-btn mt-4 inline-block"
      >
        {dict.answerCta}
      </Link>
    </section>
  );
}
