# Privacy and data handling

## Local-first default

Parsing, chunking, retrieval, deterministic checks, SQLite persistence, and reports run on
the local machine. No document is uploaded merely by opening the interface.

## Provider transmission

When the default Jev adapter is configured with `TYPESAFE_API_KEY` and the user initiates
an audit, the service transmits:

- the atomic claim;
- one selected evidence passage;
- the minimum citation/source metadata needed for interpretation;
- the versioned question definitions.

When a reviewer explicitly requests a revision, the request additionally includes their
feedback, the previous structured proposal and policy reasons, deterministic checks,
source completeness, and parent/version references. Feedback is untrusted review context,
not replacement source evidence. Reviewer aliases are recorded locally, not included in
the provider's revision context.

It does not transmit the entire manuscript by design. Users must review TypeSafe's current
terms and institutional rules. Zero-data-retention requirements need an appropriate
provider agreement; the open-source software cannot create that agreement.

## Persistence

The local alpha stores audit records in SQLite. Raw uploads are parsed in memory and are
not retained unless a future deployment explicitly adds storage. Database paths, uploaded
documents, caches, and local reports are ignored by Git.

## Sensitive data

Do not process protected health information, personal data, confidential peer-review
material, or embargoed research until the operator has documented legal basis, retention,
access, deletion, incident response, and provider processing terms.
