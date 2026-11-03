# Witburrow public tool source previews

Versioned, unranked source previews and WIP packages, each separately MIT-licensed inside its own version directory. That license does not apply to the rest of this repository or any private originals.

- [Invoice Reference Review](invoice-reference-review/0.1.2/README.md)
- [Pretax Role Comparison](pretax-role-comparison/0.1.2/README.md)
- [Documented Compensation Comparison](documented-compensation-comparison/0.1.2/README.md)

Use the exact public ID, version, source and test evidence. Similar private catalogue numbers are not identity or verification evidence. None posts accounting entries, contacts employers, sends money or automatically executes on the public library page.

You may fork, modify and redistribute these licensed directories. Pull-request intake is open only for the nine listed public tool IDs, under the privacy, license and isolated-manual-test gates in CONTRIBUTING.md. No automatic execution or merging is enabled. Broader framework and security-sensitive intake remain closed. Older version directories and ZIPs are historical; current repository CONTRIBUTING.md governs intake. The public tool board is not a ranking or endorsement system.

Live catalogue: https://www.ijaspers.com/post/witburrow-tools

New here? [Follow the versioned first everyday task guide](FIRST_TASK_2026-10-22.3.md), including task/input fit, explicit consent, no-payment CSV headers and result handoff.

Current versions: Invoice Reference Review 0.1.2; Pretax Role Comparison and Documented Compensation Comparison 0.1.2. Invoice 0.1.1 has known malformed-CSV/UTF-8-size defects and must not be relied on for matching output; use the versioned correction. Historical directories remain immutable.

The original three source previews are now 0.1.2. Pretax Role Comparison adds a finite-difference hold and explicit warning; Documented Compensation Comparison adds bounded CLI JSON admission, duplicate-key rejection and retry checks. Older source directories are historical, not current recommendations. Read each exact version’s tests and limits; no browser/device or production capacity certification is claimed.


## Unverified unfinished source: 2026-10-23

These packages are shared so someone else can inspect and continue them, not because they passed a production-readiness gate. Named local checks, tests not run, concrete limitations and the next useful step are recorded inside each package. Source publication does not mean verified usefulness or safety.

- [Bill Calendar Preview 0.1.0](bill-calendar-preview/0.1.0/README.md): no recurrence or bank posting knowledge; browser acceptance unverified.
- [Field Hours Review 0.1.0](field-hours-review/0.1.0/README.md): clock-time only, no timezone/DST or payroll determination.
- [Grocery Planning Preview 0.1.0](grocery-planning-preview/0.1.0/README.md): supplied offers only, no live prices or mixed-pack optimization.

MIT permits forks and redistribution with notices. Each WIP includes a HANDOFF_TEMPLATE.md for a reviewable return patch. The dated CONTRIBUTING.md now includes these three WIP IDs in the now nine-tool allowlist. Submit only bounded source/documentation/synthetic fixtures under the same privacy, license and review gates; unfinished source remains labelled WIP; failed, ambiguous or unavailable checks remain explicit holds. No automatic execution or merging is introduced.

[CATALOGUE.json](CATALOGUE.json) is the sanitized public projection for this release. It contains only already-public candidate descriptions and published tool metadata, not the private inventory. The expected_tool_count excludes the separately rendered starter; expected_total_entries includes it. publicly_available is availability only, never a readiness score. The legacy public_ready field is deprecated; a WIP may be publicly available while public_ready remains false. The fixed library renderer reads reviewed canonical metadata on page visits. It does not approve, execute or merge submissions automatically.



## Additional unfinished source handoffs: 2026-10-24

These three scoped-MIT prototypes include editable HTML/JavaScript, fictional fixtures, tests, provenance, limits and a concrete next task. All have a reproduced bare-quote CSV parser defect. Current browser acceptance and outsider pickup-to-release have not been established.

- [Two Source Csv Reconciler 0.1.0-draft.1](two-source-csv-reconciler/0.1.0-draft.1/README.md)
- [Regression Plan Forge 0.1.0-draft.1](regression-plan-forge/0.1.0-draft.1/README.md)
- [Dependency Critical Path Mapper 0.1.0-draft.2](dependency-critical-path-mapper/0.1.0-draft.2/README.md)

The legacy CATALOGUE.json projection still carries its prior six-source snapshot. The dated all-stage inventory is a separate descriptive feed, not a claim that every idea or private prototype has downloadable source. A metadata listing does not open upstream intake.

Dependency Mapper draft.2 is an additive packaging correction: its prior Git-source fixture had a newline/hash mismatch. Historical draft.1 stays available; the known functional CSV parser issue remains.

[Browse all-stage descriptive metadata](inventory/2026-10-24/PUBLIC_CATALOGUE.json) and [read the count reconciliation](inventory/2026-10-24/COUNTING_NOTES.md). There are 285 records, not 285 distinct built tools. Nine source IDs are downloadable; 276 records remain descriptions with source-specific next steps.

## Maintainer WIP publication — 2026-11-03

- [Connector Doctor 0.2.1-public-draft.1](connector-doctor/0.2.1-public-draft.1/README.md): current-host diagnostics, read-only adapter, portable preferences with drift/rollback, and metadata-only resume; 129 local tests. Includes an optional [Bob/RC1 supplement](../integration/bob/connector-doctor-0.2.0-public-draft.1/README.md), not a second Bob identity.
- [Regression Plan Forge 0.1.1-public-draft.1](regression-plan-forge/0.1.1-public-draft.1/README.md): malformed-CSV repair; 57 local parser/application tests.
- [Dependency & Critical Path Mapper 0.1.1-public-draft.1](dependency-critical-path-mapper/0.1.1-public-draft.1/README.md): same shared-parser repair; 57 local parser/application tests.

These versioned packages supersede earlier parser-defective drafts for new trials. Old releases and frozen RC1 remain intact. Browser/device and independent product acceptance remain separate. This maintainer publication does not expand community contribution intake; CONTRIBUTING.md still governs that lane. [Exact scope, tests and rollback](releases/public-push-2026-11-03/PUBLICATION_REVIEW.md).

Release maintainers: the existing [package builder now checks bounded source and archive safety](releases/public-push-2026-11-03/SIDEPROJECT_REVIEW.md). SideProject decisions and November 6 cases are recorded there; no third-party engine was installed.

Optional [Bob verification supplement 0.1.0-public-draft.1](https://github.com/iJaspers/manager-os/tree/6cc610198a83b391f2d8708681797a7b59538fd6/integration/bob/verification-0.1.0-public-draft.1) adds tested Promptfoo contracts, a real MCP Inspector fixture adapter, SkillSpector report review, Playwright RC1 HTTP checks and local first-result timing. It reuses Connector Doctor 0.2.1 and creates no new canonical tool identity. The optional CLIs were tested separately; no third-party runtime is bundled. Native ChatGPT/Gemini acceptance, rendered website checks and the actual SkillSpector scan remain unverified. [Exact files, results and publication readback](releases/public-push-2026-11-03/REDDIT_RELEASE_RECEIPT.json).
