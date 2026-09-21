from claim_trellis.benchmark_runner import result_to_prediction
from claim_trellis.models import ChoiceJudgment, JudgmentResult, NoulJudgment


def test_result_to_prediction_preserves_provenance() -> None:
    supported = ChoiceJudgment(choice="supports", probabilities={"supports": 1.0}, confidence=1.0)
    aligned = ChoiceJudgment(choice="aligned", probabilities={"aligned": 1.0}, confidence=1.0)
    not_applicable = ChoiceJudgment(
        choice="not_applicable", probabilities={"not_applicable": 1.0}, confidence=1.0
    )
    result = JudgmentResult(
        provider="typesafe_jev",
        requested_model="jev-1.13.0",
        resolved_model="jev-1.13.0",
        question_set_version="test-v1",
        relation=supported,
        scope_alignment=aligned,
        population_alignment=not_applicable,
        causal_fidelity=not_applicable,
        context_sufficiency=NoulJudgment(noul=1.0),
        prompt_injection=NoulJudgment(noul=0.0),
        input_tokens=200,
        output_tokens=20,
        latency_ms=40,
        retry_count=0,
        raw_answers={},
    )
    prediction = result_to_prediction("case-1", result, cached=True)
    assert prediction.prediction == "supports"
    assert prediction.model == "jev-1.13.0"
    assert prediction.cached
