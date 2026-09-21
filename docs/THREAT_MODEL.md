# Threat model

## Protected assets

- confidential manuscripts and uploaded sources;
- provider API keys;
- reviewer identities and decisions;
- integrity of evidence, prompts, model results, and audit history;
- benchmark labels and held-out evaluation data.

## Principal threats and controls

| Threat | Initial control |
|---|---|
| Secret committed to Git | broad ignore rules, no config file, CI secret scan recommended |
| Prompt injection inside a paper | state treated as data, injection Noul, explicit criteria, review routing |
| Fabricated model quote | model never generates authoritative evidence; code locates source text |
| Retrieval miss | separate retrieval metrics, top-k display, manual passage selection |
| PDF parser confusion | file signatures, size limits, no macros, visible parser warnings |
| Citation/source identity mismatch | identifiers and metadata retained; human confirms source |
| Model/provider outage | bounded retries, explicit service-failure state, no silent fallback verdict |
| Benchmark contamination | source-level split, frozen hashes, private held-out labels |
| Reviewer history tampering | append-only events and content hashes |
| Cross-user data exposure | local-only initial profile; authentication required before team deployment |
| Cost exhaustion | request limits, passage limits, usage logging, optional per-project budget |

## Out of scope for the local alpha

Multi-tenant isolation, organization SSO, managed encryption keys, malware scanning,
distributed queues, and tamper-evident external logs are required before hosted service
deployment and are not claimed by the local alpha.
