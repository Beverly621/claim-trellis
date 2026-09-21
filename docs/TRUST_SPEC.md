# Trust specification

## Vocabulary

ClaimTrellis uses deliberately narrow language:

- **Supported**: the supplied evidence states or directly implies the atomic claim under
  materially aligned population, scope, direction, time, and causal framing.
- **Partially supported**: some material part is supported, but at least one independently
  meaningful component is absent or narrower.
- **Contradicted**: the evidence states or directly implies the opposite, including a
  reported null result where the claim asserts an effect.
- **Not addressed**: the available source evidence does not address the claim either way.
- **Insufficient context**: the available passage is too incomplete to decide.
- **Source unavailable**: the identified source could not enter a valid comparison.
- **Review required**: the pipeline cannot safely propose a substantive disposition.

None of these means that a claim is globally true or false.

## Separation of responsibilities

### Deterministic code

- file type and size validation;
- text normalization and stable hashing;
- citation-marker detection;
- quote existence and passage location;
- numeric token extraction and comparison;
- date filtering and source-age checks;
- retrieval, ranking, persistence, policy, and exports.

### Structured judgment provider

- semantic relation between claim and evidence;
- scope and population alignment;
- whether causal language overstates the evidence;
- whether the passage contains enough context for the requested judgment;
- whether source text contains an apparent prompt-injection attempt.

### Human reviewer

- confirms source identity and access completeness;
- inspects the cited passage in context;
- resolves ambiguous, high-stakes, or conflicting signals;
- owns the final decision and notes.

## Fail-closed rules

- A missing source, empty passage, missing claimed quote, request failure, malformed model
  answer, prompt-injection signal, or unvalidated policy always routes to review.
- Numeric checks can add warnings or block an automatic proposal; they cannot establish
  semantic support.
- Abstract-only evidence cannot establish that a full paper is silent.
- Model confidence is recorded as a property of a distribution, not truth probability.
- Until a policy is validated, `auto_accept_enabled` remains false.

## Versions

Every result records:

- application version;
- policy version;
- question-set version;
- retrieval version;
- requested and resolved model version;
- normalized claim and evidence hashes;
- UTC creation time.

Changing question wording, criteria, label mapping, retrieval scoring, or policy behavior
requires a version bump and regression report.

## Model policy

The default provider is TypeSafe Jev and the requested model is pinned to `jev-1.13.0`.
Release builds must not silently use `jev-latest`. A provider or model upgrade is evaluated
as a new system version.

The configured provider receives only the atomic claim, selected evidence passage,
citation metadata required for interpretation, and explicit question criteria. Whole
manuscripts are never sent.

## Decision policy

The initial policy is intentionally conservative:

- deterministic failure -> `evidence_missing` or `review_required`;
- high-confidence contradiction -> proposed `contradicted`;
- high-confidence support plus aligned scope/population/causal framing and sufficient
  context -> proposed `supported`;
- partial or missing coverage -> proposed `partially_supported` or `unsupported`;
- every proposal still requires human confirmation.

Threshold constants exist to make experiments reproducible, not to claim validation.
