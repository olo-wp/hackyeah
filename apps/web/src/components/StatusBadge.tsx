import type { FeatureStatus } from "@/lib/types";

const LABELS: Record<FeatureStatus, { icon: string; text: string; className: string }> = {
  confirmed: {
    icon: "✓",
    text: "potwierdzone",
    className: "border-[#1b5e20] bg-[#e8f3e9] text-[#1b5e20]"
  },
  unknown: {
    icon: "?",
    text: "brak danych",
    className: "border-[#5b6770] bg-[#eef1f3] text-[#394149]"
  },
  conflicting: {
    icon: "⚠",
    text: "dane sprzeczne",
    className: "border-[#8a4b00] bg-[#fdf0e0] text-[#8a4b00]"
  },
  stale: {
    icon: "◷",
    text: "możliwe nieaktualne",
    className: "border-[#0063af] bg-[#e8f1f8] text-[#004f8c]"
  }
};

/** Status is conveyed by icon *and* text — never by colour alone. */
export function StatusBadge({ status }: { status: FeatureStatus }) {
  const { icon, text, className } = LABELS[status];

  return (
    <span
      className={`inline-flex items-center gap-1.5 border-2 px-2 py-0.5 text-sm font-bold ${className}`}
    >
      <span aria-hidden="true">{icon}</span>
      <span>{text}</span>
    </span>
  );
}
