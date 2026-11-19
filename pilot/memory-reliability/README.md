# Memory Reliability Guard (experimental, not installed)

This isolated, original Python prototype adds a **fail-closed selection gate**, not a new memory database. It evaluates caller-supplied, already-authorized records. It does not retrieve, store, encrypt, synchronize, redact, or execute anything.

- Requires one active verified record per key; conflicting active records HOLD.
- Superseded and revoked records are excluded.
- Sensitive records HOLD until a separate host authorization flow exists.
- Source-commit mismatch HOLD; no claim of automatic Git monitoring.
- Completed actions SKIP; incomplete actions require atomic ownership and independent readback before execution.

Run: `cd pilot/memory-reliability && python -m unittest -v`

**Important:** This is not a production security boundary. A caller can lie about `verified`, `sensitive`, or commit IDs. No trust is established by these fields alone. No concurrent locking, persistence, privacy isolation, real-host dogfooding or cross-AI tests exist here. Integrate only after independent validation and explicit promotion.

## Combo-Breaker / adoption
Existing WIT continuity-observer already tests decision authority and claims, and adaptive-experience already guards profile imports. Do not duplicate those modules. This tiny guard explores only the missing pre-action *memory eligibility* decision. No SQLite, vector search, MCP server, or external package is justified yet. Third-party projects were inspiration only; no third-party code copied. Candidate status: **REVIEW**, not adopted.
