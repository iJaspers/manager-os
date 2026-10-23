# Grocery Planning Preview

Public identity: `wit.grocery-planning-preview@0.1.0`
Release class: **UNVERIFIED WORK-IN-PROGRESS SOURCE, unranked, non-production**
License: **MIT for this sanitized tool directory only**; see LICENSE.
Prepared for source publication: 2026-10-23.

## Purpose and fit

Combine explicitly supplied recipes, a meal plan, pantry quantities and package-price offers into a local grocery estimate. Missing prices stay unknown. No live store, ordering or account integration is included.

This source may be inspected, reused and continued even while unfinished. Passing the named local checks below does not mean it is verified for everyday reliance. Start with synthetic inputs and check results yourself.

## Source and download

Canonical version directory: `tools/grocery-planning-preview/0.1.0` in https://github.com/iJaspers/manager-os . The public catalogue at https://www.ijaspers.com/post/witburrow-tools provides the exact pinned source and ZIP links when this release is published. SHA256SUMS.json covers the files in this bundle; compare the whole-ZIP hash shown in the catalogue before unpacking. Older public versions must not be overwritten.

## Setup and use

Use Python 3.9+ with its standard library, no pip install. Run python3 tool.py example.json. The included file is fictional. Copy it before editing. Required top-level fields: budget_cad (decimal string), recipes, plan, pantry and offers (explicit lists). recipes and plan must not be empty. Explicit empty pantry/offers lists are allowed, but missing prices produce UNKNOWN_MISSING_PRICE, not a complete zero-cost basket.

The source uses no accounts, credentials, network APIs, telemetry or automatic remote execution. Inputs stay local unless you share them. Browser/session retention and your surrounding host are outside this tool's control. Clear sensitive values before sharing screenshots; do not send actual personal, employer, customer, tax or financial records with a contribution.

## Reproduce the stated checks

Run from this directory:

```sh
python3 -m unittest -v test_tool.py test_boundaries.py
python3 tool.py example.json
```

17 functional and 9 input-boundary/recovery checks passed on 2026-10-22 and rerun for packaging on 2026-10-23. These cover supplied-price arithmetic, missing prices/inputs, unit and identifier validation, exact-cent output, duplicate keys, invalid UTF-8, exact/over 1 MiB, depth, repeated calculations and invalid-to-valid recovery. This is local Python evidence, not device/production capacity acceptance.

Not run or not established: independent rendered browser/mobile/device acceptance, broad fuzzing, comprehensive security review, real-world input verification and outsider pickup/handback. There is no community-adoption claim. See TEST_RESULTS.md for the precise evidence boundary.

## Known limitations, failures and unfinished work

CAD-labelled decimal-string prices only, at most 100,000 per price/budget. Quantities and meal counts are bounded whole integers up to 1,000,000; units are g, ml or each with no conversion. CLI admission: 1 MiB UTF-8 JSON, 32 nesting levels, 100 recipes, 100 plan rows, 100 ingredients per recipe, 1,000 pantry rows and 1,000 offers. Duplicate JSON object keys are rejected. The in-memory calculate function receives already parsed objects and has no file-byte cap. Each item chooses one supplied pack offer, not mixed-pack optimization; ties use surplus and store identifier. Taxes, delivery, travel, promotions, availability, nutrition, allergies and measured savings are not evaluated. Error output is diagnostic; do not submit personal data in reports.

No failing check remains in the stated local suite at packaging time. That narrow observation is not a claim that the tool has no bugs. Unsupported cases above must not be silently treated as supported.

Next useful step: Add a bounded mixed-pack optimizer with a counterexample fixture where combining pack sizes improves the supplied-offer estimate, retaining explicit unknown prices and no live-price claim.

## Pick up, change and hand back

1. Record this exact public ID/version and verify the file hashes. Preserve an untouched copy.
2. Read the source and limits; choose your own local runtime and consent before running. Nothing in the library automatically installs or executes this tool.
3. Reproduce the supplied synthetic example/checks. Record any setup failures honestly.
4. Make one bounded change with a failing-before/passing-after fixture where possible; retain unknowns and the local-only boundary.
5. Release a new version in your fork rather than editing this immutable published directory. Include the exact parent version, changed files, setup, test commands/results, tests not run, known failures, next step and dependency/license provenance. Use HANDOFF_TEMPLATE.md as a starting point.
6. MIT permits your own fork and redistribution with its notice. Upstream acceptance is separate: check the current repository CONTRIBUTING.md and its exact allowlist before opening a pull request. This package does not independently widen that policy. If not in scope, keep a reviewable patch in your fork rather than submitting to a closed category. No automatic execution, merge, exclusivity, response-time promise or upstream endorsement is implied.

## Provenance and sanitization

PROVENANCE.json records the source component version and content hash without private Library/task locators. The private original is retained unchanged. Public copies remove private-build packaging and use fictional examples. No third-party code or assets are bundled; Node, Python and browser runtimes are not distributed here and retain their own licenses. The MIT grant does not apply to private originals, unrelated repository content or third-party services.
