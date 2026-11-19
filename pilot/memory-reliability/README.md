# WIT Memory Reliability Guard | experimental security revision

Original dependency-free Python pilot. No I/O, memory store, embedding service, network calls, host actions or stable WIT changes.

Run: `python -m unittest -v` from this directory.

## Trust boundary
`select(records, key, source_commit, trusted_sources, scope)` only returns a record ID. Records are strict metadata-only dictionaries with exactly `id,key,status,source_commit`; no payload, privacy labels or caller-asserted verification flags are accepted. The separately supplied registry maps IDs to a canonical SHA-256 metadata digest, classification and scope. Missing/mismatched evidence, multiple active candidates, sensitive/unknown classification, and wrong source revisions HOLD. Completed checkpoint actions SKIP, otherwise require atomic claim and readback.

**CRITICAL LIMITATION:** A hash proves only equality. A malicious caller can construct both a record and matching registry. The registry must be assembled through independently authenticated, authorized ingestion, with separate classification and authorization; this pilot does not implement that boundary. It does not detect secrets in other data stores, encrypt memory, provide real Git monitoring, atomic multi-agent claims or durable recovery. Treat `use` as an eligibility hint, never permission to act.

## Evidence and adoption
Local Python 3 unittest execution on 2026-11-19: 20 tests, 20 pass, 0 errors (original ten behaviors plus adversarial checks). No independent real-host, concurrent-agent, cross-AI or security acceptance. The tests verify only the provided fixtures and logic. The previous two attack cases (forged verified flag and falsely labelled private payload) now reject unknown fields.

Combo-Breaker: Existing Continuity Observer and Adaptive Experience pilots already cover neighboring controls. Do not duplicate them or add SQLite/MCP/embeddings without measured need. Third-party community ideas are inspiration only; no third-party code copied.

**Decision: REVIEW / HOLD.** Draft PR only. No stable release, site, canonical records or external automation changes. Next gate: trusted ingestion design, negative integration tests, concurrency/recovery traces and fresh-host dogfood.
