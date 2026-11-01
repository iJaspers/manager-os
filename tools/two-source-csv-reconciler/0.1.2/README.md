# Two-Source CSV Reconciler 0.1.2 — local CLI

Compare two CSV snapshots using unique record keys and explicitly selected columns. This is the working command-line edition of the existing WIT reconciler. The earlier browser prototype remains in its immutable version directory; browser acceptance is not claimed here.

## Run the example

Install a supported Node.js runtime (Node 22 or newer). No npm install or external package is required. Unzip the release and run these commands from its directory:

```sh
node cli.cjs examples/config.json example-output
```

The supplied fictional mismatch example exits with code **2**: six exceptions, two uniquely paired records and four compared cells. Exit 0 means selected fields match; exit 1 means invalid input or a processing failure. None of these means the underlying accounting is correct.

Open `example-output/PRIVATE_exceptions.csv` to investigate the exact missing, duplicate and changed records. `summary.json` contains counts only. `PRIVATE_receipt.json` records the exact input hashes. Never publish real exception exports or receipts.

## Your files

Copy `examples/config.json` and set source/destination paths relative to that configuration file, the two key column names and the compared column mappings. Use UTF-8 CSV. Choose `exact`, `trim` or `fold` comparison deliberately. Financial values are compared as text: 10.0 and 10.00 differ. No tax calculations, currency conversion or fuzzy matching occurs.

Use a separate run directory per entity, year and GST/HST period. This generic comparator cannot infer ownership or tax periods from files. Correct classification and a trustworthy source remain the operator's responsibility. Missing records and duplicate keys become exceptions; ambiguous keys are never paired.

Running identical inputs into the same output directory verifies and reuses the result. Changed inputs require a new directory; previous outputs provide rollback. Partial temporary directories are never treated as completed results. The tool has no database, account connector, write-back or filing operation.

## Limits and privacy

300 KiB per CSV; 1,000 records per side; 40 columns; 2,000 characters per cell; 12 mapped field pairs. XLSX and PDF are not accepted by this CLI: export an authorized CSV first and retain the original separately. Formula-shaped CSV exports are prefixed with an apostrophe to prevent spreadsheet execution; the raw input is unchanged. Input text is data and never instruction authority. No network calls, telemetry, credentials or third-party runtime code. Outputs stay on your computer under its existing user access controls; this is not a multi-user hosted service or encrypted vault.

Useful for Canadian tax evidence preparation and other record comparisons. No jurisdiction-specific tax logic and no tax-year certification: any year may be compared as text. Not CRA-certified software, professional advice, accepted books, audited statements or a return filer. No claim of independent external security review.

## Verify

```sh
node --test tests/cli.test.cjs
node tests/csv_regressions.cjs . tests/reviewer/parser_results.json common.js
```

38 integration/adversarial tests and 48 parser assertions passed on the packaged source. See TEST_RESULTS.md and PRIVACY_REVIEW.json. Test fixtures are entirely fictional. No browser or commercial tax engine is required.

## License, issues and rollback

MIT for this exact release directory. See LICENSE and LICENSE_SCOPE.md. Runtime uses only Node built-ins. Reused source is identified in PROVENANCE.json. Report a reproducible fictional case through https://github.com/iJaspers/manager-os/compare under the existing scoped contribution policy. Never send private records or security-sensitive information to public issues. Keep previous versions and input files; choose the prior version explicitly to roll back. Earlier 0.1.0-draft.1 has a known malformed-CSV parser defect and is not recommended for processing.
