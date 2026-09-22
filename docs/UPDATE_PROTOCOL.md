# Manager OS Update Protocol

## Purpose

Manager OS can check an official upstream release record and compare it with the locally installed version.

## Weekly check

1. Read the configured official release manifest.
2. Confirm the expected protocol, schema, channel, and source.
3. Compare the release ID with the last locally trusted release.
4. Treat unexpected rollback, stale metadata, replay, or source mismatch as a reason to stop and request review.
5. If nothing material changed, record the successful check and continue.
6. If a newer release is available, present the local human operator with:
   - source and version;
   - material changes;
   - practical effect;
   - affected rules, workflows, integrations, permissions, schemas, or security controls;
   - material risk and rollback information;
   - a recommendation.
7. The human operator chooses IMPLEMENT, NOT NOW, REJECT, or REVIEW DETAILS.
8. Only an explicitly approved change proceeds through local compatibility, recovery, and regression checks.

## Authority boundary

Finding a release does not authorize changing the local installation.

A successful download, validation result, maintainer statement, or urgent notice also does not replace the local operator's decision.

A security concern may justify temporarily isolating an affected capability while it is reviewed. That isolation does not itself approve a proposed change.

## Official release records

Repository manifest:

`RELEASE_MANIFEST.json`

Public release channel:

https://www.ijaspers.com/post/manager-os-release-channel

If official sources materially disagree, stop and request review rather than selecting one silently.
