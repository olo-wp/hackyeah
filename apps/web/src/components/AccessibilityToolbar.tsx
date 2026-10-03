"use client";

import { useEffect, useState } from "react";

type FontSize = "sm" | "md" | "lg";
type Contrast = "normal" | "high";

export interface A11yLabels {
  contrastOn: string;
  contrastOff: string;
  textSizeGroup: string;
  sizeDefault: string;
  sizeLarger: string;
  sizeLargest: string;
}

export function AccessibilityToolbar({ labels }: { labels: A11yLabels }) {
  const [fontSize, setFontSize] = useState<FontSize>("sm");
  const [contrast, setContrast] = useState<Contrast>("normal");

  useEffect(() => {
    const root = document.documentElement;
    setFontSize((root.dataset.fontSize as FontSize) ?? "sm");
    setContrast((root.dataset.contrast as Contrast) ?? "normal");
  }, []);

  const apply = (nextFontSize: FontSize, nextContrast: Contrast) => {
    const root = document.documentElement;
    root.dataset.fontSize = nextFontSize;
    root.dataset.contrast = nextContrast;
    localStorage.setItem("routeable:font-size", nextFontSize);
    localStorage.setItem("routeable:contrast", nextContrast);
    setFontSize(nextFontSize);
    setContrast(nextContrast);
  };

  const sizes: Array<{ value: FontSize; className: string; title: string }> = [
    { value: "sm", className: "text-sm", title: labels.sizeDefault },
    { value: "md", className: "text-base", title: labels.sizeLarger },
    { value: "lg", className: "text-lg", title: labels.sizeLargest }
  ];

  return (
    <div className="flex items-center gap-4">
      <button
        type="button"
        onClick={() => apply(fontSize, contrast === "high" ? "normal" : "high")}
        aria-pressed={contrast === "high"}
        className="flex items-center gap-2 border-2 border-white px-3 py-1 text-sm font-bold hover:bg-white/15"
      >
        <span aria-hidden="true">◐</span>
        <span>{contrast === "high" ? labels.contrastOff : labels.contrastOn}</span>
      </button>

      <div role="group" aria-label={labels.textSizeGroup} className="flex items-center gap-1">
        {sizes.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => apply(option.value, contrast)}
            aria-pressed={fontSize === option.value}
            title={option.title}
            className={`${option.className} w-9 border-2 py-1 font-bold ${
              fontSize === option.value
                ? "border-white bg-white text-[#0064b6]"
                : "border-transparent hover:border-white"
            }`}
          >
            <span aria-hidden="true">A</span>
            <span className="sr-only">{option.title}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
