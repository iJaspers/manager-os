# Local results — 2026-11-03

`node --test tools/dependency-critical-path-mapper/0.1.1-public-draft.1/tests/*.test.cjs`: **57 passed, 0 failed, 0 skipped** on Node 24.22.1.

47 parser/serialization cases cover valid quoted CSV, newline variants, escaped quotes, Unicode, rejection of 15 malformed patterns, formula-safe exports and roundtrip. 10 application checks cover documented demo result, aggregate privacy/authority flags, actual handler rejection of malformed quotes, stale-output invalidation, successful retry, duplicate IDs, UTF-8 byte cap, schema rejection, quoted multiline input and a domain boundary.

Before repair, the published 0.1.0-draft.2 parser reproduced acceptance of `ab"cd` in an unquoted cell. The new version rejects it. Parser bytes exactly match the published MIT Reconciler 0.1.2 common.js.

Not run: inherited rendered Chromium suite (Python Playwright and Chromium unavailable), mobile/file-host download UI, accessibility review, independent outsider/security/product acceptance. Node DOM fixtures do not establish browser rendering or downloading.
