# Wit Documented Compensation Comparison

Public identity: `wit.documented-compensation-comparison`
Version: `0.1.1`
Status: **Public source preview, unranked**
License: **MIT**, scoped to this directory only. See LICENSE.
Published: 2026-10-22

## Purpose

Evaluate documented-input hourly compensation scenarios with explicitly supported overtime, cash allowances, commute costs and dues. Outputs are before tax and never verify an offer.

## Setup and use

Download and unzip this directory’s bundle. Run python3 tool.py --input example.json. No pip packages are needed. Inputs and output stay local unless you share them.

Requirements: Python 3.9+; standard library only. No credentials, external services, telemetry, accounts, or persistent browser storage are used by the tool.

## Reproduce checks

From this version directory:

```sh
python3 tool.py --self-test
python3 -m unittest -v test_tool.py
```

See TEST_RESULTS.md for fresh observations. Source-reported tests for similarly numbered private tools are not inherited. Browser checks, where reported, cover synthetic inputs only, not real-world source verification. No independent community or maintainer-to-outsider round trip is claimed.

## Known limitations and unfinished work

CAD and hourly pay only. All numeric fields must be finite, non-negative and at most 1,000,000,000; input numeric strings are capped at 64 characters. No salary, taxes, noncash benefits, statutory entitlement or automated evidence verification. Ranking requires at least two complete uniquely named scenarios; a single scenario remains unranked.

Next useful step: Add a separate annual-salary scenario type with explicit missing-data behavior and tests. Preserve the no-guessed-benefits and no-automatic-offer-verification boundary.

There are no known failing checks in this release’s stated suite; this is not a claim of comprehensive correctness or safety for untested inputs. Do not use it as tax, legal, payroll or financial advice.

## Changes from the private prototype

Replaced illustrative pay values with synthetic values, assigned an unambiguous public identity, bounded numeric input to avoid Decimal failures and rejected impossible daily commute duration.

The original private file was retained unchanged. The public derivative contains no source-owner ledgers, personal/employer/customer records, private URLs, Library IDs, task IDs or credentials. Fixtures are synthetic and do not describe an actual person or business. Runtime source is self-contained; no third-party code/assets are bundled. Node/Python/browser runtimes retain their own licenses and are not included.

## Pick up, change, and hand off again

1. Start from this exact public ID and version. Read PROVENANCE.json and SHA256SUMS.json; the hashes establish byte consistency, not author identity.
2. Copy or fork the public source and keep LICENSE plus its copyright notice. MIT allows modification and redistribution, including commercial reuse. This does not license unrelated repository content or private originals.
3. Record your base commit/version, intended change, actual changed files, expected behavior and limits in a new CHANGELOG entry. Use synthetic fixtures only.
4. Make one bounded change, rerun the commands above, and include a failing-before/passing-after regression test. Keep unknown inputs unknown and preserve read-only behavior.
5. Prepare a unified patch with `git diff -- tools/documented-compensation-comparison/0.1.1` or a clearly versioned source bundle. Include test commands/results, known failures, dependency/license changes, setup, next step and rollback. Do not overwrite a published version in your distribution; release a new version and identify its parent.
6. Public GitHub pull-request intake is **OPEN ONLY for the three licensed public tool IDs listed in the current repository CONTRIBUTING.md**. Fork the repository, prepare a bounded change from the exact base version, and open a pull request using its public-tool template. Include changes, tests, known failures, unfinished work and license/provenance. Submit source and synthetic fixtures only, not private data or binary bundles. A maintainer first reviews privacy, licensing and unsafe behavior, then may run isolated manual tests; merge, version, catalogue updates and attribution require review. No automatic untrusted execution, auto-merge, exclusivity or response-time guarantee is implied. Framework-wide and security-sensitive intake remain closed.

A local simulated pickup/edit/retest/return-patch check and a controlled internal GitHub documentation canary are reported separately. It demonstrates the packaging path only, not another person’s use or acceptance. Anyone may continue their own MIT-licensed fork; a public fork does not imply upstream endorsement or merge approval.
