from __future__ import annotations

import math
import re
from collections import Counter

from claim_trellis.chunking import chunk_text
from claim_trellis.models import EvidencePassage, RetrievedCandidate

TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9'-]{1,}|\d+(?:\.\d+)?")
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "was",
    "were",
    "with",
}


def tokenize(text: str) -> list[str]:
    return [
        token
        for token in (match.group(0).lower() for match in TOKEN_RE.finditer(text))
        if token not in STOPWORDS
    ]


def rank_passages(
    claim: str,
    passages: list[EvidencePassage],
    *,
    top_k: int = 5,
    k1: float = 1.5,
    b: float = 0.75,
) -> list[RetrievedCandidate]:
    if not passages:
        return []
    query = list(dict.fromkeys(tokenize(claim)))
    documents = [tokenize(passage.text) for passage in passages]
    average_length = sum(len(document) for document in documents) / len(documents) or 1.0
    document_frequency = Counter(token for document in documents for token in set(document))
    scored: list[tuple[float, EvidencePassage]] = []
    for passage, document in zip(passages, documents, strict=True):
        frequencies = Counter(document)
        score = 0.0
        for token in query:
            frequency = frequencies[token]
            if not frequency:
                continue
            df = document_frequency[token]
            inverse = math.log(1 + (len(documents) - df + 0.5) / (df + 0.5))
            denominator = frequency + k1 * (1 - b + b * len(document) / average_length)
            score += inverse * (frequency * (k1 + 1)) / denominator
        scored.append((score, passage))
    scored.sort(key=lambda item: (-item[0], item[1].start_char))
    return [
        RetrievedCandidate(passage=passage, score=round(score, 8), rank=rank)
        for rank, (score, passage) in enumerate(scored[:top_k], start=1)
    ]


def retrieve(claim: str, source_text: str, *, top_k: int = 5) -> list[RetrievedCandidate]:
    return rank_passages(claim, chunk_text(source_text), top_k=top_k)
