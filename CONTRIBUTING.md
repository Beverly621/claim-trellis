# Contributing

ClaimTrellis accepts changes that preserve its fail-closed trust model.

1. Open an issue describing the failure mode or capability.
2. Create a dedicated branch; never commit directly to, delete, or force-push `main`.
3. Add or update a representative test before changing policy or question wording.
4. Run `ruff check .`, `mypy`, and `pytest --cov=claim_trellis`.
5. Open a pull request and merge only after the `test` CI check succeeds.
6. Never include API keys, unpublished manuscripts, private reviews, downloaded publisher
   PDFs, or local benchmark outputs.
7. A question-set or policy change must bump its explicit version and document expected
   behavioral impact.
8. Sign every commit under the [Developer Certificate of Origin](DCO.md) with
   `git commit -s`. ClaimTrellis uses a DCO and does not require a CLA.

Contributors retain copyright in their contributions and license them under Apache-2.0.

Model-quality claims require a frozen labeled dataset, a pinned model version, the exact
question set, and a reproducible metrics report. Screenshots and cherry-picked examples
are not sufficient.
