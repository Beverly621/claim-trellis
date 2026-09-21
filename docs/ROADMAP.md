# Roadmap

## Phase 0 — trust foundation

- Project charter, trust specification, data model, threat model, and privacy boundary.
- Versioned questions and fail-closed policy.
- Curated recent-literature seed and benchmark schema.

## Phase 1 — local alpha

- Parser, chunker, citation detection, lexical retrieval, deterministic checks.
- Provider interface and Jev adapter with retry, validation, usage tracking, and pinned model.
- SQLite audit history, CLI, REST API, and review interface.
- Unit, integration, and secret-free CI tests.

## Phase 2 — measured research preview

- Domain annotation guide and double-annotated benchmark.
- Hybrid BM25/embedding retrieval and retrieval ablations.
- Threshold fitting on validation data; untouched source-level test split.
- Reproducible model/prompt comparison reports.

## Phase 3 — controlled team pilot

- Authentication, authorization, encrypted storage, retention controls, deletion workflow.
- Worker queue, quotas, budgets, observability, backups, and incident response.
- Manual source-identity confirmation and expert escalation.

## Phase 4 — public release

- Independent validation and published limitations.
- Signed releases, SBOM, dependency scanning, and security reporting contact.
- Optional hosted profile only after privacy and legal review.
