# Regression Plan Forge

Unfinished source handoff, draft 0.1.0-draft.1. Turn explicit fictional requirements into a reviewable, unexecuted regression test plan.

This draft includes the actual editable application, shared helpers, synthetic fixtures and executable browser tests. It is not just a concept description. The inspected files have an owner-authorized scoped MIT license; see LICENSE and LICENSE_SCOPE.md. Manual pull-request intake is open for this exact tool ID under the repository CONTRIBUTING.md. No automatic execution or merging is enabled.

## Run locally

Keep the folder together and open `10_Regression_Plan_Forge.html` in a modern browser. No account, server, package install or network dependency is required by the application. Use the built-in fictional examples or CSVs in examples/. Independent file-host/browser acceptance is still needed; the current executor could not launch its browser test process.

The built-in three-requirement example produces 13 planned cases; seven require human specification. None of those generated cases has executed.

## What currently works in the inspected implementation

- Parses an 11-column requirements CSV and validates IDs, risk and required expectations.
- Generates valid, invalid, repeat and relevant boundary/privacy/rollback test cases.
- Marks generic expectations REVIEW_REQUIRED and prepared cases NOT_EXECUTED.
- Exports case CSV, review TXT and counts-only JSON without pretending tests have run.

The evidence below is narrower than full browser acceptance. These statements describe implemented behavior and the specific checks performed, not a production guarantee.

## Known issues and missing work

- Confirmed parser gap: `common.js` accepts a double quote inside an unquoted field, for example `ab"cd`, instead of rejecting malformed CSV. This was reproduced in Node on the sanitized copies.
- No test runner, environment setup, source-code inspection or actual pass/fail execution.
- Limits: 100 KiB, 40 requirements, 500 characters per cell and 240 cases.
- Boundary, repetition, privacy and rollback checks need exact human-specified expectations.
- Browser launch, visual/accessibility review, normal file-host downloads, mobile behavior and real-user acceptance are not verified on this derivative.

## Next useful task

Add a separate editable expected-outcome field for each REVIEW_REQUIRED case, preserving NOT_EXECUTED status until actual evidence is recorded. First add a strict bare-quote CSV regression test.

## Evidence level

Progress: prototype. Testing: partly tested, known issues. Contribution: needs finishing; parser hardening is a bounded candidate fix, not an effort guarantee. Potential: experimental and needs evaluation, an editorial label rather than a measured outcome.

- Copied source bytes matched the supplied v2.0 member SHA-256 manifest before sanitation.
- Current static checks: JavaScript/Python syntax, resource/privacy checks and network/storage API scan.
- Current Node VM checks: 40 assertions across all three handoffs with a minimal DOM stub. This includes positive reproduction of the known parser gap. It is not a browser or download test.
- Historical source report: 66/66 Chromium in-memory assertions passed on the original v2.0 source package. This was not rerun successfully on the sanitized derivative.
- Current browser attempt: blocked before any assertions. See TEST_RESULTS.md.

## Tests

With Python, Playwright and Chromium already available, run:

    python tests/regression_browser_checks.py

Set CHROMIUM_PATH to the Chromium executable if system discovery does not find it. Test prerequisites are separate from the dependency-free application. The tests use fictional data and write results under tests/. Review code before running it in a disposable environment.

The repository also contains `tools/handoff-tests/2026-10-24/logic_checks.cjs`; from a repository checkout run `node tools/handoff-tests/2026-10-24/logic_checks.cjs`. Individual ZIPs contain the application-specific browser suite, not that batch-wide runner.

## Data boundaries

Use fictional inputs. The app has no backend, telemetry, network integration or persistent storage. Detailed CSV/TXT exports deliberately retain entered text and may be sensitive if you ignore the fictional-input restriction. Aggregate JSON omits raw identifiers but is not a privacy certification or permission to share. Do not upload real records to issues or pull requests.

## Continue the work

Repository: https://github.com/iJaspers/manager-os
Read CONTRIBUTING.md for the current route and scope. The owner approved the manual contribution route for this tool on 2026-10-24. No automatic execution or merging is authorized.

## Rollback

The original source archive was not edited. Discard this draft folder to undo the handoff preparation. For a published release, restore the prior versioned catalogue/source reference rather than deleting history. Later releases must retain the base hashes and document changes rather than overwrite this evidence.
