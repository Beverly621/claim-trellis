# Project charter

## Mission

ClaimTrellis helps a reviewer determine whether an identified source supports an
identified claim, while preserving enough provenance for another reviewer to reproduce
and challenge the result.

## Non-goals

The project does not:

- determine whether a claim is universally true;
- replace peer review, clinical judgment, legal review, or editorial accountability;
- infer author intent;
- treat a model's confidence as permission to act;
- bypass publisher access controls or redistribute protected papers;
- hide evidence retrieval failures inside a semantic verdict.

## Users

- AI and machine-learning researchers checking manuscripts before submission;
- peer reviewers and editors auditing citations;
- research-integrity teams triaging high-volume reviews;
- analysts checking white papers and technical reports;
- researchers studying calibrated claim-to-source verification.

## Core invariant

A final decision must be attributable to a human. A machine result may prioritize work,
surface evidence, or propose a disposition, but it cannot overwrite `human_review`.

## Product boundary

The unit of work is a `ClaimAudit`: one atomic claim, one identified source, zero or more
candidate passages, deterministic checks, model judgments, a policy proposal, and an
optional human decision.

## Definition of done for a public beta

1. A frozen benchmark protocol, annotation guide, and non-blind evaluation subset are public;
   the formal blind test labels remain private.
2. Retrieval recall, per-label metrics, calibration, coverage, and selective risk are
   reported for a pinned model and question-set version.
3. Thresholds are derived from validation data rather than copied from a cookbook.
4. Every displayed verdict has a source locator and provenance record.
5. Confidential documents can be processed without persistence and only selected passages
   leave the machine.
6. Security, privacy, licensing, incident response, and maintenance contacts are named.
