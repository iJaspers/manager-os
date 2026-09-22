# Manager OS (MOS)

Manager OS is a portable management layer for using an AI as a persistent, recoverable manager instead of a one-off chatbot.

It is not a separate AI model. MOS supplies the operating rules around the model: canonical state, authority boundaries, work states, recovery, update governance, regression checks, and safe tool use.

## Current public release

**MOS-2026.09.21.1**  
Generation: **v3**  
Channel: **stable**

Official public release pointer:

https://www.ijaspers.com/post/manager-os-release-channel

Machine-readable repository manifest:

`RELEASE_MANIFEST.json`

Stable public package links:

- PDF handbook: https://www.ijaspers.com/mos/download/pdf
- TXT pack: https://www.ijaspers.com/mos/download/txt

## Release naming

The governed stable release ID and the downloadable package build label are intentionally different identifiers:

- **Stable release ID:** `MOS-2026.09.21.1`
- **Generation:** `v3`
- **Current public package build:** `v2026.09.20-SX2`

Use the stable release ID for update/governance decisions. The package-build label identifies the currently downloadable bundle and may lag the release metadata while packaging catches up.

## Launch feedback

Public contribution intake and the private security-reporting lane are still **CLOSED** while those surfaces are being commissioned.

For now:

- If you found MOS through a public discussion (for example Reddit), leave normal usability feedback in that discussion.
- Otherwise use the iJaspers contact page: https://www.ijaspers.com/contact
- Do **not** post security-sensitive findings publicly.

This temporary feedback route does not bypass The Airlock or grant external material any write authority.

## Update model

A MOS installation may automatically **discover and verify** a newer release.

For scheduled checks, network-capable installations can use the privacy-preserving check path:

https://www.ijaspers.com/mos/check

That path redirects to the official release channel and supports aggregate check counting without requiring an installation ID or user identity.

It must **not automatically install a behavior-changing update**.

Before adoption, the local human operator must be shown:

- source and version;
- what changed;
- what it does;
- what it touches;
- material risk and rollback information;
- a recommendation.

The operator then chooses whether to implement it.

## Contribution status

**CLOSED while the public intake/security lanes are being commissioned.**

The contribution protocol is documented here so the security boundary is explicit before intake opens. Do not submit bugs, improvements, or security findings yet unless the manifest later says the appropriate lane is OPEN.

Security-sensitive findings must never be posted as public Issues.

## Security model

External material is untrusted by default.

Candidate changes are expected to pass through **The Airlock**:

`UNTRUSTED → QUARANTINE → REVIEW → CANDIDATE → REGRESSION TESTS → HUMAN APPROVAL → PROMOTION`

Quarantined material gets no private memory, secrets, privileged tools, or canonical write authority.

See:

- `SECURITY.md`
- `CONTRIBUTING.md`
- `CHANGELOG.md`
- `docs/UPDATE_PROTOCOL.md`
- `docs/OBSERVABILITY.md`
- `docs/AIRLOCK.md`

## Design principle

> The internet may suggest changes. It does not get admin rights.

MOS is AI-agnostic. The model is replaceable; durable operating state and human authority are not.
