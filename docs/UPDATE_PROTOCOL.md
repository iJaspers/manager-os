# Manager OS Update Protocol

## Purpose

Manager OS can check an official upstream release record and compare it with the locally installed version.

## Weekly check

1. When network access is available, request the privacy-preserving public check URL once for the scheduled check cycle: `https://www.ijaspers.com/mos/check`.
2. Read the configured official release manifest.
3. Confirm the expected protocol, schema, channel, and source.
4. Compare the release ID with the last locally trusted release.
5. Treat unexpected rollback, stale metadata, replay, or source mismatch as a reason to stop and request review.
6. If nothing material changed, record the successful check and continue.
7. If a newer release is available, present the local human operator with:
   - source and version;
   - material changes;
   - practical effect;
   - affected rules, workflows, integrations, permissions, schemas, or security controls;
   - material risk and rollback information;
   - a recommendation.
8. The human operator chooses IMPLEMENT, NOT NOW, REJECT, or REVIEW DETAILS.
9. Only an explicitly approved change proceeds through local compatibility, recovery, and regression checks.

## Privacy-preserving check counter

The `/mos/check` request exists only to make aggregate scheduled update-check traffic measurable.

Do not attach an installation ID, user identity, device fingerprint, local state, prompts, transcripts, files, secrets, credentials, or custom query parameters containing local information.

A check-counter failure must not block safe update verification. Fall back to the configured official release records and respect the normal retry budget.

The resulting metric is **update-check requests**, not unique installations. See `docs/OBSERVABILITY.md`.

## Authority boundary

Finding a release does not authorize changing the local installation.

A successful download, validation result, maintainer statement, or urgent notice also does not replace the local operator's decision.

A security concern may justify temporarily isolating an affected capability while it is reviewed. That isolation does not itself approve a proposed change.

## Official release records

Repository manifest:

`RELEASE_MANIFEST.json`

Privacy-preserving public check URL:

https://www.ijaspers.com/mos/check

Authoritative public release channel:

https://www.ijaspers.com/post/manager-os-release-channel

If official sources materially disagree, stop and request review rather than selecting one silently.
