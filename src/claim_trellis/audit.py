from __future__ import annotations

import hashlib
from uuid import uuid4

from claim_trellis import __version__
from claim_trellis.chunking import RETRIEVAL_VERSION
from claim_trellis.config import Settings
from claim_trellis.deterministic import run_deterministic_checks
from claim_trellis.models import AuditRequest, ClaimAudit, Provenance
from claim_trellis.policy import POLICY_VERSION, propose_disposition
from claim_trellis.provider import JudgmentProvider, ProviderError
from claim_trellis.providers import TypeSafeJevProvider
from claim_trellis.retrieval import retrieve


async def run_audit(
    request: AuditRequest,
    settings: Settings,
    *,
    judgment_provider: JudgmentProvider | None = None,
) -> ClaimAudit:
    candidates = retrieve(request.claim, request.source_text, top_k=request.top_k)
    selected = candidates[0].passage if candidates and candidates[0].score > 0 else None
    checks = run_deterministic_checks(
        request.claim,
        selected.text if selected else None,
        request.quote,
        quote_source_text=request.source_text,
    )
    errors: list[str] = []
    judgment_result = None
    provider = judgment_provider
    if request.use_judgment_provider and selected is not None:
        if (
            provider is None
            and settings.judgment_provider == "typesafe_jev"
            and settings.jev_api_key
        ):
            provider = TypeSafeJevProvider(
                api_key=settings.jev_api_key,
                endpoint=settings.jev_endpoint,
                model=settings.jev_model,
                timeout_seconds=settings.jev_timeout_seconds,
                max_retries=settings.jev_max_retries,
            )
        if provider is not None:
            try:
                judgment_result = await provider.evaluate(
                    request.claim, selected.text, request.citation
                )
            except ProviderError as exc:
                errors.append(str(exc))

    source = request.source.model_copy(
        update={
            "content_sha256": request.source.content_sha256
            or hashlib.sha256(request.source_text.encode()).hexdigest()
        }
    )
    proposal = propose_disposition(
        checks,
        judgment_result,
        source_access_tier=source.access_tier,
        relation_confidence_threshold=settings.relation_confidence_threshold,
        alignment_confidence_threshold=settings.alignment_confidence_threshold,
        service_errors=errors,
    )
    return ClaimAudit(
        audit_id=str(uuid4()),
        claim=request.claim,
        citation=request.citation,
        source=source,
        candidates=candidates,
        selected_passage=selected,
        deterministic_checks=checks,
        judgment_result=judgment_result,
        proposal=proposal,
        provenance=Provenance(
            application_version=__version__,
            retrieval_version=RETRIEVAL_VERSION,
            judgment_provider=provider.provider_name if provider is not None else None,
            question_set_version=(
                provider.question_set_version if provider is not None else "not-run"
            ),
            policy_version=POLICY_VERSION,
        ),
        service_errors=errors,
    )
