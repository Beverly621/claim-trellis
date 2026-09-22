import pytest

from claim_trellis.audit import run_audit
from claim_trellis.config import Settings
from claim_trellis.models import (
    AuditRequest,
    ChoiceJudgment,
    JudgmentResult,
    NoulJudgment,
    RevisionContext,
    SourceAccessTier,
    SourceMetadata,
)


def choice(name: str) -> ChoiceJudgment:
    return ChoiceJudgment(choice=name, probabilities={name: 1.0}, confidence=1.0)


class StubProvider:
    provider_name = "test_provider"
    model_name = "stub-1"
    question_set_version = "test-questions-v1"

    async def evaluate(
        self,
        claim: str,
        evidence: str,
        citation: str | None = None,
        *,
        revision_context: RevisionContext | None = None,
    ) -> JudgmentResult:
        return JudgmentResult(
            provider=self.provider_name,
            requested_model="stub-1",
            resolved_model="stub-1",
            question_set_version=self.question_set_version,
            relation=choice("supports"),
            scope_alignment=choice("aligned"),
            population_alignment=choice("not_applicable"),
            causal_fidelity=choice("not_applicable"),
            context_sufficiency=NoulJudgment(noul=1.0),
            prompt_injection=NoulJudgment(noul=0.0),
            input_tokens=0,
            output_tokens=0,
            latency_ms=0,
            retry_count=0,
            raw_answers={},
        )


@pytest.mark.asyncio
async def test_audit_accepts_a_vendor_neutral_provider(tmp_path) -> None:
    request = AuditRequest(
        claim="The method improved retrieval accuracy.",
        source_text="The method improved retrieval accuracy in the held-out evaluation.",
        source=SourceMetadata(access_tier=SourceAccessTier.FULL_TEXT),
    )
    audit = await run_audit(
        request,
        Settings(data_dir=tmp_path),
        judgment_provider=StubProvider(),
    )
    assert audit.judgment_result is not None
    assert audit.judgment_result.provider == "test_provider"
    assert audit.provenance.judgment_provider == "test_provider"
