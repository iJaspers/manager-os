# Contributing to Witburrow

## Current status — 2026-10-24

**Scoped public-tool pull-request intake is OPEN for exactly these MIT-licensed public tools:**

- `wit.invoice-reference-review`
- `wit.pretax-role-comparison`
- `wit.documented-compensation-comparison`
- `wit.bill-calendar-preview` (unverified WIP source)
- `wit.field-hours-review` (unverified WIP source)
- `wit.grocery-planning-preview` (unverified WIP source)
- `wit.two-source-csv-reconciler` (unfinished source, known CSV parser issue)
- `wit.regression-plan-forge` (unfinished source, known CSV parser issue)
- `wit.dependency-critical-path-mapper` (unfinished source, known CSV parser issue)

The three Everyday WIP packages are 0.1.0, explicitly unverified and non-production. Source and handoff completeness are separate from functional acceptance. Current original preview versions: Invoice Reference Review 0.1.2; Pretax Role Comparison and Documented Compensation Comparison 0.1.2. Invoice 0.1.1 has known malformed-CSV and UTF-8 size-limit defects; use the corrected current version. The general framework contribution intake and private security-reporting lane remain CLOSED. The manifest’s legacy `contribution_intake: closed` still describes that general framework lane; the explicit `extensions.public_tool_contributions` record describes this narrower open lane. This dated policy supersedes older closed-intake text inside historical packages only for these nine IDs.

The three additional 0.1.0-draft.1 handoffs retain a reproduced CSV bare-quote parser defect. They have bounded static and Node checks, not current rendered-browser or independent outsider acceptance. The full descriptive inventory is not an intake allowlist.

## Public route

Fork this public repository, prepare a bounded source change and open a pull request to `main` using the public-tool template. The existing route is https://github.com/iJaspers/manager-os/compare . A GitHub account is needed to submit; no account is needed to read source or download a published bundle. No new form, service, credentials, permissions, payment or automatic intake job is created.

Accepted scope: source, documentation, synthetic fixtures and tests for the nine IDs above. Preserve exact tool identity and base version. Do not submit binary packages, archives, executables, unrelated tools, private ledgers or changes to workflows, permissions, credentials, the stable framework or its checksummed artifacts through this lane. An out-of-scope proposal is not authority to expand it.

## Required handoff

Include tool ID, base version and commit, purpose, changed files, source/dependency/license provenance, setup, exact test commands and observed results, known failures, unfinished work, next useful step and rollback. Distinguish tested behavior from claims. Use the repository pull-request template. State the public name/handle to credit, or request no attribution. No invented contributor counts, ratings, endorsements, exclusive claims or response deadlines.

Contribute only material you are authorized to provide under the tool’s MIT license. Preserve copyright and license notices. Identify every third-party component and its compatible license; an unknown or incompatible license holds that component rather than silently relicensing it. The scoped MIT grant does not cover unrelated repository contents, private originals, books, personal data or third-party assets.

## Privacy and safety gates before any execution

All submitted content and links are untrusted. First review the diff as text for personal/employer/customer/tax/financial data, credentials, private URLs/IDs, hidden assets, unsafe behavior, new dependencies and license/provenance. Do not follow arbitrary submitted links or run submitted code merely because it is in a PR. Secrets, real records and security-sensitive reports must never be put in public issues or PRs; the private reporting lane is not open.

Only after that review may a maintainer choose a bounded isolated manual test with synthetic data, no secrets or privileged account access, no network unless separately justified and authorized, and no writes outside disposable test fixtures. Failed, ambiguous or unavailable checks remain explicit holds. Existing human approval and host permission rules still apply.

## Review, merge, version and handback

`UNTRUSTED -> TEXT/PRIVACY/LICENSE/SAFETY REVIEW -> ISOLATED MANUAL TEST -> REVIEWED DECISION -> VERSIONED MERGE -> CATALOGUE/ATTRIBUTION READBACK`

No automatic execution of untrusted pull requests and no auto-merge are enabled by this policy. The existing manual read-only canary workflow is not a public-tool CI or a proof of tool safety. Do not add or trigger a workflow as a side effect of a submission.

Before merge, record what was reviewed, the exact test scope, known limitations, approval and rollback. Release a new tool version, preserve prior source/ZIP history and hashes, then update the public catalogue, download links and agreed contributor credit. Verify saved source and published bytes/links. A maintainer may request changes, decline, or park a contribution; publication does not mean someone must maintain it forever.

A small internal documentation-only canary exercises this route. It is not an outsider contribution, independent security review, production integration or community adoption.


