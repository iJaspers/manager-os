# Test results — WIT Scout + Explain 0.1.0-public-draft.1

Verification date: **2026-11-24 UTC** (**2026-11-23 America/Dawson_Creek**). These are fresh results from the selected standalone source and tests, not inherited release claims.

## Environment and observed results

| Check | Observed result |
|---|---|
| Python runtime | Python 3.12.14 |
| JavaScript runtime | Node.js 24.22.3 |
| Operating system / architecture | Linux x86_64 |
| Python regression suite | **135 tests passed**, exit 0; no failures, errors or skips reported |
| JavaScript adapter suite | **20 tests passed**, exit 0; 0 failures and 0 skips |
| Documented fictional CLI example | Exit 0; two findings printed, both labelled unverified search snippets |
| Dependency installation | None |
| Live source/provider calls | None in this verification |

Commands were run from the source directory:

```sh
python3 -B -m unittest discover -s . -p 'test_*.py' -q
node --test test_github_host_runtime.mjs
python3 -B provider_adapter.py example_results.json --goal "school gymnastics workshops and funding" --level practical
```

The 155 regression tests are counts reported by the two test runners; subcases and repeated subprocess checks are not added as extra tests. The CLI example is reported separately.

## What the checks cover

The suites exercise URL normalization and ranking; rejection of malformed and oversized admitted fields; untrusted provider flags; source/hash/quote mismatch; unsupported completed-action claims; conservative negation checks; evidence navigation and changed-input holds; current and legacy MCP response shapes; conflicting/error connector responses; immutable target and UTF-8 blob checks; complete checkpoint recovery; altered bytes, code revisions and allowlists; preserved failures; and consistent short/detail presentation.

Checkpoint tests use temporary local files. Recovery acceptance tests use synthetic transfers and actual short-lived subprocesses. On this POSIX host, the acquisition subprocess deliberately terminates itself with SIGKILL after writing its checkpoint; fresh processes then exercise valid restore and rejected receipt/claim states, with and without Python optimization. The separate unit case mocks the kill call. No existing user process is targeted.

All source and test files were inspected before execution. The connector test functions are stubs, and the recovery runner disables its own socket access. The suites do not claim an operating-system network sandbox, a live connector run or a deployed acquisition pipeline.

## Not established by these results

No independent semantic truth review, security certification, production-capacity benchmark, malicious-host containment, live search/LinkedIn/Reddit ingestion, end-to-end deployed host acceptance, Windows support, rendered browser UI or physical-phone use was tested. The full CLI file is read before row/field admission checks; passing these tests does not make it an arbitrary-upload service.

The source is an experimental preview. No failed checks were observed in the named run, but untested behavior and documented limits remain. Generated test receipts, source captures, local checkpoints and raw run logs are excluded from the release candidate.
