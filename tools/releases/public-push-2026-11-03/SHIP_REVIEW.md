# Ship It & Dogfood — bounded continuation of PR #10

Starting head: `41108ab3da9788b72f9e19f16a0fa9c5502aa17c`. Main/RC1 base: `6fc0c50a5c93a6eefc66b60418d78541e98171bc`. Earlier October, November and PR receipts remain historical; this batch does not overwrite them. Current maintainer authorization covers safe generic licensed WIP publication on the existing review branch. Merge, website deployment, user installation updates and product/security acceptance remain separate.

## Exact publication scope

| Scope (exact paths/hashes in SHIP_FILES.json) | Rights and privacy decision | Release claim |
| --- | --- | --- |
| `tools/connector-doctor/0.2.2-public-draft.1/` and corresponding ZIP | Existing scoped MIT retained; original WIT repair; fictional fixtures | Successor with authorization-binding repair; 147 passing local cases; prior versions preserved |
| `integration/bob/verification-0.1.1-public-draft.1/` | Existing scoped MIT; source imports the repaired Doctor; no external runtime bundled | 64 local tests, 20 Promptfoo cases and five actual Inspector fixture scenarios; not native-host acceptance |
| `tools/source-linked-handoff-review/0.1.0-public-draft.1/` and corresponding ZIP | Original WIT-owned BOB-089 v1.0.1 traced by exact source/proof hash; generic public derivative under scoped MIT; fictional fixtures; private originals excluded | One new public tool listing, existing identity, zero new Bob build credits; 25 passing tests; structural review only |
| Existing release builder, preflight and snapshot tests plus SHIP receipts | Original WIT code under existing release-directory MIT; no third-party source copied | Captures/scans/packages identical bytes, refuses replacement of frozen releases; 58 passing tests |
| Existing catalogue, tool index and catalogue count assertion | Public metadata only, commit-pinned to verified downloads; no private identity expansion | Doctor successor and one additional WIP listing; no production-ready claim |

No repository-wide license is created. Retain each directory's copyright/license when redistributing. Public ZIPs contain source, tests, synthetic examples and scoped licenses; ZIP metadata/member checksums are inspected. No private operating document, credential, original backlog bundle, account identifier or task record enters this batch.

## Concrete defects and repairs

The actual prior builder scanned source, then reread it to package it. A disposable reproduction changed an existing member and added another after scanning: both unscanned bytes entered its ZIP. The recovered original snapshot helper was integrated into the production scanner/builder, with an immutable captured-byte mapping, deterministic ZIPs and exclusive create-or-identical-readback behavior. Seven production integration cases supplement the recovered 12 helper cases and 39 existing preflight cases. Existing planning-tool ZIPs remain byte-identical. This is a trusted local release-workspace utility, not a malicious same-user filesystem or multi-package transaction boundary.

The actual prior read adapter allowed an authorization callback to change both the callback request and original target before binding the request. It then invoked the changed target and reported VERIFIED. The successor fixes intent before any callback/await, freezes observations, pins trusted callbacks, rechecks caller intent/capabilities, rejects a changed request and enforces a five-minute local read-check window. The host still owns permission and real response authenticity. Historical 0.2.0/0.2.1 adapters retain this defect; use 0.2.2 for new authorization-sensitive trials, or conversation-only fallback.

BOB-089 retains its original generic handoff logic, with bounded input, strict flags/time syntax, duplicate-key rejection, final-symlink refusal and useful HOLD exit status. It does not authenticate linked evidence, approve work or execute writes. A separately discovered same-numbered BOB-090 variant was not promoted because its proof/source lineage did not match.

## Dogfood and Combo-Breaker decisions

Followed the existing public Bob RC1 instructions and Combo-Breaker reuse/owner/evidence rules. The bounded task was to prepare this existing PR's review handoff, using the real GitHub metadata tool, Doctor preflight/result consistency, BOB-089 proposal check and a saved output. The live Wix entry was rendered in cloud Chrome and its Bob RC1 link followed successfully. No new Bob, workflow engine, owner, memory store or scheduled job was created.

`SHIP_DOGFOOD.json`, the actual input/result and portable resume card retain the evidence. A fresh local process checks the saved output hash and rechecks capabilities; durable GitHub readback is recorded after publication. This is current-session assistant dogfooding, not a fresh ChatGPT/Gemini customer journey. No observed end-to-end user timing was captured; none is invented. Denial, unsupported hosts and copied access remain explicit negative cases in the retained Doctor/verification suites. A separate actual local preference apply/read/rollback demo also succeeded.

Combo-Breaker: **INTEGRATE** the recovered snapshot repair and BOB-089 public derivative; **REPAIR** the existing Doctor; **REUSE** existing tests, catalogue, Product task and private crosswalk; **HOLD** uncertain variants and broad private business/accounting originals; **ALREADY COVERED** additional orchestration, memory and progress stores. Previous candidate/license decisions remain in SIDEPROJECT_REVIEW.md and REDDIT_INTEGRATION_REVIEW.md; completed research is not repeated.

## Review and security evidence

Complete current PR candidate bytes and ZIP members were processed by the bounded WIT preflight; the initial complete pass covered 188 paths / 285 files and archive members with zero blocking findings. Its 35 source-risk flags (including duplicate archived code) were reviewed: fixed local test subprocesses, explicitly supplied reviewed optional CLIs, and the scanner's inert negative fixture. No scanned code is executed by preflight. Newly written receipts/manifests receive a final additional scan before publication. SHIP_PREFLIGHT.json records this scope; SHIP_FILES.json binds final new/changed bytes.

Gitleaks core 8.30.1 (MIT, Zachary Rice) was downloaded only from its official release. Both the release API digest and checksum list verified the Linux archive: `551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb`; binary SHA-256 `88f91962aa2f93ac6ab281d553b9e125f5197bbbce38f9f2437f7299c32e5509`. Zero findings in the six existing PR commits and current public worktree with archive depth 2. A clean fixture passed; a never-issued correctly shaped 36-character GitHub-token sentinel failed with github-pat. The first malformed 38-character sentinel was not detected and was corrected before validating the control. No binary or fake credential is redistributed. No claim about unscanned old repository history or authenticated publisher signing is made.

Optional Promptfoo/Inspector dependency audit was attempted but the npm advisory endpoint failed certificate validation. No TLS bypass, audit fix or dependency clearance is claimed. Existing dependency rights review remains incomplete for redistributing that optional runtime bundle, which is excluded. OSV-Scanner and CodeQL were not run. SkillSpector and Wayflow execution remain blocked by unavailable isolated no-network sandbox capability. Local Playwright rendered execution remains unavailable; cloud Chrome navigation is separately observed evidence.

PR reviews/threads and PR-triggered workflow runs were empty at the starting head. The only repository workflow, `.github/workflows/mos-gate-public-readonly.yml`, is an existing manual read-only canary, not WIT PR CI. It was inspected and preserved, not enabled or claimed passing. Local tests and scanners are not independent security acceptance. The recovered helper had prior independent narrow review; this sprint's additional implementation still requires the existing independent review gate.

## November 6 and rollback

Use the existing acceptance kit in fresh ChatGPT and Gemini sessions: open the one-link entry, inspect that host's actual tools, run one permitted fictional task, deny another, verify unsupported-host conversational fallback, then save/resume through that host's real storage and independently compare the output. Confirm user isolation and changed/expired authorization denial. Current host success is not transferable access or universal compatibility.

Rollback: stop the optional successor commands, preserve their evidence, and revert this batch's reviewed commits normally if needed. Do not force-push or overwrite old releases. Before merge, closing/reverting the review branch leaves frozen main RC1 untouched. Avoid reverting security-sensitive execution to the known-defective older Doctor; use conversation-only fallback while repairing. No global configuration, service, subscription, website or account change needs undoing. Exact source/publication commits and download verification follow in SHIP_RELEASE_RECEIPT.json; the final merge packet identifies the head to approve without authorizing deployment.
