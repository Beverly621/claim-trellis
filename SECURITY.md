# Security policy

## Reporting a vulnerability

Use GitHub Private Vulnerability Reporting for this repository. Do not open a public issue
containing an unpatched vulnerability, API key, manuscript, patient information, or
private source. A dedicated project address may be added after a project domain is
established; no personal email is published merely to fill this field.

## Secrets

- `TYPESAFE_API_KEY` is read only from the process environment.
- The API never returns the key or logs authorization headers.
- `.env*`, `*.key`, local databases, uploads, caches, and reports are ignored by Git.
- CI does not require or receive a production API key.

## Supported versions

Security fixes are provided for the current minor release until a formal release policy
is adopted.

## Deployment baseline

Run behind TLS, set explicit upload and request-size limits at the reverse proxy, restrict
the data directory to the service account, and do not expose a development server directly
to the internet. The built-in server is intended for local use and controlled evaluation.
