from claim_trellis.deterministic import run_deterministic_checks
from claim_trellis.models import (
    ChoiceJudgment,
    JudgmentResult,
    NoulJudgment,
    ProposalStatus,
    SourceAccessTier,
)
from claim_trellis.policy import propose_disposition


def choice(name: str, confidence: float = 0.96) -> ChoiceJudgment:
    return ChoiceJudgment(choice=name, probabilities={name: 1.0}, confidence=confidence)


def judgment(relation: str = "supports") -> JudgmentResult:
    return JudgmentResult(
        provider="typesafe_jev",
        requested_model="jev-1.13.0",
        resolved_model="jev-1.13.0",
        question_set_version="test",
        relation=choice(relation),
        scope_alignment=choice("aligned"),
        population_alignment=choice("not_applicable"),
        causal_fidelity=choice("not_applicable"),
        context_sufficiency=NoulJudgment(noul=0.98),
        prompt_injection=NoulJudgment(noul=0.01),
        input_tokens=100,
        output_tokens=10,
        latency_ms=20,
        retry_count=0,
        raw_answers={},
    )


def test_never_auto_accepts_supported_result() -> None:
    checks = run_deterministic_checks("The intervention helped.", "The intervention helped.")
    proposal = propose_disposition(
        checks, judgment(), source_access_tier=SourceAccessTier.FULL_TEXT
    )
    assert proposal.status == ProposalStatus.SUPPORTED
    assert proposal.requires_human_review
    assert not proposal.auto_accepted


def test_missing_quote_fails_closed() -> None:
    checks = run_deterministic_checks("A claim.", "Evidence.", "absent quote")
    proposal = propose_disposition(
        checks, judgment(), source_access_tier=SourceAccessTier.FULL_TEXT
    )
    assert proposal.status == ProposalStatus.EVIDENCE_MISSING


def test_abstract_silence_routes_to_review() -> None:
    checks = run_deterministic_checks("A claim.", "Unrelated evidence.")
    proposal = propose_disposition(
        checks,
        judgment("not_addressed"),
        source_access_tier=SourceAccessTier.ABSTRACT,
    )
    assert proposal.status == ProposalStatus.REVIEW_REQUIRED
