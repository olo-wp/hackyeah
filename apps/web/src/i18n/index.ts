import type { Locale } from "./config";
import { en } from "./dictionaries/en";
import { pl, type Dictionary } from "./dictionaries/pl";

const DICTIONARIES: Record<Locale, Dictionary> = { pl, en };

export function getDictionary(locale: Locale): Dictionary {
  return DICTIONARIES[locale];
}

/** Fills `{placeholder}` slots in a translated string. */
export function format(template: string, values: Record<string, string | number>): string {
  return template.replace(/\{(\w+)\}/g, (match, key: string) =>
    key in values ? String(values[key]) : match
  );
}

export type { Dictionary };
