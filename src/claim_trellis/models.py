from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, field_validator


def utc_now() -> datetime:
    return datetime.now(UTC)


class SourceAccessTier(StrEnum):
    FULL_TEXT = "full_text"
    ABSTRACT = "abstract"
    EXCERPT = "excerpt"
    UNKNOWN = "unknown"


class RelationLabel(StrEnum):
    SUPPORTS = "supports"
    PARTIALLY_SUPPORTS = "partially_supports"
    CONTRADICTS = "contradicts"
    NOT_ADDRESSED = "not_addressed"
    INSUFFICIENT_CONTEXT = "insufficient_context"
    SOURCE_UNAVAILABLE = "source_unavailable"


class ProposalStatus(StrEnum):
    SUPPORTED = "supported"
    PARTIALLY_SUPPORTED = "partially_supported"
    CONTRADICTED = "contradicted"
    UNSUPPORTED = "unsupported"
    EVIDENCE_MISSING = "evidence_missing"
    REVIEW_REQUIRED = "review_required"


class HumanDecision(StrEnum):
    ACCEPT = "accept"
    REJECT = "reject"
    REVISE = "revise"
    DEFER = "defer"


class SourceMetadata(BaseModel):
    title: str | None = None
    journal: str | None = None
    year: int | None = Field(default=None, ge=1900, le=2100)
    doi: str | None = None
    pmid: str | None = None
    url: HttpUrl | None = None
    access_tier: SourceAccessTier = SourceAccessTier.UNKNOWN
    content_sha256: str | None = None


class EvidencePassage(BaseModel):
    passage_id: str
    text: str
    locator: str
    start_char: int = Field(ge=0)
    end_char: int = Field(ge=0)
    sha256: str


class RetrievedCandidate(BaseModel):
    passage: EvidencePassage
    score: float
    rank: int = Field(ge=1)


class NumericToken(BaseModel):
    raw: str
    normalized: float
    unit: str | None = None


class DeterministicChecks(BaseModel):
    normalized_claim_sha256: str
    selected_evidence_sha256: str | None = None
    quote_requested: bool = False
    quote_found: bool | None = None
    claim_numbers: list[NumericToken] = Field(default_factory=list)
    evidence_numbers: list[NumericToken] = Field(default_factory=list)
    unmatched_claim_numbers: list[NumericToken] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ChoiceJudgment(BaseModel):
    choice: str
    probabilities: dict[str, float]
    confidence: float = Field(ge=0, le=1)

    @field_validator("probabilities")
    @classmethod
    def validate_probabilities(cls, value: dict[str, float]) -> dict[str, float]:
        if not value:
            raise ValueError("probabilities must not be empty")
        if any(probability < 0 or probability > 1 for probability in value.values()):
            raise ValueError("probabilities must be between 0 and 1")
        if abs(sum(value.values()) - 1.0) > 0.03:
            raise ValueError("probabilities must sum to approximately 1")
        return value


class NoulJudgment(BaseModel):
    noul: float = Field(ge=0, le=1)


class JudgmentResult(BaseModel):
    provider: str
    requested_model: str
    resolved_model: str
    question_set_version: str
    relation: ChoiceJudgment
    scope_alignment: ChoiceJudgment
    population_alignment: ChoiceJudgment
    causal_fidelity: ChoiceJudgment
    context_sufficiency: NoulJudgment
    prompt_injection: NoulJudgment
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    latency_ms: float = Field(ge=0)
    retry_count: int = Field(ge=0)
    raw_answers: dict[str, Any]

    @field_validator("relation")
    @classmethod
    def validate_relation_label(cls, value: ChoiceJudgment) -> ChoiceJudgment:
        RelationLabel(value.choice)
        return value


class Proposal(BaseModel):
    status: ProposalStatus
    reasons: list[str]
    requires_human_review: bool = True
    auto_accepted: bool = False
    policy_version: str


class HumanReview(BaseModel):
    decision: HumanDecision
    notes: str = Field(min_length=1, max_length=10_000)
    reviewer: str = Field(min_length=1, max_length=200)
    created_at: datetime = Field(default_factory=utc_now)


class Provenance(BaseModel):
    application_version: str
    retrieval_version: str
    judgment_provider: str | None = None
    question_set_version: str
    policy_version: str
    created_at: datetime = Field(default_factory=utc_now)


class ClaimAudit(BaseModel):
    audit_id: str
    claim: str
    citation: str | None = None
    source: SourceMetadata
    candidates: list[RetrievedCandidate]
    selected_passage: EvidencePassage | None = None
    deterministic_checks: DeterministicChecks
    judgment_result: JudgmentResult | None = None
    proposal: Proposal
    human_review: HumanReview | None = None
    provenance: Provenance
    service_errors: list[str] = Field(default_factory=list)


class AuditRequest(BaseModel):
    claim: str = Field(min_length=3, max_length=20_000)
    source_text: str = Field(min_length=1, max_length=2_000_000)
    citation: str | None = Field(default=None, max_length=2_000)
    quote: str | None = Field(default=None, max_length=20_000)
    source: SourceMetadata = Field(default_factory=SourceMetadata)
    top_k: int = Field(default=5, ge=1, le=20)
    use_judgment_provider: bool = True


class EvidenceSearchRequest(BaseModel):
    claim: str = Field(min_length=3, max_length=20_000)
    source_text: str = Field(min_length=1, max_length=2_000_000)
    top_k: int = Field(default=5, ge=1, le=20)


class HumanReviewRequest(BaseModel):
    decision: HumanDecision
    notes: str = Field(min_length=1, max_length=10_000)
    reviewer: str = Field(min_length=1, max_length=200)


class AuditEvent(BaseModel):
    event_id: str
    audit_id: str
    event_type: str
    created_at: datetime
    payload: dict[str, Any]


class ParsedCitationSentence(BaseModel):
    sentence: str
    markers: list[str]
    start_char: int = Field(ge=0)
    end_char: int = Field(ge=0)


class ParsedDocument(BaseModel):
    filename: str
    media_type: str
    text: str
    content_sha256: str
    character_count: int = Field(ge=0)
    citation_sentences: list[ParsedCitationSentence]
    warnings: list[str] = Field(default_factory=list)
