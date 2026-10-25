# Validation and limitations

Collection candidate: 3.5-public-draft.2. Experimental fictional-data source, not an operational product.

## Freshly performed
- Baseline controlled Node promise test reproduced a stale-read overwrite of a newer manual edit in all 25 changed applications.
- Candidate asynchronous-import suite: 357/357 controlled assertions across those 25 apps, using multiple event listeners and deferred promises. Covers same-field replacement, manual edit, stale rejection, cancellation, oversize selection, recovery, demos, independent sides and forced pending exports. See tests/async_import_results.json.
- Independent separately authored challenge: 786/786 controlled-promise assertions across all25 changed apps, including configuration edits, both completion orders, stale errors, pending state, demos and recovery. See tests/independent_async_import_results.json. This overlaps the357 checks.
- All 37 applications: 148/148 syntax/startup/shared-parser/API assertions under a minimal synthetic Node DOM.
- Shared parser: 48/48 assertions. It is byte-identical to the prior corrected parser.
- Three parser-family application-state suite: 38/38 assertions.
- All 105 supplied fictional CSV fixtures parse. This is syntax, not business correctness.

Suites overlap; do not sum these as independent coverage. Tests were run on the final source candidate, but browser/business suites were not comprehensively rerun.

## Not established
No rendered-browser, real file-picker/download, mobile layout/accessibility, customer, outside-AI, real-host, commercial, security or legal/IP acceptance is claimed. Previously restricted browser/OS execution routes were not retried or bypassed. All data must remain fictional; exports remain private until separately reviewed.

## Reproduce synthetic checks
With Node already installed, from the extracted collection:

    node tests/async_import_regressions.cjs
    node tests/independent_async_import_challenge.cjs . tests/independent_async_import_results.json
    node tests/collection_smoke.cjs
    node tests/fixture_syntax.cjs
    node tests/csv_regressions.cjs . tests/reviewer/parser_results.json common.js
    node tests/application_regressions.cjs . 3.5-public-draft.2 tests/reviewer/application_results.json

The baseline option needs the preserved prior release directory and is not required for candidate testing. Review scripts before running. A Node VM is not an OS security boundary. Historical Python browser suites are provided for continuation, not represented as rerun. Do not bypass environment restrictions to run them.
