# Architecture

## Data flow

```text
uploaded source
  -> local parser
  -> normalized document + stable locators
  -> deterministic chunking
  -> lexical candidate retrieval
  -> exact quote and numeric checks
  -> selected short evidence passage
  -> one provider request with parallel atomic questions
  -> explicit policy proposal
  -> human review
  -> append-only audit record and export
```

## Components

- `ingestion.py`: text, Markdown, PDF, and DOCX extraction with upload limits.
- `citations.py`: sentence segmentation and citation-marker discovery.
- `chunking.py`: paragraph-aware, overlapping passages with stable locators.
- `retrieval.py`: deterministic BM25-style candidate ranking.
- `deterministic.py`: quote location, normalized hashes, and numeric checks.
- `provider.py`: vendor-neutral structured judgment protocol and error boundary.
- `providers/typesafe_jev.py`: default TypeSafe Jev adapter, retries, typed requests, and validation.
- `policy.py`: versioned, fail-closed composition of independent signals.
- `audit.py`: orchestration and provenance construction.
- `storage.py`: SQLite records and append-only event stream.
- `metrics.py`: benchmark and calibration measurements.
- `api.py`: REST boundary and static review interface.
- `cli.py`: local and automation-friendly commands.

## Why retrieval precedes structured judgment

The semantic provider is not used as a long-document search engine. The retriever reduces
the source to short candidate passages; the provider judges each relevant relationship.
Retrieval recall and semantic judgment quality are measured separately. The default Jev
adapter sends independent questions over shared state in one request.

## Why numbers stay in code

Numeric precision, counting, date ordering, and unit conversion are deterministic tasks.
They remain in code because the provider's value is semantic judgment, not arithmetic.

## Deployment profiles

- **Local workstation**: default; SQLite and uploads remain local.
- **Controlled team service**: TLS reverse proxy, encrypted volume, access control,
  retention policy, worker queue, and organization-managed TypeSafe key required.
- **Public demo**: sample/public documents only; no persistence; per-IP limits; no shared
  provider key without spend controls.

The initial release implements the local profile. Team and public profiles require the
controls listed in the roadmap.
