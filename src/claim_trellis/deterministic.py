from __future__ import annotations

import hashlib
import re
import unicodedata

from claim_trellis.models import DeterministicChecks, NumericToken

DASHES = str.maketrans({"‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-", "−": "-"})
QUOTES = str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'"})
NUMBER_RE = re.compile(
    r"(?<![\w.])(?P<number>-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?|-?\.\d+)"
    r"\s*(?P<unit>%|percent(?:age)?|mg|g|kg|µg|μg|ml|l|mmhg|years?|months?|days?|hours?)?",
    re.IGNORECASE,
)


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).translate(DASHES).translate(QUOTES)
    return re.sub(r"\s+", " ", normalized).strip().lower()


def text_sha256(text: str) -> str:
    return hashlib.sha256(normalize_text(text).encode()).hexdigest()


def locate_quote(source_text: str, quote: str) -> tuple[bool, int | None]:
    needle = normalize_text(quote)
    if not needle:
        return False, None
    index = normalize_text(source_text).find(needle)
    return index >= 0, index if index >= 0 else None


def extract_numeric_tokens(text: str) -> list[NumericToken]:
    tokens: list[NumericToken] = []
    for match in NUMBER_RE.finditer(normalize_text(text)):
        raw = match.group("number")
        value = float(raw.replace(",", ""))
        unit = match.group("unit")
        tokens.append(NumericToken(raw=match.group(0).strip(), normalized=value, unit=unit))
    return tokens


def _equivalent(left: NumericToken, right: NumericToken) -> bool:
    if abs(left.normalized - right.normalized) > 1e-9 * max(
        1.0, abs(left.normalized), abs(right.normalized)
    ):
        return False
    if left.unit and right.unit and left.unit.lower() != right.unit.lower():
        aliases = {
            "percent": "%",
            "percentage": "%",
            "year": "years",
            "month": "months",
            "day": "days",
            "hour": "hours",
        }
        return aliases.get(left.unit.lower(), left.unit.lower()) == aliases.get(
            right.unit.lower(), right.unit.lower()
        )
    return True


def run_deterministic_checks(
    claim: str,
    evidence: str | None,
    quote: str | None = None,
    *,
    quote_source_text: str | None = None,
) -> DeterministicChecks:
    claim_numbers = extract_numeric_tokens(claim)
    evidence_numbers = extract_numeric_tokens(evidence or "")
    unmatched = [
        token
        for token in claim_numbers
        if not any(_equivalent(token, candidate) for candidate in evidence_numbers)
    ]
    warnings: list[str] = []
    quote_found: bool | None = None
    if quote is not None:
        quote_found, _ = locate_quote(
            quote_source_text if quote_source_text is not None else evidence or "", quote
        )
        if not quote_found:
            warnings.append("The requested quote was not found in the selected evidence passage.")
    if unmatched:
        warnings.append(
            "One or more numeric values in the claim were not found in the selected passage."
        )
    if evidence is None:
        warnings.append("No evidence passage was retrieved.")
    return DeterministicChecks(
        normalized_claim_sha256=text_sha256(claim),
        selected_evidence_sha256=text_sha256(evidence) if evidence else None,
        quote_requested=quote is not None,
        quote_found=quote_found,
        claim_numbers=claim_numbers,
        evidence_numbers=evidence_numbers,
        unmatched_claim_numbers=unmatched,
        warnings=warnings,
    )
