# WIT | Connected GitHub ingestion + conservative semantic gate | 2026-11-22

**Status:** Isolated EXPERIMENT, draft PR #14. Not merged into main, not live on Wix, not an installed WIT component, and not independently validated as secure.

## DONE

- Added `github_connector_adapter.py` and `test_github_connector_adapter.py`: a host-injected, read-only GitHub fetch callback is restricted to an explicit immutable commit/path allowlist. Recompute the Git blob SHA-1 against actual UTF-8 content; reject unexpected ref/path/response hashes, malformed targets, oversized source and untrusted target requests. The Python adapter does not have network access on its own.
- Added `github_host_runtime.mjs` and `test_github_host_runtime.mjs`: an asynchronous, host-native adapter calls the connected `mcp__GitHub__fetch_file` action from an injected host tool object, checks the pinned target and Git blob hash, then prepares an evidence object. No new service or token handling added. This adapter still requires a host to load it, choose the approved target list and connect the Python handoff. It is not automatically deployed by committing the source.
- Added `semantic_guard.py`, regression tests and an additive `research_handoff.py` precheck. Matched source quotes are **NEEDS_SEMANTIC_REVIEW**, never automatically declared correct; obvious inverted-polarity claims become **HOLD**; unsupported completed-action claims remain **HOLD**. The code also emits a bounded request packet for future independent review. It is a heuristic, not an independent language model or semantic proof.
- Current local execution: **71 Python unittest PASS**, **9 JavaScript node --test PASS**. Existing research handoff regression tests still pass. Remote Git blob readbacks matched the exact locally tested source for the changed files.
- Directly exercised the connected GitHub action on the public WIT SECURITY.md pinned to commit `57c8de2d5d7dc5b43e4108b36078c9b41e2be75a`. Recomputed Git blob hash matches provider `5c946ef0932b247ba1ec1bea905b02272d2143f0` for 1,325 bytes. Public source content was then captured into a local fixture and replayed through the new Python adapter. This confirms real source acquisition with offline replay, not an unattended continuous GitHub-to-Python pipeline.
- Replay reproduced 3 assertions: source-aligned statement -> NEEDS_SEMANTIC_REVIEW, positive claim contradicting “None of these authorize...” -> HOLD, fabricated completed action -> HOLD. A poisoned provider search snippet did not masquerade as the fetched text. Receipt artifact: `WIT_Github_Pinned_Connector_Review_Receipt_2026-11-22.json`.

## Test-driven correction

The first replay **failed** to detect “None of these authorize...” as a contradiction. Adding “none” initially falsely flagged a compatible “cannot authorize” claim. The guard was corrected to a conservative sentence-level polarity precheck and both examples became regression tests. It can still miss contradictions expressed through different vocabulary or multiple clauses. False positives remain possible. No independent semantic reviewer was invoked.

## Combo-Breaker

Reused existing Nov 19 Scout, Nov 22 claim review, handoff, evidence gate and host bridge. Added **one connector boundary** and **one review precheck**, not a second tool owner, external proxy, paid AI service, scheduler or public release. Third-party implementation code was not copied from the Reddit projects.

## NEXT ACTION

1. Have a trusted host execute the committed JavaScript adapter with explicitly approved immutable targets; pass the validated host result to the Python gate without accepting user-supplied attestation flags.
2. Run a separate independent semantic reviewer on a sanitized, public-source evaluation packet. Require authenticated reviewer provenance, evidence-linked SUPPORTED/CONTRADICTED/INSUFFICIENT verdicts, and measure errors against labelled examples before considering integration.
3. Independent code/security review, end-to-end restart and source-failure acceptance, then an explicit owner decision before merging or shipping.

## WAITING ON

A genuine deployed host runtime that can connect the async GitHub tool invocation to the Python gate; an independent, approved semantic reviewer (none has been invoked); and security/release approval. No email, outreach, spend, Wix change or public release performed.
