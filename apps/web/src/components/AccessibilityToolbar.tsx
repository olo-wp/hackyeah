"use client";

import { useEffect, useState } from "react";

type FontSize = "sm" | "md" | "lg";
type Contrast = "normal" | "high";

const FONT_SIZES: Array<{ value: FontSize; label: string; className: string; title: string }> = [
  { value: "sm", label: "A", className: "text-sm", title: "Domyślny rozmiar tekstu" },
  { value: "md", label: "A", className: "text-base", title: "Większy tekst" },
  { value: "lg", label: "A", className: "text-lg", title: "Największy tekst" }
];

export function AccessibilityToolbar() {
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

  return (
    <div className="flex items-center justify-center gap-4 py-2">
      <button
        type="button"
        onClick={() => apply(fontSize, contrast === "high" ? "normal" : "high")}
        aria-pressed={contrast === "high"}
        className="flex items-center gap-2 border-2 border-white px-3 py-1 font-bold hover:bg-white/15"
      >
        <span aria-hidden="true">◐</span>
        <span>{contrast === "high" ? "Zwykły kontrast" : "Wysoki kontrast"}</span>
      </button>

      <div role="group" aria-label="Rozmiar tekstu" className="flex items-center gap-1">
        {FONT_SIZES.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => apply(option.value, contrast)}
            aria-pressed={fontSize === option.value}
            title={option.title}
            className={`${option.className} w-9 border-2 py-1 font-bold ${
              fontSize === option.value
                ? "border-white bg-white text-krakow"
                : "border-transparent hover:border-white"
            }`}
          >
            <span aria-hidden="true">{option.label}</span>
            <span className="sr-only">{option.title}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
