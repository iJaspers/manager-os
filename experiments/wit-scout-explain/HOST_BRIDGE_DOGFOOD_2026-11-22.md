# WIT Scout: controlled host bridge and live-source replay (2026-11-22)

STATUS: EXPERIMENTAL; draft PR #14. No merge, website edit, external post, purchase, or stable release.

## Delivered

- trusted_host_bridge.py accepts search candidates only through existing provider_adapter/scout ranking; it can retrieve up to six sources through an explicitly supplied trusted-host callback. There is no network client inside this module.
- It binds the requested URL to the host read, rejects invalid and cross-host final redirects, limits content through existing evidence_gate, requires a timezone-qualified observation time and a host provider reference, and returns SHA-256 text receipts. Error messages are reduced to exception classes.
- Untrusted provider fields such as fetched/host_verified cannot establish that a page was retrieved; the trusted host callback is responsible for actually reading it and enforcing public-IP DNS, redirects and tool permissions.
- test_trusted_host_bridge.py adds 12 regression/adversarial checks. The local suite passed 48/48 tests: 36 carried forward from the Nov 22 source-claim build plus 12 bridge tests. No third-party runtime dependency.

## Live-data dogfood boundary

Read the public WIT GitHub README through the connected GitHub tool (blob 76d3477289d46da1725513f28b9cbf5ab2f6429c) and the Reddit first-user discussion through a web tool:
- https://github.com/iJaspers/manager-os/blob/main/README.md
- https://www.reddit.com/r/sideprojects/comments/1y2akw2/i_can_be_your_first_user/

Manually transferred bounded excerpts of those actual reads into a local trusted-host callback fixture. This was a live-source replay, NOT automated live provider orchestration. The local receipt is WIT_Live_Source_Replay_Receipt_2026-11-22.json, sha256 cc87ef7fd94d2d8972b613a44629c35ca1586ce171ca4175e257efb7b24b3f10.

- Two source receipts; two exact-source quote matches; no failed handoffs.
- Provider-inserted malicious snippet was not shown as the fetched page description.
- Claim that a release was already completed was held for an independent action receipt.
- Deliberately contradictory statement about WIT being a separate AI model still returned REVIEW_REQUIRED because the source quote was present. Quote overlap does not check meaning.

## Independent-review decision

Keep deterministic source/hash checks as the first gate. For a second gate, require a semantic reviewer with access to both full claim and source context, explicit SUPPORTED/CONTRADICTED/UNKNOWN outputs, and an evidence-linked rationale. A model's self-reported independence is not proof of independence. Human/product owner approval remains separate. No new paid service, extra AI API, or autonomous judge was adopted.

Known blockers: real connector callback must be supplied in the host runtime; user-supplied metadata is not cryptographic attestation; semantic evaluator not integrated; GitHub/Reddit full-document native end-to-end has not been exercised in an unattended process. Tests are deterministic local fixtures, not independent security acceptance.

## Combo-Breaker and release gate

Reused the existing WIT Scout + Explain code, evidence_gate, provider_adapter, research_handoff and claim_review. No new task owner, agent, scheduler, external proxy, dependency or permissions. The host bridge must remain a review-only experiment until authorized live integration and independent security evaluation. Keep PR #14 as DRAFT, with no stable promotion.

NEXT: Trusted host fetch binding, independent semantic reviewer evaluation, and local-to-remote integrity/dogfood tests; require separate approval before merge or public release.
