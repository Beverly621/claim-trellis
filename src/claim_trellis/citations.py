from __future__ import annotations

import re

from claim_trellis.models import ParsedCitationSentence

NUMERIC_MARKER = re.compile(
    r"(?:\[(?:\d{1,4})(?:\s*[-,–—]\s*\d{1,4})*\]|"
    r"\((?!(?:19|20)\d{2}\))(?:\d{1,4})(?:\s*[-,–—]\s*\d{1,4})*\))"
)
AUTHOR_YEAR_MARKER = re.compile(
    r"\((?:[A-Z][A-Za-z'’-]+(?:\s+et\s+al\.)?"
    r"(?:\s*(?:,|&|and)\s*[A-Z][A-Za-z'’-]+(?:\s+et\s+al\.)?)*)"
    r"\s*,?\s*(?:19|20)\d{2}[a-z]?(?:\s*;[^)]*)?\)"
)
PARENTHETICAL_YEAR = re.compile(r"\b[A-Z][A-Za-z'’-]+(?:\s+et\s+al\.)?\s*\((?:19|20)\d{2}[a-z]?\)")

_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])(?:[\"'’”\]])?\s+(?=[A-Z0-9])")


def sentence_spans(text: str) -> list[tuple[int, int]]:
    """Return conservative sentence spans without losing source offsets."""

    if not text.strip():
        return []
    starts = [0]
    for match in _SENTENCE_BOUNDARY.finditer(text):
        starts.append(match.end())
    spans: list[tuple[int, int]] = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(text)
        while start < end and text[start].isspace():
            start += 1
        while end > start and text[end - 1].isspace():
            end -= 1
        if end > start:
            spans.append((start, end))
    return spans


def citation_markers(sentence: str) -> list[str]:
    matches: list[tuple[int, str]] = []
    for pattern in (NUMERIC_MARKER, AUTHOR_YEAR_MARKER, PARENTHETICAL_YEAR):
        matches.extend((match.start(), match.group(0)) for match in pattern.finditer(sentence))
    return [marker for _, marker in sorted(matches, key=lambda item: item[0])]


def extract_citation_sentences(text: str) -> list[ParsedCitationSentence]:
    rows: list[ParsedCitationSentence] = []
    for start, end in sentence_spans(text):
        sentence = text[start:end]
        markers = citation_markers(sentence)
        if markers:
            rows.append(
                ParsedCitationSentence(
                    sentence=sentence,
                    markers=markers,
                    start_char=start,
                    end_char=end,
                )
            )
    return rows


def strip_citation_markers(sentence: str) -> str:
    result = sentence
    for pattern in (NUMERIC_MARKER, AUTHOR_YEAR_MARKER, PARENTHETICAL_YEAR):
        result = pattern.sub("", result)
    return re.sub(r"\s+([.,;:?!])", r"\1", re.sub(r"\s+", " ", result)).strip()
