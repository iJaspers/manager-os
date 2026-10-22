# Test evidence: wit.invoice-reference-review@0.1.2

Date: 2026-10-22. Synthetic inputs only.

- `node test.js`: 15 original named engine/export checks passed, 0 failed.
- `node test_stress.js`: 15 additional malformed-input, size-boundary and compatibility checks passed, 0 failed. These include rejecting text after a closing quote and quotes in unquoted fields; rejecting over-limit ASCII and multibyte CSV; accepting exactly 1,048,576 UTF-8 bytes; quoted commas/newlines/escaped quotes; CRLF; duplicate/blank headers; wrong widths; ID collisions; prototype-named headers; formula-safe CSV export; instruction-like text treated only as data.
- Baseline 0.1.1 failed the three newly reproduced quote/multibyte assertions. The same fixed-candidate checks were rerun during publication and passed. The package includes its reproducible tests rather than private workload fixtures.
- UTF-8 counting uses bounded character iteration, including surrogate pairs, without new dependencies. Row admission is limited to 10,000 data rows per CSV. These bounds are not a latency or memory guarantee for every device.
- HTML engine tests use Node VM, not browser rendering. Standalone browser/device/mobile acceptance remains NOT VERIFIED. A separate bounded synthetic stress campaign measures engine behavior; it is not public traffic, concurrent users, host installation, production capacity or an independent security audit.
- Previous local simulated pickup/change/retest/return-patch checks and internal documentation PR remain historical evidence; no outsider adoption is claimed.

The known v0.1.1 defects are documented in README.md and CHANGELOG.md. Existing financial/input limitations remain. Matching remains diagnostic, never verified accounting, deposit evidence or a posting decision.
