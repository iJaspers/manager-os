# Verification record

Candidate version: 0.1.1-draft.1. Prepared 2026-10-25.

The exact new candidate source is tested with the existing reviewed suites: 40 batch logic assertions, 144 parser assertions and 38 application function/state assertions. These overlap and must not be summed as unique coverage. Current per-package results and exact runtime hashes are in tests/FINAL_TEST_RECEIPT.json. Three-tool totals are context, not extra independent coverage. They are in-house synthetic Node VM/DOM-stub checks, not an independent human or browser acceptance test.

Historical versions accepted a bare quote in an unquoted field. This version rejects it and retains valid quoted commas, doubled quotes and multiline fields under the named tests. Unsupported/unexamined CSV cases may still exist.

No new browser run is claimed: the previous attempt was blocked before assertions by the environment. Rendered browser, file picker/download, mobile, accessibility, real-user and production acceptance remain unverified. Historical source-package Chromium totals do not upgrade this derivative.

Use fictional inputs and review source before isolated execution.
