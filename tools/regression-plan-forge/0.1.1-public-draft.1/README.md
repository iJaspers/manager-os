# Regression Plan Forge 0.1.1-public-draft.1

Turn fictional requirements into a reviewable test plan. The built-in example produces 13 planned cases; seven need human expectations. No generated case has executed.

Download this version's ZIP, extract the whole folder, then open `10_Regression_Plan_Forge.html` in a modern browser. Click **Load fictional sample** and prepare/analyze. Edit the provided CSV or use the fictional file in `examples/`. Keep common.js and styles.css beside the HTML. No account, server, installation or network dependency.

This corrected WIP rejects bare quotes in unquoted CSV fields. Valid quoted commas, doubled quotes and multiline fields still work. Rejected input clears previous results and disables export; loading the sample restores usable output. Detailed CSV/TXT exports include entered text; counts-only JSON omits raw identifiers and does not grant authority.

## Tests and limitations

From this folder: `node --test tests/*.test.cjs`. **57 passed, 0 failed** on Node 24.22.1: 47 parser/serialization checks and 10 application tests using a minimal DOM fixture. These are actual local tests, not rendered-browser acceptance.

40 requirements, 100 KiB UTF-8, 500 characters per cell, 240 generated cases. No test runner or source inspection. Repetition, boundary, privacy and rollback outcomes need human specification.

Inherited optional Python Playwright/Chromium checks remain in tests/. They were not run here because those browser prerequisites are unavailable. Mobile, visual/accessibility, independent real-user and security acceptance remain unverified. Use synthetic data; no private records belong in public reports.

## Provenance and rollback

Derived from published `0.1.0-draft.1` under its directory-scoped MIT license. Reuses the already-published strict parser from Reconciler 0.1.2, retaining its MIT notice. No new runtime dependencies, vendor code, private source or private examples. See PROVENANCE.json for exact base hashes and TEST_RESULTS.md for scope.

Old releases remain untouched. Rollback by selecting the prior version, which retains the documented CSV defect; never use malformed input as a workaround. For Git rollback, revert the relevant source/catalogue publication commit after reviewing later dependencies. This WIP is not product acceptance or the WIT hard launch. Existing CONTRIBUTING.md governs submissions; no automatic merge.
