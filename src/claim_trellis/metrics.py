from __future__ import annotations

import json
from collections import Counter, defaultdict
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from claim_trellis.models import RelationLabel


class LiteratureSource(BaseModel):
    source_id: str
    title: str
    journal: str
    year: int = Field(ge=2022, le=2026)
    doi: str
    url: str
    domain: str
    checked_at: str


class BenchmarkCase(BaseModel):
    case_id: str
    source: LiteratureSource
    claim: str
    evidence: str
    label: RelationLabel
    failure_mode: str
    evidence_locator: str
    annotation_status: str = "editor_seed"
    notes: str = ""


class Prediction(BaseModel):
    case_id: str
    prediction: RelationLabel
    probabilities: dict[str, float] = Field(default_factory=dict)
    confidence: float | None = Field(default=None, ge=0, le=1)
    model: str | None = None
    question_set_version: str | None = None
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    latency_ms: float | None = Field(default=None, ge=0)
    cached: bool = False


def read_jsonl(path: Path, model: type[BaseModel]) -> list[BaseModel]:
    records: list[BaseModel] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                records.append(model.model_validate_json(line))
            except Exception as exc:
                raise ValueError(f"Invalid JSONL record at {path}:{line_number}: {exc}") from exc
    return records


def _per_label(gold: list[str], predicted: list[str]) -> dict[str, dict[str, float | int]]:
    labels = sorted(set(gold) | set(predicted))
    report: dict[str, dict[str, float | int]] = {}
    for label in labels:
        true_positive = sum(g == label and p == label for g, p in zip(gold, predicted, strict=True))
        false_positive = sum(
            g != label and p == label for g, p in zip(gold, predicted, strict=True)
        )
        false_negative = sum(
            g == label and p != label for g, p in zip(gold, predicted, strict=True)
        )
        support = sum(g == label for g in gold)
        precision = (
            true_positive / (true_positive + false_positive)
            if true_positive + false_positive
            else 0.0
        )
        recall = (
            true_positive / (true_positive + false_negative)
            if true_positive + false_negative
            else 0.0
        )
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        report[label] = {
            "precision": round(precision, 6),
            "recall": round(recall, 6),
            "f1": round(f1, 6),
            "support": support,
        }
    return report


def _calibration(
    cases: list[BenchmarkCase], predictions: dict[str, Prediction], bins: int = 10
) -> dict[str, Any]:
    observations: list[tuple[float, int]] = []
    for case in cases:
        prediction = predictions[case.case_id]
        probability = prediction.probabilities.get("supports")
        if probability is not None:
            observations.append((probability, int(case.label == "supports")))
    if not observations:
        return {"count": 0, "brier": None, "expected_calibration_error": None, "bins": []}
    brier = sum((probability - outcome) ** 2 for probability, outcome in observations) / len(
        observations
    )
    grouped: dict[int, list[tuple[float, int]]] = defaultdict(list)
    for probability, outcome in observations:
        grouped[min(int(probability * bins), bins - 1)].append((probability, outcome))
    rows: list[dict[str, float | int]] = []
    ece = 0.0
    for index in range(bins):
        values = grouped[index]
        if not values:
            continue
        mean_probability = sum(item[0] for item in values) / len(values)
        observed_rate = sum(item[1] for item in values) / len(values)
        ece += len(values) / len(observations) * abs(mean_probability - observed_rate)
        rows.append(
            {
                "lower": index / bins,
                "upper": (index + 1) / bins,
                "count": len(values),
                "mean_probability": round(mean_probability, 6),
                "observed_rate": round(observed_rate, 6),
            }
        )
    return {
        "count": len(observations),
        "brier": round(brier, 6),
        "expected_calibration_error": round(ece, 6),
        "bins": rows,
    }


def score_predictions(
    cases: Iterable[BenchmarkCase], predictions: Iterable[Prediction]
) -> dict[str, Any]:
    case_list = list(cases)
    prediction_map = {prediction.case_id: prediction for prediction in predictions}
    missing = [case.case_id for case in case_list if case.case_id not in prediction_map]
    extra = sorted(set(prediction_map) - {case.case_id for case in case_list})
    if missing:
        raise ValueError(f"Missing predictions for {len(missing)} cases: {', '.join(missing[:10])}")
    gold = [case.label.value for case in case_list]
    predicted = [prediction_map[case.case_id].prediction.value for case in case_list]
    correct = sum(left == right for left, right in zip(gold, predicted, strict=True))
    confusion: dict[str, Counter[str]] = defaultdict(Counter)
    for expected, actual in zip(gold, predicted, strict=True):
        confusion[expected][actual] += 1
    high_confidence = [
        (case, prediction_map[case.case_id])
        for case in case_list
        if (prediction_map[case.case_id].confidence or 0) >= 0.9
    ]
    high_confidence_supports = [
        (case, prediction)
        for case, prediction in high_confidence
        if prediction.prediction == RelationLabel.SUPPORTS
    ]
    false_support = sum(
        case.label != RelationLabel.SUPPORTS for case, _prediction in high_confidence_supports
    )
    return {
        "case_count": len(case_list),
        "accuracy": round(correct / len(case_list), 6) if case_list else None,
        "per_label": _per_label(gold, predicted),
        "confusion_matrix": {label: dict(counts) for label, counts in sorted(confusion.items())},
        "calibration": _calibration(case_list, prediction_map),
        "high_confidence": {
            "threshold": 0.9,
            "count": len(high_confidence),
            "support_proposal_count": len(high_confidence_supports),
            "false_support_count": false_support,
            "false_support_rate": round(false_support / len(high_confidence_supports), 6)
            if high_confidence_supports
            else None,
        },
        "extra_prediction_ids": extra,
    }


def validate_benchmark(path: Path) -> dict[str, Any]:
    cases = [BenchmarkCase.model_validate(item) for item in read_jsonl(path, BenchmarkCase)]
    ids = [case.case_id for case in cases]
    duplicate_ids = sorted(case_id for case_id, count in Counter(ids).items() if count > 1)
    if duplicate_ids:
        raise ValueError(f"Duplicate case ids: {', '.join(duplicate_ids)}")
    labels = Counter(case.label for case in cases)
    domains = Counter(case.source.domain for case in cases)
    sources = {case.source.source_id for case in cases}
    return {
        "path": str(path),
        "cases": len(cases),
        "sources": len(sources),
        "labels": dict(sorted(labels.items())),
        "domains": dict(sorted(domains.items())),
        "annotation_status": dict(
            sorted(Counter(case.annotation_status for case in cases).items())
        ),
    }


def write_json(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True)
