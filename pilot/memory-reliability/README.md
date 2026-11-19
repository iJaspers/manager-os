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


## 2026-11-19 trusted-ingestion adapter checkpoint
Added `trusted_ingestion.py` and `test_trusted_ingestion.py` (ten additional negative/positive cases). Adapter requires a separate manifest explicitly marked authenticated, with exact scope, approved digest, classification and source revision. It rejects self-asserted `verified` fields and record payloads.

**Security caveat:** `authenticated=True` is still just caller-supplied data. The adapter cannot independently verify identity, signatures, permissions, or trusted storage. It must not be used with an authority manifest obtained from the same untrusted source as the record. This is a contract test, not a complete trusted ingestion implementation.

**Test status:** New ten-case suite committed, but not executed in this session: local GitHub clone failed due to DNS. Earlier 20-case local result is a prior snapshot, not a current branch-wide test result. Do not merge or promote. Next gate: materialize the exact branch in an executable environment, run both suites, test forged authenticated manifests and concurrent/restart scenarios, then inspect independent host traces.
