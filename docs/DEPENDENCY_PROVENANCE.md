# Dependency and provenance review

Reviewed 2026-09-21 for the v0.1 source release.

## Repository provenance

- The ClaimTrellis application code, tests, web interface, schemas, and documentation in
  this repository were authored for this project.
- No third-party application source tree, UI asset, publisher PDF, or proprietary dataset
  is vendored in the repository.
- The TypeSafe citation-check cookbook informed the verification pattern; ClaimTrellis
  uses an independent implementation and the public TypeSafe HTTP API.
- Benchmark evidence fields are concise editor-authored paraphrases with source metadata
  and locators. They are not copied article bodies and do not replace the original source.

## Direct runtime dependencies

Licenses below come from the installed distribution metadata used for the v0.1 verification
build. Dependencies are referenced through `pyproject.toml`, not copied into the source
repository.

| Distribution | Verified version | Declared license |
|---|---:|---|
| FastAPI | 0.141.1 | MIT |
| HTTPX | 0.28.1 | BSD-3-Clause |
| Pydantic | 2.13.5 | MIT |
| pydantic-settings | 2.15.0 | MIT |
| pypdf | 6.19.0 | BSD-3-Clause |
| python-docx | 1.2.0 | MIT |
| python-multipart | 0.0.32 | Apache-2.0 |
| Rich | 14.3.4 | MIT |
| Typer | 0.27.2 | MIT |
| Uvicorn | 0.53.0 | BSD-3-Clause |

Transitive dependencies and container operating-system packages retain their own licenses.
Release engineering should generate an SBOM and review the resolved dependency graph for
each tagged build because the permitted version ranges can resolve differently over time.

This inventory records engineering provenance; it is not legal advice or a trademark
clearance.
