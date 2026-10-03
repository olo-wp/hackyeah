import type { FeatureStatus } from "@/lib/types";

const LABELS: Record<FeatureStatus, { icon: string; text: string }> = {
  confirmed: { icon: "✓", text: "potwierdzone" },
  unknown: { icon: "?", text: "brak danych" },
  conflicting: { icon: "⚠", text: "dane sprzeczne" },
  stale: { icon: "◷", text: "dane mogą być nieaktualne" }
};

/** Status is conveyed by icon *and* text — never by colour alone. */
export function StatusBadge({ status }: { status: FeatureStatus }) {
  const { icon, text } = LABELS[status];

  return (
    <span className="inline-flex items-center gap-1 rounded border border-slate-300 px-2 py-0.5 text-sm">
      <span aria-hidden="true">{icon}</span>
      <span>{text}</span>
    </span>
  );
}
