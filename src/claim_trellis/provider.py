from __future__ import annotations

from typing import Protocol

from claim_trellis.models import JudgmentResult


class ProviderError(RuntimeError):
    """A structured judgment provider could not produce a valid result."""


class JudgmentProvider(Protocol):
    """Vendor-neutral boundary for semantic claim-to-source judgments."""

    provider_name: str
    model_name: str
    question_set_version: str

    async def evaluate(
        self, claim: str, evidence: str, citation: str | None = None
    ) -> JudgmentResult: ...
