# Wit Pretax Role Comparison

Public identity: `wit.pretax-role-comparison`
Version: `0.1.2`
Status: **Public source preview, unranked**
License: **MIT**, scoped to this directory only. See LICENSE.
Published: 2026-10-22

## Purpose

Compare two manually entered hourly or salary cash scenarios and commute costs, before tax, without silently treating unknown terms as zero.

## Correction notice

Version 0.1.2 corrects an extreme numeric-range defect in 0.1.1: two finite scenario values could yield an infinite difference while still being marked calculated. The comparison now returns UNKNOWN when either difference is non-finite and displays the explicit range warning. Historical versions remain unchanged. This is a numerical guard, not financial or offer verification.

## Setup and use

Download and unzip this directory’s bundle, then open tool.html locally in a modern browser. There is no build step and no external asset request.

Requirements: Node.js 18+ for tests; a modern browser to use the tool. No credentials, external services, telemetry, accounts, or persistent browser storage are used by the tool.

## Reproduce checks

From this version directory:

```sh
node test.js
node test_handlers.js
```

See TEST_RESULTS.md for fresh observations. Source-reported tests for similarly numbered private tools are not inherited. Browser checks, where reported, cover synthetic inputs only, not real-world source verification. No independent community or maintainer-to-outsider round trip is claimed.

## Known limitations and unfinished work

CAD-labelled planning inputs. No tax calculation, verified offer extraction, benefits valuation, overtime entitlement, pension, risk or resignation advice. Working and commute weeks share one input. Fractional weeks/days are allowed for planning. No automatic evidence checks or currency conversion.

Next useful step: Separate paid weeks from commute weeks, with backward-compatible inputs and tests covering paid leave. Do not infer tax, benefit or employment-rights rules.

There are no known failing checks in this release’s stated suite; this is not a claim of comprehensive correctness or safety for untested inputs. Do not use it as tax, legal, payroll or financial advice.

## Changes from the private prototype

Invalid booleans/objects and non-finite calculated results now fail closed; input labels are associated with controls. Removed private-build branding.

The original private file was retained unchanged. The public derivative contains no source-owner ledgers, personal/employer/customer records, private URLs, Library IDs, task IDs or credentials. Fixtures are synthetic and do not describe an actual person or business. Runtime source is self-contained; no third-party code/assets are bundled. Node/Python/browser runtimes retain their own licenses and are not included.

## Pick up, change, and hand off again

1. Start from this exact public ID and version. Read PROVENANCE.json and SHA256SUMS.json; the hashes establish byte consistency, not author identity.
2. Copy or fork the public source and keep LICENSE plus its copyright notice. MIT allows modification and redistribution, including commercial reuse. This does not license unrelated repository content or private originals.
3. Record your base commit/version, intended change, actual changed files, expected behavior and limits in a new CHANGELOG entry. Use synthetic fixtures only.
4. Make one bounded change, rerun the commands above, and include a failing-before/passing-after regression test. Keep unknown inputs unknown and preserve read-only behavior.
5. Prepare a unified patch with `git diff -- tools/pretax-role-comparison/0.1.2` or a clearly versioned source bundle. Include test commands/results, known failures, dependency/license changes, setup, next step and rollback. Do not overwrite a published version in your distribution; release a new version and identify its parent.
6. Public GitHub pull-request intake is **OPEN ONLY for the three licensed public tool IDs listed in the current repository CONTRIBUTING.md**. Fork the repository, prepare a bounded change from the exact base version, and open a pull request using its public-tool template. Include changes, tests, known failures, unfinished work and license/provenance. Submit source and synthetic fixtures only, not private data or binary bundles. A maintainer first reviews privacy, licensing and unsafe behavior, then may run isolated manual tests; merge, version, catalogue updates and attribution require review. No automatic untrusted execution, auto-merge, exclusivity or response-time guarantee is implied. Framework-wide and security-sensitive intake remain closed.

A local simulated pickup/edit/retest/return-patch check and a controlled internal GitHub documentation canary are reported separately. It demonstrates the packaging path only, not another person’s use or acceptance. Anyone may continue their own MIT-licensed fork; a public fork does not imply upstream endorsement or merge approval.
