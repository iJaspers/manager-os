# Field Hours Review

Public identity: `wit.field-hours-review@0.1.0`
Release class: **UNVERIFIED WORK-IN-PROGRESS SOURCE, unranked, non-production**
License: **MIT for this sanitized tool directory only**; see LICENSE.
Prepared for source publication: 2026-10-23.

## Purpose and fit

Calculate a draft shift length from clock start/end times, an explicit next-day checkbox and unpaid lunch minutes. It does not decide payroll or overtime eligibility.

This source may be inspected, reused and continued even while unfinished. Passing the named local checks below does not mean it is verified for everyday reliance. Start with synthetic inputs and check results yourself.

## Source and download

Canonical version directory: `tools/field-hours-review/0.1.0` in https://github.com/iJaspers/manager-os . The public catalogue at https://www.ijaspers.com/post/witburrow-tools provides the exact pinned source and ZIP links when this release is published. SHA256SUMS.json covers the files in this bundle; compare the whole-ZIP hash shown in the catalogue before unpacking. Older public versions must not be overwritten.

## Setup and use

Open tool.html in a modern browser. Review start/end times and lunch. Select End time is on the next day only for a shift crossing midnight, then click Calculate draft hours. Blank lunch is held; enter 0 only when that is the intended assumption.

The source uses no accounts, credentials, network APIs, telemetry or automatic remote execution. Inputs stay local unless you share them. Browser/session retention and your surrounding host are outside this tool's control. Clear sensitive values before sharing screenshots; do not send actual personal, employer, customer, tax or financial records with a contribution.

## Reproduce the stated checks

Run from this directory:

```sh
node test.js
```

13 standalone Node VM/DOM-stub checks passed on 2026-10-22 and rerun for packaging on 2026-10-23: same-day/overnight/midnight arithmetic, explicit overnight consent, malformed times, missing/fractional/excess lunch, 18-hour bound and static offline restrictions. An older private package also had an opener-integration check; that component is not included and that check is not claimed.

Not run or not established: independent rendered browser/mobile/device acceptance, broad fuzzing, comprehensive security review, real-world input verification and outsider pickup/handback. There is no community-adoption claim. See TEST_RESULTS.md for the precise evidence boundary.

## Known limitations, failures and unfinished work

Clock-time arithmetic only: no date, timezone or daylight-saving adjustment. Shifts over 18 hours, equal start/end times and ambiguous overnight entries are held. Lunch must be a whole 0–720 minutes and shorter than the shift. Decimal hours are rounded to two places; exact net minutes are also shown. Travel, paid breaks, rounding rules, employer policy and statutory overtime are not inferred. No employer upload or payroll submission exists.

No failing check remains in the stated local suite at packaging time. That narrow observation is not a claim that the tool has no bugs. Unsupported cases above must not be silently treated as supported.

Next useful step: Add an optional explicit date/timezone mode with daylight-saving regression fixtures while preserving the simple clock-time mode and its warning; do not infer paid-time entitlements.

## Pick up, change and hand back

1. Record this exact public ID/version and verify the file hashes. Preserve an untouched copy.
2. Read the source and limits; choose your own local runtime and consent before running. Nothing in the library automatically installs or executes this tool.
3. Reproduce the supplied synthetic example/checks. Record any setup failures honestly.
4. Make one bounded change with a failing-before/passing-after fixture where possible; retain unknowns and the local-only boundary.
5. Release a new version in your fork rather than editing this immutable published directory. Include the exact parent version, changed files, setup, test commands/results, tests not run, known failures, next step and dependency/license provenance. Use HANDOFF_TEMPLATE.md as a starting point.
6. MIT permits your own fork and redistribution with its notice. Upstream acceptance is separate: check the current repository CONTRIBUTING.md and its exact allowlist before opening a pull request. This package does not independently widen that policy. If not in scope, keep a reviewable patch in your fork rather than submitting to a closed category. No automatic execution, merge, exclusivity, response-time promise or upstream endorsement is implied.

## Provenance and sanitization

PROVENANCE.json records the source component version and content hash without private Library/task locators. The private original is retained unchanged. Public copies remove private-build packaging and use fictional examples. No third-party code or assets are bundled; Node, Python and browser runtimes are not distributed here and retain their own licenses. The MIT grant does not apply to private originals, unrelated repository content or third-party services.
