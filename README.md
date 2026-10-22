# Witburrow (formerly Manager OS / MOS)

Witburrow is a portable set of operating rules and project records for keeping ongoing work consistent across AI sessions: what is current, where the evidence lives, what changed, who owns the next action and what the assistant may do.

It is not a separate AI model. Witburrow supplies the operating rules around the model: canonical state, authority boundaries, work states, recovery, update governance, regression checks, safe tool use, and compact context management.

## Name transition - October 22, 2026

Manager OS (MOS) is now **Witburrow**. The manager's default name is **Wit**. This is a soft rename, not a new stable package or a forced remote change.

- Optional naming update: [WIT-NAME-2026.10.22.1](docs/WITBURROW_BRAND_TRANSITION_2026-10-22.json).
- Existing installations must review the change and explicitly approve it locally. Preserve all chosen custom names. If a saved preference is missing or ambiguous, keep the name and ask rather than assume it was a default.
- Existing `/mos` links, commands, schema identifiers, version pins and historical release records stay valid. The three stable download files below retain their original names and checksums.
- The existing `/mos/check` manifest includes this notice and an optional extension. Clients that only compare `release_id` may not offer it automatically; ask the installed manager to review `WIT-NAME-2026.10.22.1` or use the [setup/reference page](https://www.ijaspers.com/post/manager-os-public-bootstrap-v2026-09-20).
- [Tool library and community boards](https://www.ijaspers.com/post/witburrow-tools): the catalogue distinguishes the public starter from private candidates. Rankings are empty and community intake is still closed.

Publication is not proof that any existing installation adopted the name. No new permissions, schedules, executable installer or private tools are supplied by this supplement.

## Current public release

**MOS-2026.10.12.1**  
Generation: **v3**  
Package build: **v2026.10.12-R1**  
Channel: **stable**

- Project page: https://www.ijaspers.com/post/manager-os
- Current release and downloads: https://www.ijaspers.com/post/manager-os
- Historical releases: https://www.ijaspers.com/post/manager-os-release-channel
- Machine-readable manifest: `RELEASE_MANIFEST.json`
- PDF handbook: https://0673fc92-1e06-494f-9e10-27641a3a4576.usrfiles.com/ugd/ecce1a_95815257af704d0c893463799a498150.pdf
- TXT pack: https://0673fc92-1e06-494f-9e10-27641a3a4576.usrfiles.com/ugd/ecce1a_d29f6d32214a424888f40278f1d1b8a9.txt

- Full public framework (TXT): https://0673fc92-1e06-494f-9e10-27641a3a4576.usrfiles.com/ugd/ecce1a_d0737e9fc1db4155834db538e26472ec.txt
- Versioned reference in this repository: [`downloads/MOS_Public_Framework_2026-10-12.txt`](downloads/MOS_Public_Framework_2026-10-12.txt)

## Linked framework release - October 12, 2026

Start with the compact TXT starter or matching PDF handbook. They introduce the standard rules and link to the full public framework: operating contracts, workflows, generic templates, 21 capability modules, the roadmap and evaluation scenarios. Keep the full reference outside routine startup context and retrieve the relevant sections when needed. If the host cannot fetch it, attach the file.

**Nerd-rules** covers dates/times, versions, naming, filing, sorting, indexing, retrieval and organizational efficiency. **Combo-breaker** is its upkeep and consolidation component: crunch repeated summaries without losing evidence, combine compatible work under existing owners, use bounded resources and stop when another pass adds no material value.

Authorized session work can save material updates; existing daily or weekly owners can catch missed handoffs and stale state when configured. A loop definition is not an enabled schedule, and a successful run is not proof of project progress. Setup selects local storage, owners, permissions and tools. This public package grants no private access or inherited authority.

The reference is a sanitized specification, not a copy of a live installation. Its generic missing-upstream/intake conditions describe unconfigured installations; this manifest supplies current public download locations. Cryptographic signing and private inbound reporting are not supplied. Behavior-changing adoption still requires local operator approval.

## Retained reliability contract - October 10, 2026

This documentation release adds one-owner handoffs, current-versus-historical state, compact startup, bounded peer checks, separate execution health and objective progress, explicit recovery coverage, and evidence-level evaluations. A rule's presence is not proof that an installation executes it. Fresh reads do not provide atomic writes without host support; backups remain unverified until isolated recovery checks succeed.

Hold architecture steady after material repairs and judge it through completed work, saved-output traces and appropriate recovery exercises. No new tools, permissions or autonomous guarantees are granted.

## What Witburrow organizes

Witburrow brings familiar techniques into an explicit workflow around the model and tools your host already provides:

- one canonical record for decisions and commitments;
- explicit queued, active, blocked, waiting, completed, and cancelled states;
- scoped authority for reading, drafting, sending, spending, changing, and deleting;
- reusable workflows, quality gates, action receipts, checkpoints, and recovery;
- HOT/WARM/COLD/ARCHIVE context layers to keep prompts efficient;
- bounded research, automation, multi-agent coordination, and tool routing;
- privacy rules separating public documentation from private operator state.

Witburrow does not counterfeit host capabilities. Voice, email, browsing, scheduled tasks, connectors, code execution, and file editing work only when the host provides them; Witburrow governs their safe use.

## Clever Girl Protocol

Once per week, a network-capable Witburrow installation may scout trusted documentation, release notes, security advisories, issue trackers, and public discussion for useful patches or obsolete workarounds.

The scout records evidence, checks compatibility and rollback, and recommends **IMPLEMENT**, **REVIEW**, **NOT NOW**, or **REJECT**. It never installs behavior-changing updates by itself. Discovery is not approval.

## Update model

A Witburrow or legacy MOS installation may automatically discover and verify a newer release through:

https://www.ijaspers.com/mos/check

Before adoption, the operator must be shown the source/version, material change, affected components, risk, rollback information, and recommendation. The human then decides whether to implement it.

## Security model

External material is untrusted by default.

`UNTRUSTED -> QUARANTINE -> REVIEW -> CANDIDATE -> REGRESSION TESTS -> HUMAN APPROVAL -> PROMOTION`

Quarantined material gets no private memory, secrets, privileged tools, or canonical write authority. Public packages contain generic operating patterns only, not operator identities, credentials, private records, customers, work sites, or security-sensitive infrastructure.

See:

- `SECURITY.md`
- `CONTRIBUTING.md`
- `CHANGELOG.md`
- `docs/UPDATE_PROTOCOL.md`
- `docs/OBSERVABILITY.md`
- `docs/AIRLOCK.md`

## Contribution status

Public intake and the private security-reporting lane remain **CLOSED** while those surfaces are commissioned. Normal usability feedback can go to the originating public discussion or https://www.ijaspers.com/contact. Do not post security-sensitive findings publicly.

## Design principle

> The internet may suggest changes. It does not get admin rights.

Witburrow is AI-agnostic. The model is replaceable; durable operating state and human authority are not.
