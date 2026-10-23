# Bill Calendar Preview

Public identity: `wit.bill-calendar-preview@0.1.0`
Release class: **UNVERIFIED WORK-IN-PROGRESS SOURCE, unranked, non-production**
License: **MIT for this sanitized tool directory only**; see LICENSE.
Prepared for source publication: 2026-10-23.

## Purpose and fit

Preview day-end cash balances and a separate same-day debit-first what-if from a supplied starting balance and dated entries. It never connects to a bank or moves money.

This source may be inspected, reused and continued even while unfinished. Passing the named local checks below does not mean it is verified for everyday reliance. Start with synthetic inputs and check results yourself.

## Source and download

Canonical version directory: `tools/bill-calendar-preview/0.1.0` in https://github.com/iJaspers/manager-os . The public catalogue at https://www.ijaspers.com/post/witburrow-tools provides the exact pinned source and ZIP links when this release is published. SHA256SUMS.json covers the files in this bundle; compare the whole-ZIP hash shown in the catalogue before unpacking. Older public versions must not be overwritten.

## Setup and use

Open tool.html in a modern browser with JavaScript and BigInt support. Start with the fictional values already present. Review the inputs, then click Check cash buffers. Enter one line per event: YYYY-MM-DD, signed dollars, optional short label. Positive amounts add cash; negative amounts subtract it.

The source uses no accounts, credentials, network APIs, telemetry or automatic remote execution. Inputs stay local unless you share them. Browser/session retention and your surrounding host are outside this tool's control. Clear sensitive values before sharing screenshots; do not send actual personal, employer, customer, tax or financial records with a contribution.

## Reproduce the stated checks

Run from this directory:

```sh
node test.js
```

17 Node VM/DOM-stub checks passed on 2026-10-22 and rerun for packaging on 2026-10-23. They cover labelled and legacy entries, exact-cent balances, opening/day-end/debit-first gaps, invalid dates/money/labels, 20-row and 8,192-character bounds, text-only output and static network/storage restrictions.

Not run or not established: independent rendered browser/mobile/device acceptance, broad fuzzing, comprehensive security review, real-world input verification and outsider pickup/handback. There is no community-adoption claim. See TEST_RESULTS.md for the precise evidence boundary.

## Known limitations, failures and unfinished work

Up to 20 nonempty entry lines and 8,192 JavaScript string characters, not bytes. Each amount must have at most six whole digits and two fractional digits; labels allow 1–40 plain characters and reject long digit sequences. This is a simple comma-separated format, not quoted CSV. It does not know actual posting order, pending holds, deposit availability, omitted bills, recurrence, bank holidays or live balances. Same-day debits-first is a conservative scenario, not a prediction or guarantee. Label checks are not comprehensive personal-data detection.

No failing check remains in the stated local suite at packaging time. That narrow observation is not a claim that the tool has no bugs. Unsupported cases above must not be silently treated as supported.

Next useful step: Add explicit recurring-event expansion as a separate, reviewable preview with an expansion cap and synthetic tests; never infer posting dates or silently write to accounts.

## Pick up, change and hand back

1. Record this exact public ID/version and verify the file hashes. Preserve an untouched copy.
2. Read the source and limits; choose your own local runtime and consent before running. Nothing in the library automatically installs or executes this tool.
3. Reproduce the supplied synthetic example/checks. Record any setup failures honestly.
4. Make one bounded change with a failing-before/passing-after fixture where possible; retain unknowns and the local-only boundary.
5. Release a new version in your fork rather than editing this immutable published directory. Include the exact parent version, changed files, setup, test commands/results, tests not run, known failures, next step and dependency/license provenance. Use HANDOFF_TEMPLATE.md as a starting point.
6. MIT permits your own fork and redistribution with its notice. Upstream acceptance is separate: check the current repository CONTRIBUTING.md and its exact allowlist before opening a pull request. This package does not independently widen that policy. If not in scope, keep a reviewable patch in your fork rather than submitting to a closed category. No automatic execution, merge, exclusivity, response-time promise or upstream endorsement is implied.

## Provenance and sanitization

PROVENANCE.json records the source component version and content hash without private Library/task locators. The private original is retained unchanged. Public copies remove private-build packaging and use fictional examples. No third-party code or assets are bundled; Node, Python and browser runtimes are not distributed here and retain their own licenses. The MIT grant does not apply to private originals, unrelated repository content or third-party services.
