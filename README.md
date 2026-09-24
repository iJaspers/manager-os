# Manager OS (MOS)

Manager OS is a portable management layer for using an AI as a persistent, recoverable manager instead of a one-off chatbot.

It is not a separate AI model. MOS supplies the operating rules around the model: canonical state, authority boundaries, work states, recovery, update governance, regression checks, safe tool use, and compact context management.

## Current public release

**MOS-2026.09.24.1**  
Generation: **v3**  
Package build: **v2026.09.24-CG1**  
Channel: **stable**

- Project page: https://www.ijaspers.com/post/manager-os
- Release channel: https://www.ijaspers.com/post/manager-os-release-channel
- Machine-readable manifest: `RELEASE_MANIFEST.json`
- PDF handbook: https://raw.githubusercontent.com/iJaspers/manager-os/main/downloads/MOS_Public_Handbook_v2026.09.24-CG1.pdf
- TXT pack: https://raw.githubusercontent.com/iJaspers/manager-os/main/downloads/MOS_PUBLIC_PACK_v2026.09.24-CG1.txt

## What MOS adds beyond normal ChatGPT

A normal chat is a conversation. MOS turns capable AI tools into a governed operating system for work:

- one canonical record for decisions and commitments;
- explicit queued, active, blocked, waiting, completed, and cancelled states;
- scoped authority for reading, drafting, sending, spending, changing, and deleting;
- reusable workflows, quality gates, action receipts, checkpoints, and recovery;
- HOT/WARM/COLD/ARCHIVE context layers to keep prompts efficient;
- bounded research, automation, multi-agent coordination, and tool routing;
- privacy rules separating public documentation from private operator state.

MOS does not counterfeit host capabilities. Voice, email, browsing, scheduled tasks, connectors, code execution, and file editing work only when the host provides them; MOS governs their safe use.

## Clever Girl Protocol

Once per week, a network-capable MOS may scout trusted documentation, release notes, security advisories, issue trackers, and public discussion for useful patches or obsolete workarounds.

The scout records evidence, checks compatibility and rollback, and recommends **IMPLEMENT**, **REVIEW**, **NOT NOW**, or **REJECT**. It never installs behavior-changing updates by itself. Discovery is not approval.

## Update model

A MOS installation may automatically discover and verify a newer release through:

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

MOS is AI-agnostic. The model is replaceable; durable operating state and human authority are not.
