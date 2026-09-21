## Change

Describe the user-visible or research-facing change.

## Trust impact

- [ ] No question, threshold, label, retrieval, or policy behavior changed.
- [ ] Behavioral changes include a version bump and regression evidence.
- [ ] No confidential source, API key, local database, or publisher PDF is included.
- [ ] Every commit includes a DCO `Signed-off-by` line (`git commit -s`).

## Verification

- [ ] `ruff check .`
- [ ] `mypy`
- [ ] `pytest --cov=claim_trellis`
