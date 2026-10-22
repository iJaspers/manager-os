# Wit Invoice Reference Review

Public identity: `wit.invoice-reference-review`
Version: `0.1.2`
Status: **Public source preview, unranked**
License: **MIT**, scoped to this directory only. See LICENSE.
Published: 2026-10-22

## Purpose

Compare supplied invoice references and payment rows, flagging missing, duplicate, partial, overpaid and orphan candidates. It never posts accounting entries or verifies a deposit.

## Correction notice

Version 0.1.2 replaces 0.1.1 as the current preview. Stress tests found that 0.1.1 could normalize malformed quoted CSV and counted its 1 MiB limit in JavaScript characters, not UTF-8 bytes. Do not rely on 0.1.1 matching output; historical bytes remain unchanged. The correction requires strict CSV quote grammar and an actual UTF-8 byte limit. Review TEST_RESULTS.md for exact observed coverage rather than treating this notice as a safety certification.

## Setup and use

Download and unzip this directory’s bundle, then open tool.html locally in a modern browser. There is no build step and no external asset request.

Requirements: Node.js 18+ for tests; a modern browser to use the tool. No credentials, external services, telemetry, accounts, or persistent browser storage are used by the tool.

### Exact input fit

Invoice CSV requires `invoice_id,amount`, with real known positive amounts in a single currency. References alone are not supported; missing amounts stay missing, not guessed or zero-filled. For no supplied payment rows, use the header-only CSV `invoice_id,amount,payment_id`. Empty payment text is invalid. `NO_PAYMENT_EVIDENCE` means no rows were supplied, not proof that an invoice is unpaid or a bank deposit is verified. Start with the fictional demo; never post real records to public feedback.

## Reproduce checks

From this version directory:

```sh
node test.js
node test_stress.js
```

See TEST_RESULTS.md for fresh observations. Source-reported tests for similarly numbered private tools are not inherited. Browser checks, where reported, cover synthetic inputs only, not real-world source verification. No independent community or maintainer-to-outsider round trip is claimed.

## Known limitations and unfinished work

Manual CSV only. Positive amounts in a single caller-selected currency. IDs are case-insensitive. No refunds, credits, FX, fuzzy matching or payment allocation. Supplied references are not authenticated. Maximum 1 MiB of UTF-8 and 10,000 data rows per CSV. Strict quoted fields reject trailing non-whitespace text after a closing quote and quotes inside unquoted data. Spreadsheet formula-like exported cells are prefixed with an apostrophe, so their displayed text may differ.

Next useful step: Add independently tested handling for credits/refunds as a separate opt-in input type, without turning candidate matching into verified accounting postings.

There are no known failing checks in this release’s stated suite; this is not a claim of comprehensive correctness or safety for untested inputs. Do not use it as tax, legal, payroll or financial advice.

## Changes from the private prototype

Fixed spreadsheet formula injection in CSV export; duplicate payment references now hold every affected invoice; duplicate/blank headers and aggregate overflow fail closed. Replaced examples with explicitly fictional data and added a bounded input size.

The original private file was retained unchanged. The public derivative contains no source-owner ledgers, personal/employer/customer records, private URLs, Library IDs, task IDs or credentials. Fixtures are synthetic and do not describe an actual person or business. Runtime source is self-contained; no third-party code/assets are bundled. Node/Python/browser runtimes retain their own licenses and are not included.

## Pick up, change, and hand off again

1. Start from this exact public ID and version. Read PROVENANCE.json and SHA256SUMS.json; the hashes establish byte consistency, not author identity.
2. Copy or fork the public source and keep LICENSE plus its copyright notice. MIT allows modification and redistribution, including commercial reuse. This does not license unrelated repository content or private originals.
3. Record your base commit/version, intended change, actual changed files, expected behavior and limits in a new CHANGELOG entry. Use synthetic fixtures only.
4. Make one bounded change, rerun the commands above, and include a failing-before/passing-after regression test. Keep unknown inputs unknown and preserve read-only behavior.
5. Prepare a unified patch with `git diff -- tools/invoice-reference-review/0.1.2` or a clearly versioned source bundle. Include test commands/results, known failures, dependency/license changes, setup, next step and rollback. Do not overwrite a published version in your distribution; release a new version and identify its parent.
6. Public GitHub pull-request intake is **OPEN ONLY for the three licensed public tool IDs listed in the current repository CONTRIBUTING.md**. Fork the repository, prepare a bounded change from the exact base version, and open a pull request using its public-tool template. Include changes, tests, known failures, unfinished work and license/provenance. Submit source and synthetic fixtures only, not private data or binary bundles. A maintainer first reviews privacy, licensing and unsafe behavior, then may run isolated manual tests; merge, version, catalogue updates and attribution require review. No automatic untrusted execution, auto-merge, exclusivity or response-time guarantee is implied. Framework-wide and security-sensitive intake remain closed.

A local simulated pickup/edit/retest/return-patch check and a controlled internal GitHub documentation canary are reported separately. It demonstrates the packaging path only, not another person’s use or acceptance. Anyone may continue their own MIT-licensed fork; a public fork does not imply upstream endorsement or merge approval.
