# Verification — 0.1.2

2026-11-01: 38/38 Node CLI/core tests and 48/48 retained parser assertions passed. Exact outputs are in tests/reviewer. Covers duplicate/blank keys, missing/extra rows, invalid quoting/UTF-8, source size bounds, text rounding differences, refunds, formula export escaping, malicious document text, prototype-named columns, unchanged originals, repeated execution, changed-input overwrite refusal, damaged-result refusal, interrupted-run recovery and cross-run data isolation.

No tax calculation, GST/ITC eligibility, GIFI mapping, professional acceptance, native filing diagnostics, hosted multi-user isolation or browser acceptance is claimed: the CLI has none of those capabilities. The private tax workbench tests are separate and no private evidence is included.

The installed Playwright package had no browser binary; an official Chromium download returned an unusable archive. Browser assertions did not run. That block applies to the historical HTML edition, which is excluded from this CLI release.
