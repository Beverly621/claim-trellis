# Evaluation protocol

## Purpose

Evaluation measures the entire workflow and its separable components. A good final score
must not conceal failed retrieval, missing sources, or excessive human-review volume.

## Dataset construction

1. Freeze source versions and record DOI/PMID/URL, journal, year, access tier, and locator.
2. Write one atomic claim per case.
3. Include all six relationship labels: supports, partially supports, contradicts,
   not addressed, insufficient context, and source unavailable.
4. Include hard negatives differing in population, endpoint, direction, causal framing,
   duration, or numeric value.
5. Use two independent domain-aware annotators and a third adjudicator for disagreement.
6. Split by source, not case, so paraphrases from one article cannot leak across splits.
7. Keep the held-out test labels inaccessible to prompt and threshold development.

## Required reports

- retrieval Recall@1, Recall@5, and mean reciprocal rank;
- confusion matrix and per-label precision, recall, and F1;
- high-confidence false-support rate;
- Brier score for the supported probability;
- expected calibration error with published bins;
- coverage and selective risk at every proposed threshold;
- results stratified by field, journal, access tier, evidence length, and failure type;
- latency, input tokens, provider errors, and retry counts.

## Release gate

The initial safety target is a false-support rate below 1% on an adjudicated held-out
benchmark. It is an evaluation target, not a product promise. Automatic acceptance stays
disabled throughout v0.1 regardless of measured confidence. Clinical and publication use
require independent external validation.

## Seed benchmark limitation

The included seed is for schema, pipeline, and regression testing. Its cases are
editor-authored from recent authoritative literature, but it is too small and not
independently double-annotated. It must never be used for a marketing accuracy claim.
