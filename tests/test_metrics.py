from pathlib import Path

from claim_trellis.metrics import (
    BenchmarkCase,
    Prediction,
    score_predictions,
    validate_benchmark,
)


def test_seed_benchmark_is_valid_and_recent() -> None:
    path = Path(__file__).parents[1] / "benchmarks" / "literature_seed.jsonl"
    summary = validate_benchmark(path)
    assert summary["cases"] >= 25
    assert summary["sources"] >= 8
    assert "supports" in summary["labels"]
    assert "contradicts" in summary["labels"]


def test_metrics_include_accuracy_and_calibration() -> None:
    source = {
        "source_id": "s",
        "title": "t",
        "journal": "Nature",
        "year": 2024,
        "doi": "10.test/test",
        "url": "https://example.org",
        "domain": "test",
        "checked_at": "2026-09-21",
    }
    cases = [
        BenchmarkCase(
            case_id="a",
            source=source,
            claim="a",
            evidence="a",
            label="supports",
            failure_mode="none",
            evidence_locator="abstract",
        ),
        BenchmarkCase(
            case_id="b",
            source=source,
            claim="b",
            evidence="b",
            label="contradicts",
            failure_mode="reversal",
            evidence_locator="abstract",
        ),
    ]
    predictions = [
        Prediction(
            case_id="a", prediction="supports", probabilities={"supports": 0.9}, confidence=0.9
        ),
        Prediction(
            case_id="b", prediction="contradicts", probabilities={"supports": 0.1}, confidence=0.9
        ),
    ]
    report = score_predictions(cases, predictions)
    assert report["accuracy"] == 1.0
    assert report["calibration"]["count"] == 2
    assert report["high_confidence"]["support_proposal_count"] == 1
    assert report["high_confidence"]["false_support_rate"] == 0.0
