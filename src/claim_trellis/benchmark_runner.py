from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path

from claim_trellis.config import Settings
from claim_trellis.metrics import BenchmarkCase, Prediction
from claim_trellis.models import JudgmentResult, RelationLabel
from claim_trellis.provider import JudgmentProvider
from claim_trellis.providers import TypeSafeJevProvider


def _cache_key(case: BenchmarkCase, provider: JudgmentProvider) -> str:
    payload = {
        "claim": case.claim,
        "evidence": case.evidence,
        "citation": case.source.doi,
        "provider": provider.provider_name,
        "model": provider.model_name,
        "question_set_version": provider.question_set_version,
    }
    serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()


def result_to_prediction(case_id: str, result: JudgmentResult, *, cached: bool) -> Prediction:
    return Prediction(
        case_id=case_id,
        prediction=RelationLabel(result.relation.choice),
        probabilities=result.relation.probabilities,
        confidence=result.relation.confidence,
        model=result.resolved_model,
        question_set_version=result.question_set_version,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        latency_ms=result.latency_ms,
        cached=cached,
    )


async def run_cases(
    cases: list[BenchmarkCase],
    settings: Settings,
    *,
    concurrency: int = 8,
    cache_dir: Path | None = None,
    judgment_provider: JudgmentProvider | None = None,
) -> list[Prediction]:
    provider = judgment_provider
    if provider is None:
        if not settings.jev_api_key:
            raise ValueError("TYPESAFE_API_KEY is required to run a live Jev benchmark.")
        provider = TypeSafeJevProvider(
            api_key=settings.jev_api_key,
            endpoint=settings.jev_endpoint,
            model=settings.jev_model,
            timeout_seconds=settings.jev_timeout_seconds,
            max_retries=settings.jev_max_retries,
        )
    cache_root = cache_dir or settings.data_dir / "cache" / "jev"
    cache_root.mkdir(parents=True, exist_ok=True)
    semaphore = asyncio.Semaphore(max(1, concurrency))

    async def run_one(case: BenchmarkCase) -> Prediction:
        cache_path = cache_root / f"{_cache_key(case, provider)}.json"
        if cache_path.exists():
            result = JudgmentResult.model_validate_json(cache_path.read_text(encoding="utf-8"))
            return result_to_prediction(case.case_id, result, cached=True)
        async with semaphore:
            result = await provider.evaluate(case.claim, case.evidence, case.source.doi)
        temporary = cache_path.with_suffix(".tmp")
        temporary.write_text(result.model_dump_json(indent=2), encoding="utf-8")
        temporary.replace(cache_path)
        return result_to_prediction(case.case_id, result, cached=False)

    return list(await asyncio.gather(*(run_one(case) for case in cases)))


def write_predictions(path: Path, predictions: list[Prediction]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(prediction.model_dump_json() for prediction in predictions) + "\n"
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)
