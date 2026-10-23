# Witburrow public tool source previews

Six distinct published source tools, each versioned, unranked and separately MIT-licensed inside its own version directory. Three are explicitly UNVERIFIED work-in-progress source packages. That license does not apply to the rest of this repository or any private originals.

- [Invoice Reference Review](invoice-reference-review/0.1.2/README.md)
- [Pretax Role Comparison](pretax-role-comparison/0.1.2/README.md)
- [Documented Compensation Comparison](documented-compensation-comparison/0.1.2/README.md)

Use the exact public ID, version, source and test evidence. Similar private catalogue numbers are not identity or verification evidence. None posts accounting entries, contacts employers, sends money or automatically executes on the public library page.

You may fork, modify and redistribute these licensed directories. Pull-request intake remains open only for the original three public tool IDs, under the privacy, license and isolated-manual-test gates in CONTRIBUTING.md. No automatic execution or merging is enabled. Broader framework and security-sensitive intake remain closed. Older version directories and ZIPs are historical; current repository CONTRIBUTING.md governs intake. The public tool board is not a ranking or endorsement system.

Live catalogue: https://www.ijaspers.com/post/witburrow-tools

New here? [Follow the versioned first everyday task guide](FIRST_TASK_2026-10-22.3.md), including task/input fit, explicit consent, no-payment CSV headers and result handoff.

Current versions: Invoice Reference Review 0.1.2; Pretax Role Comparison and Documented Compensation Comparison 0.1.2. Invoice 0.1.1 has known malformed-CSV/UTF-8-size defects and must not be relied on for matching output; use the versioned correction. Historical directories remain immutable.

The original three source previews are now 0.1.2. Pretax Role Comparison adds a finite-difference hold and explicit warning; Documented Compensation Comparison adds bounded CLI JSON admission, duplicate-key rejection and retry checks. Older source directories are historical, not current recommendations. Read each exact version’s tests and limits; no browser/device or production capacity certification is claimed.


## Unverified unfinished source: 2026-10-23

These packages are shared so someone else can inspect and continue them, not because they passed a production-readiness gate. Named local checks, tests not run, concrete limitations and the next useful step are recorded inside each package. Source publication does not mean verified usefulness or safety.

- [Bill Calendar Preview 0.1.0](bill-calendar-preview/0.1.0/README.md): no recurrence or bank posting knowledge; browser acceptance unverified.
- [Field Hours Review 0.1.0](field-hours-review/0.1.0/README.md): clock-time only, no timezone/DST or payroll determination.
- [Grocery Planning Preview 0.1.0](grocery-planning-preview/0.1.0/README.md): supplied offers only, no live prices or mixed-pack optimization.

MIT permits forks and redistribution with notices. Each WIP includes a HANDOFF_TEMPLATE.md for a reviewable return patch. This release does not widen the original three-ID upstream PR allowlist; consult CONTRIBUTING.md before submitting. No automatic execution or merging is introduced.

[CATALOGUE.json](CATALOGUE.json) is the sanitized public projection for this release. It contains only already-public candidate descriptions and published tool metadata, not the private inventory. The expected_tool_count excludes the separately rendered starter; expected_total_entries includes it. publicly_available is availability only, never a readiness score. The legacy public_ready field is deprecated; a WIP may be publicly available while public_ready remains false. Canonical data is not an enabled autonomous update job.
