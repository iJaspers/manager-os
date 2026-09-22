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

## Update model

A MOS installation may automatically **discover and verify** a newer release.

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
- `docs/UPDATE_PROTOCOL.md`
- `docs/AIRLOCK.md`

## Design principle

> The internet may suggest changes. It does not get admin rights.

MOS is AI-agnostic. The model is replaceable; durable operating state and human authority are not.
