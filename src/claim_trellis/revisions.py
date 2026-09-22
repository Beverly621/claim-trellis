from __future__ import annotations

import asyncio

from claim_trellis.config import Settings
from claim_trellis.models import RevisionContext, RevisionRequest, RevisionRun
from claim_trellis.policy import propose_disposition
from claim_trellis.provider import JudgmentProvider, ProviderError
from claim_trellis.providers import TypeSafeJevProvider
from claim_trellis.storage import AuditStore


async def revise(
    store: AuditStore,
    audit_id: str,
    request: RevisionRequest,
    settings: Settings,
    provider: JudgmentProvider | None = None,
) -> RevisionRun:
    run, is_new = store.request_revision(audit_id, request)
    if not is_new:
        return run
    store.start_revision(run)
    try:
        audit = store.get(audit_id)
        if audit is None or audit.selected_passage is None:
            return store.fail_revision(
                run, "evidence_unavailable", "No evidence passage is available for revision."
            )
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
        if provider is None:
            return store.fail_revision(
                run, "provider_unavailable", "Configure the judgment provider before retrying."
            )
        context = RevisionContext(
            previous_proposal=store.proposals(audit_id)[-1],
            deterministic_checks=audit.deterministic_checks,
            source_completeness=audit.source.access_tier,
            human_feedback=request.feedback,
            revision_number=audit.current_proposal_version + 1,
        )
        async with asyncio.timeout(90):
            judgment = await provider.evaluate(
                audit.claim, audit.selected_passage.text, audit.citation, revision_context=context
            )
        policy = propose_disposition(
            audit.deterministic_checks,
            judgment,
            source_access_tier=audit.source.access_tier,
            relation_confidence_threshold=settings.relation_confidence_threshold,
            alignment_confidence_threshold=settings.alignment_confidence_threshold,
        )
        return store.finish_revision(run, judgment, policy)
    except asyncio.CancelledError:
        store.fail_revision(
            run, "interrupted", "Evaluation was interrupted. Retry with the preserved feedback."
        )
        raise
    except TimeoutError:
        return store.fail_revision(
            run, "timeout", "Provider timed out. Your original proposal and feedback are preserved."
        )
    except ProviderError:
        return store.fail_revision(
            run,
            "provider_error",
            "Provider evaluation failed. Retry after checking provider availability.",
        )
    except (ValueError, TypeError, KeyError, AttributeError):
        return store.fail_revision(
            run, "invalid_response", "Provider returned an invalid structured judgment."
        )
    except Exception:
        # Do not leak provider response bodies, keys or source content through errors.
        return store.fail_revision(
            run, "evaluation_error", "Evaluation failed. Your feedback is preserved for retry."
        )
