"""Keyword extraction over the visible text of an allowlisted accessibility page.

Every value keeps the sentence it came from so a human can verify it later.
"""

import html
import re
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from routeable_model import FeatureKey, RawAccessibilityEvidence, VerificationStatus

_SCRIPTS = re.compile(r"<(script|style|noscript)[\s\S]*?</\1>", re.IGNORECASE)
_TAGS = re.compile(r"<[^>]+>")
_WHITESPACE = re.compile(r"\s+")

NEGATION = re.compile(
    r"(brak|nie\s+ma|nie\s+posiada|niedostępn|niedostepn|bez\s+windy|\bno\s)", re.IGNORECASE
)

SNIPPET_PADDING = 80
NEGATION_WINDOW = 40

PL_NUMBERS: dict[str, int] = {
    "jeden": 1,
    "jednego": 1,
    "dwa": 2,
    "dwoch": 2,
    "trzy": 3,
    "cztery": 4,
    "piec": 5,
}


def html_to_text(raw_html: str) -> str:
    without_scripts = _SCRIPTS.sub(" ", raw_html)
    without_tags = _TAGS.sub(" ", without_scripts)
    return _WHITESPACE.sub(" ", html.unescape(without_tags)).strip()


def _to_count(raw: str) -> int | None:
    if raw.isdigit():
        return int(raw)
    decomposed = unicodedata.normalize("NFD", raw.lower())
    ascii_word = "".join(c for c in decomposed if not unicodedata.combining(c))
    return PL_NUMBERS.get(ascii_word)


@dataclass(frozen=True, slots=True)
class ExtractionRule:
    feature_key: FeatureKey
    pattern: re.Pattern[str]
    extract: Callable[[re.Match[str], bool], Any]


RULES: tuple[ExtractionRule, ...] = (
    ExtractionRule(
        FeatureKey.STEP_FREE_ENTRANCE,
        re.compile(
            r"(wejście[^.]{0,40}(bezstopniow|bez\s+schod)"
            r"|bezstopniow\w*\s+wejści"
            r"|step[-\s]free\s+entrance)",
            re.IGNORECASE,
        ),
        lambda _match, negated: not negated,
    ),
    ExtractionRule(
        FeatureKey.ENTRANCE_STEPS,
        re.compile(r"(\d+|jeden|dwa|trzy|cztery|pięć)\s+stopn\w*", re.IGNORECASE),
        lambda match, _negated: _to_count(match.group(1)),
    ),
    ExtractionRule(
        FeatureKey.RAMP,
        re.compile(r"(podjazd\w*|pochyln\w*|\bramp\b)", re.IGNORECASE),
        lambda _match, negated: not negated,
    ),
    ExtractionRule(
        FeatureKey.ELEVATOR,
        re.compile(r"(wind[aeyąę]\w*|\belevator\b|\blift\b)", re.IGNORECASE),
        lambda _match, negated: not negated,
    ),
    ExtractionRule(
        FeatureKey.ACCESSIBLE_TOILET,
        re.compile(
            r"(toalet\w*[^.]{0,60}(dostosowan|przystosowan|dla\s+osób|wózk)"
            r"|accessible\s+toilet)",
            re.IGNORECASE,
        ),
        lambda _match, negated: not negated,
    ),
    ExtractionRule(
        FeatureKey.DOOR_WIDTH_CM,
        re.compile(r"szerokoś\w*[^.]{0,40}?(\d{2,3})\s*cm", re.IGNORECASE),
        lambda match, _negated: int(match.group(1)),
    ),
    ExtractionRule(
        FeatureKey.ACCESSIBLE_PARKING,
        re.compile(
            r"(miejsc\w*\s+parkingow\w*[^.]{0,40}(dla\s+osób|niepełnosprawn)|koperta)",
            re.IGNORECASE,
        ),
        lambda _match, negated: not negated,
    ),
    ExtractionRule(
        FeatureKey.SEATING,
        re.compile(
            r"(miejsc\w*\s+(do\s+)?odpoczynk\w*|ławk\w*|krzesł\w*\s+dla\s+zwiedzaj)",
            re.IGNORECASE,
        ),
        lambda _match, negated: not negated,
    ),
)


def extract_accessibility_evidence(text: str, source_url: str) -> list[RawAccessibilityEvidence]:
    evidence: list[RawAccessibilityEvidence] = []

    for rule in RULES:
        match = rule.pattern.search(text)
        if match is None:
            continue

        start, end = match.span()
        preceding = text[max(0, start - NEGATION_WINDOW) : start]
        value = rule.extract(match, NEGATION.search(preceding) is not None)
        if value is None:
            continue

        evidence.append(
            RawAccessibilityEvidence(
                feature_key=rule.feature_key,
                value=value,
                verification_status=VerificationStatus.AUTOMATICALLY_EXTRACTED,
                raw_data={
                    "snippet": text[
                        max(0, start - SNIPPET_PADDING) : min(len(text), end + SNIPPET_PADDING)
                    ].strip(),
                    "matched": match.group(0),
                },
                source_url=source_url,
            )
        )

    return evidence
