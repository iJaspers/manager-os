# Validation and limitations

Collection: 3.5-public-draft.1. This is a source-available experimental collection, not a validated operational product.

## Performed on this candidate
- 37 inline application scripts parsed and started under a minimal synthetic Node DOM. Shared malformed-quote rejection, valid CSV fixture and prohibited runtime API checks brought this suite to 148/148 assertions. The mock DOM cannot establish rendering, event dispatch, file picking or actual downloads.
- Shared corrected parser: 48/48 synthetic assertions, including malformed input, quoted fields, spreadsheet-formula-safe exports and serialization round trips.
- The three existing corrected Reconciler/Forge/Mapper applications: 38/38 synthetic application-state assertions, including invalid-input result clearing/export locking and recovery. This is not independent browser acceptance.
- All 105 supplied fictional CSV examples parse under the corrected shared parser. This checks syntax, not the business meaning or correctness of results.
- Source/manifest checks preserve the exact reviewed corrected 0.1.1-draft.1 HTML for tools 9–11, reused shared parser and scoped license/provenance notices.
- Source scan checked direct network, persistence, dynamic-code APIs, private identity markers and credentials. Original runtime code has no identified external runtime dependencies. This is a bounded review, not proof against all possible data disclosure or vulnerabilities.

These suites overlap. Do not add their counts together as independent coverage, call them an entire business-regression pass, or claim that every application's business rules were exhaustively validated.

## Not performed or not established
- Rendered real-browser acceptance of this combined candidate, direct extracted-file or published-host use, desktop/mobile accessibility and layout, actual file picker/download flow, outside AI/user/customer acceptance and commercial demand.
- The current execution environment refused a Chromium launch (OS socket restriction), and a cloud browser refused file-protocol navigation. Those routes were stopped, not bypassed. Existing historical in-memory browser checks are not acceptance of this changed collection. Other inherited business-rule/browser suites were NOT rerun for this release.
- No original customer/employer record, real financial decision, legal agreement, work dispatch, payment, tax filing or safety decision was tested or authorized.

## Reproduce the safe local synthetic checks
From the extracted collection directory, with Node.js already installed:

    node tests/collection_smoke.cjs
    node tests/fixture_syntax.cjs
    node tests/csv_regressions.cjs . tests/reviewer/parser_results.json common.js
    node tests/application_regressions.cjs . 3.5-public-draft.1 tests/reviewer/application_results.json

These scripts read only collection files and write test results below tests/. Review scripts before executing. A Node VM is not an OS security boundary.

Original `tests/*browser_checks.py` scripts are provided for continuation by a suitably configured and authorized tester; they require separate Python, Playwright and Chromium installations and may use the inherited executable path `/usr/bin/chromium`. They were not run as part of this combined release. Test scripts and fixture inputs are fictional. Never bypass an environment security restriction to run them.

Any change to source, sample data, paths or dependencies requires its own versioned checks. A successful demonstration is not permission to use real private data or to remove fictional-only constraints.
