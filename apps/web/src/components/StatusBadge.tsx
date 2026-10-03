import type { FeatureStatus } from "@/lib/types";

const STYLES: Record<FeatureStatus, { icon: string; className: string }> = {
  confirmed: { icon: "✓", className: "border-[#1b5e20] bg-[#e8f3e9] text-[#1b5e20]" },
  unknown: { icon: "?", className: "border-[#5b6770] bg-[#eef1f3] text-[#394149]" },
  conflicting: { icon: "⚠", className: "border-[#8a4b00] bg-[#fdf0e0] text-[#8a4b00]" },
  stale: { icon: "◷", className: "border-[#0064b6] bg-[#e8f1f8] text-[#005092]" }
};

/** Status is conveyed by icon *and* text — never by colour alone. */
export function StatusBadge({
  status,
  labels
}: {
  status: FeatureStatus;
  labels: Record<FeatureStatus, string>;
}) {
  const { icon, className } = STYLES[status];

  return (
    <span
      className={`inline-flex items-center gap-1.5 border-2 px-2 py-0.5 text-sm font-bold ${className}`}
    >
      <span aria-hidden="true">{icon}</span>
      <span>{labels[status]}</span>
    </span>
  );
}
