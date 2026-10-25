# Two-Source CSV Reconciler

Unfinished source handoff, draft 0.1.1-draft.1. Compare two CSV snapshots by a unique key and explicitly mapped columns.

This draft includes the actual editable application, shared helpers, synthetic fixtures and executable browser tests. It is not just a concept description. The inspected files have an owner-authorized scoped MIT license; see LICENSE and LICENSE_SCOPE.md. Manual pull-request intake is open for this exact tool ID under the repository CONTRIBUTING.md. No automatic execution or merging is enabled.

## Run locally

Keep the folder together and open `09_Two_Source_CSV_Reconciler.html` in a modern browser. No account, server, package install or network dependency is required by the application. Use the built-in fictional examples or CSVs in examples/. Independent file-host/browser acceptance is still needed; the current executor could not launch its browser test process.

The built-in mismatch example contains six source records, four destination records, two uniquely paired records and six exceptions. The matching example has zero exceptions.

## What currently works in the inspected implementation

- Loads fictional CSV text or local sample files.
- Finds blank keys, duplicate keys, missing and extra records, and changed mapped values.
- Keeps ambiguous duplicate keys unpaired; offers exact, trimmed and case-insensitive comparison.
- Exports detailed local CSV/TXT and aggregate-only JSON; editing invalidates old output.

The evidence below is narrower than full browser acceptance. These statements describe implemented behavior and the specific checks performed, not a production guarantee.

## Known issues and missing work

- Historical CSV-BARE-QUOTE is corrected in this version: bare quotes inside unquoted fields are rejected. Bounded Node tests preserve valid quoted commas, doubled quotes and multiline fields. This is not a general CSV/security certification.
- No database connection, migration, write-back or verification of source truth.
- Limits: 300 KiB per input, 1,000 records per side, 40 columns, 12 mapped pairs and 2,000 characters per cell.
- Only selected columns are compared. Both inputs can match and still be wrong.
- Browser launch, visual/accessibility review, normal file-host downloads, mobile behavior and real-user acceptance are not verified on this derivative.

## Next useful task

Run the included browser suite in an ordinary permitted environment and record actual file import, edit-invalidates-output and download behavior. Preserve the new malformed-CSV regression cases.

## Evidence level

Progress: prototype. Testing: partly tested; historical bare-quote defect corrected within the stated Node scope. Contribution: needs finishing; browser verification and documented next tasks remain, without an effort guarantee. Potential: experimental and needs evaluation, an editorial label rather than a measured outcome.

- Copied source bytes matched the supplied v2.0 member SHA-256 manifest before sanitation.
- Current static checks: JavaScript/Python syntax, resource/privacy checks and network/storage API scan.
- Current candidate checks: 40 batch logic, 144 parser and 38 application-state assertions on the new source. These suites overlap, so do not sum them as unique coverage. No browser or download acceptance follows.
- Historical source report: 58/58 Chromium in-memory assertions passed on the original v2.0 source package. This was not rerun successfully on the sanitized derivative.
- Previous browser attempt: blocked before any assertions. No new browser acceptance is claimed; see TEST_RESULTS.md.

## Tests

With Python, Playwright and Chromium already available, run:

    python tests/recon_browser_checks.py

Set CHROMIUM_PATH to the Chromium executable if system discovery does not find it. Test prerequisites are separate from the dependency-free application. The tests use fictional data and write results under tests/. Review code before running it in a disposable environment.

This ZIP is self-contained for running the application and its 48-case parser regression suite. The batch-wide logic runner is a separately prepared companion, not a dependency or a promise of public availability. The bundled application-state runner requires a checkout containing all three matching version directories; it is not a standalone one-package command.

## Data boundaries

Use fictional inputs. The app has no backend, telemetry, network integration or persistent storage. Detailed CSV/TXT exports deliberately retain entered text and may be sensitive if you ignore the fictional-input restriction. Aggregate JSON omits raw identifiers but is not a privacy certification or permission to share. Do not upload real records to issues or pull requests.

## Continue the work

Repository: https://github.com/iJaspers/manager-os
Read CONTRIBUTING.md for the current route and scope. The owner approved the manual contribution route for this tool on 2026-10-24. No automatic execution or merging is authorized.

## Rollback

The original source archive was not edited. Discard this draft folder to undo the handoff preparation. For a published release, restore the prior versioned catalogue/source reference rather than deleting history. Later releases must retain the base hashes and document changes rather than overwrite this evidence.

## New parser correction

This version rejects malformed bare quotes while preserving valid quoted CSV in the tested scope. No new dependency, network integration or persistent storage was introduced. The internal reviewer rejected an earlier invalid fix; only the reviewed parser bytes were carried forward. No outside contributor attribution or production/browser acceptance is claimed. Previous versions remain available.

## Reproduce bounded parser tests

From this version folder, run `node tests/csv_regressions.cjs . tests/reviewer/parser_results.json common.js` (48 parser assertions for this one copy). The bundled application_regressions.cjs is a three-tool suite and requires all three matching version directories; it is not needed to run this app or its one-package parser tests. Test reports write only to the chosen reviewer output folder. These Node checks are not rendered-browser checks.
