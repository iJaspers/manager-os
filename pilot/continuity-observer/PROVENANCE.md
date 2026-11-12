# Provenance, design comparison and held integrations

Date checked: 2026-11-12. Repo being extended: `iJaspers/manager-os`, observed main commit `b9fa480ae6da5f2b906c5bd8c520faf1eb50a031` before this optional pilot.

### External research (pinned source snapshots)

| Project | Observed ref | Relevant fact | Decision |
|---|---|---|---|
| [Thomas Schijf's llm-eval-harness](https://github.com/thomasschijf/llm-eval-harness) | `9d14b21c303893e8af64bd7fe2c3ed8fb5c7f476` | Offers golden-set scoring and offline stub demonstrations; repository has **no visible license** at the inspected root. | Concepts only. No code, fixtures, prompts or expression copied. |
| [Syns CLI](https://github.com/synsdev/syns-cli) | `3b26518044a1a3a9e3729e997333c65baf0d8ac2` | CLI with source synchronization and conflict workflow, MIT notice `Copyright (c) 2026 Bartosz Sojka`. | No implementation copied; auto-sync would create an unapproved external transfer surface. |
| [Syns Claude plugins](https://github.com/synsdev/syns-claude-plugins) | `51a8404bab0d780dd8bf4c7c3ced19c8ce0107a4` | Hook-based pull on session start and sync on stop, MIT. | No hooks imported: unapproved authentication, implicit sync and portability constraints. |
| [Syns Codex plugins](https://github.com/synsdev/syns-codex-plugins) | `566c77aa1d57fe961f6a58b5966f46c944904fa1` | Host-specific hooks, explicit trust confirmation, MIT. | No code copied. WIT already has host-specific capability gating. |
| [Trellis fork](https://github.com/thomasschijf/Trellis) | Public fork of `mindfold-ai/Trellis`, AGPL-3.0 | Repo-based memory/spec/task workflows substantially overlap WIT. | No integration; strong copyleft and duplication risk. |
| [Web Tools fork](https://github.com/thomasschijf/web-tools) | Public fork of `arnaudjnn/web-tools`, MIT | Search/fetch/archives with several self-hosted services. | Not needed for a zero-cost, host-native WIT pilot; nothing copied. |

**Ownership note:** Thomas's GitHub includes forks of other developers' projects, and the Syns MIT license credits Bartosz Sojka. A public repository owned by an account is not proof that person authored everything in it. Respect upstream notices if any portion is ever reused.

### Why this pilot is genuinely different from existing WIT pieces

- `tools/regression-plan-forge` plans tests but does not execute or score observed model responses.
- `pilot/adaptive-experience` contains fixed profile-card validation plus documented synthetic acceptance cases, not a reusable structured-response scoring lane.
- `10_MANAGER_EVALS` and `10A_SUBOS_REGRESSION_EVALS` are scenario definitions and historical evidence. This observer does not assert they have been independently run or replace their ownership.
- This observer's implementation, schema, fictional cases and unit tests were authored independently for WIT with AI assistance, using generic Python standard-library concepts. There are no vendored source files, runtime imports, network endpoints, credentials, production records, telemetry or changed WIT permissions.

### Integration boundary

This pilot exists as a **read-only optional test aid**, not the public installer or another canonical tool identity. Additional host-specific adapters, real session logs, score calibration, network integrations, automatic pull/push and product acceptance are explicitly **out of scope**. Do not promote this source preview into the stable installer, make host-reliability claims, or enable automatic adoption without independent host acceptance and exact release readback. Source-only WIP publication requires explicit owner approval, an honest test receipt, and a clean license/privacy review. Existing release SHA, source inventory, profile storage, PR #10 and stable downloads must remain unchanged.

### Review-branch hardening (2026-11-12)
An original, dependency-free `compare` mode was added after reviewing the existing WIT pilot. It compares two sets of **recorded structured responses** against the same fictional oracle while refusing to count missing observations as improvements. The input loader now uses an opened file descriptor, validates regular-file type and bounds the bytes actually read. Test and documentation changes are original WIT work, not implementations from Syns, Trellis or the unlicensed LLM harness. Neither the license boundaries above nor the WIT public starter's release gates changed.

### Grey Goo-style local negative tests (2026-11-12)

16 new synthetic adversarial tests are original WIT-authored unit tests; they were not copied from an external GG tool or Thomas Schijf's repositories. They do not authenticate model behavior. Publication, if approved, applies only to the optional WIP source and not to the stable installer or website. See `GREY_GOO_LOCAL_REVIEW_2026-11-12.md`.
