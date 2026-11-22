# WIT research handoff + evidence check | Nov 22, 2026

**Status: EXPERIMENTAL / REVIEW ONLY.** Not a stable WIT feature, not independently reviewed, not approved for release. Adds source-first presentation and a deterministic quote/source-hash check to the existing Nov 19 Scout experiment. No third-party source code has been copied; the ideas are adapted from public project discussions. No paid dependencies or hosted account are required.

## What changed

- `claim_review.py` checks explicitly cited source URLs, verbatim text spans, SHA-256 document fingerprints and completed-action claims. Unknown evidence, missing quotes, a changed document or an unsupported completion claim returns `HOLD`. Even a completely matched research result returns **REVIEW_REQUIRED**, never automatically `APPROVE` or `DONE`.
- `research_handoff.py` ranks search results with the existing provider-neutral Scout and builds simple/practical/technical summaries. It distinguishes `SEARCH_SNIPPET_ONLY` from `HOST_FETCHED_TEXT` and includes claim-check results.
- `test_claim_review.py` adds 18 controlled checks, including adversarial source text, false completion, digest substitution, absent snippets and strict schema limits.

## Acceptance boundary

- The check proves only that the supplied quote exists in a particular supplied text version, and that its digest agrees with that text. It does **not** determine truth, semantic entailment, a completed action or publisher identity.
- The existing `host_verified` input is a caller-controlled boolean. It is **not** remote attestation and must be controlled by a trusted host integration; the module cannot secure DNS or redirects on its own.
- A source can contain prompt-injection instructions. Treat all source text as data and never delegate tool permissions to it. `build_handoff()` does not fetch, run code or grant write access.
- This is the deterministic first stage of a future independent reviewer, not the reviewer itself. An independent provider receipt and semantic review remain separate.
- No automatic import into WIT main, live Wix edits, stable release, CI claim or Reddit contact was made.

## Combo-Breaker decision

**ADOPT EXPERIMENTALLY:** enhance Nov 19 Scout + Explain instead of creating a separate search service, privacy proxy, scheduler, task owner or AI reviewer. Keep the existing source-linked handoff owner and Airlock. **DEFER:** provider orchestration, independent cross-model factual review, account-free website demo and live external usability tests until explicitly gated.

## Test evidence

Nov 22, 2026 local Python (offline): `python -B -m unittest discover -p 'test_*.py' -v` executed in the experimental directory: **36 passed** (18 previous Scout tests, 18 new). This confirms only the checked local fixtures. No live API orchestration, native mobile test, Windows test, independent code/security review or external user evaluation was performed. Rollback is simply not importing or merging these additive modules.
