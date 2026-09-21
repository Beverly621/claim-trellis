# ClaimTrellis v0.1 decisions and release gates

**Current status: ClaimTrellis v0.1 — Feature Frozen / Private Pre-Release**

The v0.1 product direction is frozen. ClaimTrellis is an independent project and its only
primary brand. TypeSafe Jev is the first structured judgment provider and part of the
technical lineage, not the product identity.

## Feature-freeze policy

The product features, external API, data model, CLI commands, provider architecture, and
six-label judgment system are frozen. The repository must remain private. Do not publish
to PyPI, create a formal release, or perform promotional activity. New features and
nonessential dependency upgrades are paused.

Changes during the freeze are limited to:

- bug and security fixes;
- test, CI, type-checking, and reliability improvements;
- refactoring that does not change external behavior;
- documentation and benchmark preparation;
- UI refactoring explicitly requested by the repository owner; and
- domain or Vercel deployment configuration explicitly requested by the repository owner.

Do not run or claim the `<1% false-support rate` target without a formally adjudicated,
held-out benchmark. Do not change the brand, positioning, license, or release strategy
without an explicit decision from the repository owner.

| Area | v0.1 decision |
|---|---|
| Display name | ClaimTrellis |
| Repository and distribution | `claim-trellis` |
| Python package | `claim_trellis` |
| CLI | `claim-trellis` |
| Environment prefix | `CLAIM_TRELLIS_` |
| Local data directory | `.claim-trellis/` |
| License | Apache-2.0 |
| Contribution governance | DCO; no CLA |
| Copyright | Contributors retain copyright |
| Primary users | Researchers and editorial reviewers |
| First domain | AI and machine-learning research |
| Second domain | Biomedical and life-science research |
| Semantic judgment | Provider interface; TypeSafe Jev is the default adapter |
| Relation labels | `supports`, `partially_supports`, `contradicts`, `not_addressed`, `insufficient_context`, `source_unavailable` |
| Automatic acceptance | Disabled for v0.1 |
| Final judgment | Always human-confirmed |
| Privacy | Local-first, no telemetry, minimum necessary provider payload |
| Evaluation safety target | False-support rate below 1% on an adjudicated held-out benchmark; not a product claim |
| Benchmark adjudication | Two independent annotators; third-party resolution of disagreements |
| Public history | New clean repository; private development repository retained as an archive |
| Blind test | Kept private |
| Public positioning | Verification/review infrastructure, never autonomous fact checking |

## Human release gates

The following require accountable human action before or during release:

1. Complete PyPI, GitHub, web, USPTO, WIPO, and target-market name checks. A free package
   name is not a trademark clearance.
2. Review actual source and dependency provenance. Copying code or assets can create
   license obligations even when public Git history starts clean.
3. Enable GitHub Private Vulnerability Reporting. Do not publish a personal email merely
   to fill a template field.
4. Appoint benchmark annotators and an adjudicator before making accuracy claims.
5. Review TypeSafe terms and institutional policy before sending confidential,
   unpublished, personal, or protected material.
6. Do not publish a performance claim until a frozen held-out evaluation is complete.

These gates do not block transparent experimental open-source publication. Releases must
remain `0.x experimental` until the validation and governance requirements are met.
