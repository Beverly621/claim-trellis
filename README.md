# ClaimTrellis

**Auditable claim-to-source verification with human final judgment.**

ClaimTrellis is an independent open-source system for determining whether source evidence
supports written claims. It combines deterministic parsing and numeric checks, local
evidence retrieval, structured probabilistic judgments, and an explicit human decision
trail.

ClaimTrellis develops the citation-verification pattern demonstrated with TypeSafe Jev
into a general-purpose verification stack with deterministic retrieval, provider-neutral
structured judgment, provenance tracking, human adjudication, and reproducible audit
trails. Jev is the default provider, not the product identity.

The project is deliberately **not** marketed as an autonomous fact checker. It answers a
narrower and testable question: *does this identified source, in the supplied context,
support this claim?*

## Trust model

- Code owns file parsing, exact quote matching, numeric comparison, identifiers, dates,
  policy, and persistence.
- Retrieval narrows a source to short candidate passages before any model call.
- A provider interface supplies narrow semantic judgments; the default Jev adapter asks
  independent questions in parallel and never generates evidence.
- No model verdict becomes a final human verdict. Automatic acceptance is disabled by
  default until thresholds are validated on a domain-specific labeled dataset.
- Every result records its source locator, evidence text hash, question-set version,
  model version, probabilities, policy version, and reviewer action.

Read [the trust specification](docs/TRUST_SPEC.md) before deploying the software.

## Current capabilities

- Parse English `.txt`, `.md`, `.pdf`, and `.docx` files.
- Detect numeric and author-year citation markers and produce citation-bearing sentences.
- Split sources into stable, locator-preserving evidence passages.
- Retrieve candidate evidence using a deterministic BM25-style lexical ranker.
- Check exact quotes and numeric consistency in code.
- Ask the configured provider for relation, scope, population, causal-fidelity, and
  evidence-sufficiency judgments in one request.
- Distinguish `supports`, `partially_supports`, `contradicts`, `not_addressed`,
  `insufficient_context`, and `source_unavailable`.
- Apply a fail-closed decision policy and capture a final human review separately.
- Accept, reject, defer, or request a new provider proposal with human feedback; retain
  every proposal version and protect against stale or concurrent review actions.
- Persist audits in local SQLite with append-only audit events.
- Run through a CLI, REST API, or the included accessible review interface.
- Evaluate predictions with accuracy, per-label precision/recall/F1, Brier score, expected
  calibration error, coverage, and selective risk.

## Quick start

Requirements: Python 3.11 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
claim-trellis serve
```

Open `http://127.0.0.1:8000`. Without a provider API key the system runs its deterministic
checks and routes every semantic decision to human review.

To enable Jev for the current shell only:

```bash
export TYPESAFE_API_KEY='your-key-from-console.typesafe.ai'
claim-trellis serve
```

Do not place the key in source files. Local `.env*`, private uploads, databases, caches,
and evaluation outputs are ignored by Git.

## CLI examples

```bash
# Audit a claim against a local source. The output is JSON.
claim-trellis audit \
  --claim "The intervention reduced the primary composite cardiovascular endpoint." \
  --source paper.pdf \
  --citation "doi:10.1056/NEJMoa2307563"

# Validate and summarize the curated seed benchmark without calling Jev.
claim-trellis benchmark validate benchmarks/literature_seed.jsonl

# Run the pinned default-provider question set. Responses are cached locally.
claim-trellis benchmark run benchmarks/literature_seed.jsonl

# Score a JSONL predictions file against gold labels.
claim-trellis benchmark score \
  benchmarks/literature_seed.jsonl reports/local/predictions.jsonl
```

## API outline

- `GET /healthz` — health and model configuration, never the API key.
- `POST /api/v1/documents/parse` — parse an uploaded English source.
- `POST /api/v1/evidence/search` — return ranked candidate passages.
- `POST /api/v1/audits` — run deterministic and optional Jev checks.
- `GET /api/v1/audits/{audit_id}` — retrieve the full audit record.
- `POST /api/v1/audits/{audit_id}/reviews` — record the human decision.
- `POST /api/v1/audits/{audit_id}/revisions` — re-evaluate with feedback and an idempotency key.
- `GET /api/v1/audits/{audit_id}/proposals/current` — inspect the current proposal.
- `GET /api/v1/audits/{audit_id}/proposals` — inspect all proposal versions and lifecycle states.
- `GET /api/v1/audits/{audit_id}/revisions` — inspect revision attempts, including failures.
- `GET /api/v1/audits/{audit_id}/events` — retrieve the append-only audit trail.

Interactive API documentation is available at `/docs` while the service is running.
See [UI and review-loop contracts](docs/UI_AND_REVIEW_V1.md) for concurrency, migration,
and compatibility details.

## Seed literature benchmark

`benchmarks/literature_seed.jsonl` contains English cases derived from recent
(2022–2026) articles in high-authority journals including *Nature*, *Science*, *The New
England Journal of Medicine*, and *JAMA*. The repository stores metadata and concise
editor-authored paraphrases, not publisher PDFs. It is a smoke-test seed, not evidence of
clinical validity. See [the literature policy](docs/LITERATURE_POLICY.md) and
[evaluation protocol](docs/EVALUATION_PROTOCOL.md).

## Repository map

```text
src/claim_trellis/   Core engine, API, CLI, storage, and Jev adapter
web/                    Dependency-free review interface served by the API
tests/                  Deterministic unit and integration tests
benchmarks/             Schemas and recent authoritative literature seed cases
docs/                   Trust, architecture, evaluation, privacy, and threat model
.github/workflows/      Secret-free CI
```

## Security and privacy

Documents may be confidential or copyrighted. ClaimTrellis defaults to local parsing,
local persistence, and no telemetry. When the Jev adapter is enabled, the claim,
selected passage, and citation context are sent to TypeSafe. Revisions also transmit
human feedback, previous judgment, and deterministic-check context. Review provider terms and institutional policy
before processing unpublished or protected material. See [SECURITY.md](SECURITY.md) and
[docs/PRIVACY.md](docs/PRIVACY.md). The initial dependency and source review is recorded in
[docs/DEPENDENCY_PROVENANCE.md](docs/DEPENDENCY_PROVENANCE.md).

## Status

Alpha. The architecture and deterministic test suite are suitable for open development;
the included thresholds are conservative placeholders and are not validated for clinical,
legal, regulatory, or publication decisions.

## License

Apache-2.0. Contributors retain copyright and certify contributions under the
[Developer Certificate of Origin](DCO.md); no CLA is required.
