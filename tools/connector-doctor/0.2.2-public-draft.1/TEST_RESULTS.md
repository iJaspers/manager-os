# Local execution evidence — 2026-11-03

`node --test tools/connector-doctor/0.2.2-public-draft.1/*.test.mjs`: **147 passed, 0 failed, 0 skipped**, Node 24.22.1. Includes 129 preserved cases and 18 new authorization-boundary cases. The actual prior adapter was reproduced invoking a changed target when both the callback argument and caller request were changed during authorization; this version holds that case without invocation.

Checks include immutable pre-authorization intent, changed fields, frozen nested observations, callback replacement, expiry, clock rollback, post-invocation mutation, invalid accessors/fields and bounds. Existing cases cover the five connection states, denied/missing tools, copied/cross-host observations, exact action schema, credential rejection, stale/replayed approvals, wrong receipts, local preferences drift/backup/rollback and filesystem reads.

The current Bob verification supplement has 64 passing Node tests and imports this version. Promptfoo 0.125.1 passed 20 synthetic contract cases; MCP Inspector 2.13.0 passed five actual stdio fixture scenarios. These are not native ChatGPT/Gemini model or provider-account acceptance. Exact current and historical results are in the existing release directory, SHIP_TEST_RESULTS.json and REDDIT_TEST_RESULTS.json.

Release pipeline: 58 Python checks pass, including 39 preserved preflight checks, 12 recovered snapshot-helper checks and seven actual builder integration checks. Gitleaks 8.30.1 separately scanned the current public tree and existing PR commit range; its scope and controls are recorded in SHIP_REVIEW.md. No dependency-vulnerability clearance or independent security certification is implied.

Not run: live provider OAuth/writes, fresh ChatGPT/Gemini trials, mobile/Windows acceptance, SkillSpector execution or independent product/security acceptance. Live public entry-to-Bob navigation was manually observed in cloud Chrome, separate from the unavailable local Playwright rendered runner. Prior 22-test private baseline and six RC1 checks are retained historical evidence, not new runs counted here.
