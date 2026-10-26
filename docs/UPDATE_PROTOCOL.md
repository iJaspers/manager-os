# Witburrow Update Protocol (MOS-compatible)

## Purpose

Witburrow and legacy Manager OS installations can check an official upstream release record and compare it with the locally installed version.

## Weekly check

1. When network access is available, request the privacy-preserving public check URL once for the scheduled check cycle: `https://www.ijaspers.com/mos/check`.
2. Read the configured official release manifest.
3. Confirm the expected protocol, schema, channel, and source.
4. Compare the release ID with the last locally trusted release. Separately inspect known optional manifest extensions and their metadata revisions. A naming notice does not change the stable release ID or authorize installing anything. Unknown extensions are informational only; do not execute their contents or relax local schema/security validation.
5. Treat unexpected rollback, stale metadata, replay, or source mismatch as a reason to stop and request review.
6. If neither a release nor a supported optional notice materially changed, record the successful check and continue.
7. If a newer release or supported optional notice is available, present the local human operator with:
   - source and version;
   - material changes;
   - practical effect;
   - affected rules, workflows, integrations, permissions, schemas, or security controls;
   - material risk and rollback information;
   - a recommendation.
8. The human operator chooses IMPLEMENT, NOT NOW, REJECT, or REVIEW DETAILS.
9. Only an explicitly approved change proceeds through local compatibility, recovery, and regression checks.

## Optional Witburrow name transition - October 22, 2026

The manifest retains `protocol: MOS_UPDATE_EXCHANGE`, `schema_version: 1`, the stable release ID, and every existing artifact record. Its existing `notes` field announces the soft rename; `extensions.witburrow_brand_transition_v1` points to [WIT-NAME-2026.10.22.1](WITBURROW_BRAND_TRANSITION_2026-10-22.json), with its own metadata revision, byte length and SHA-256. A checksum checks byte consistency, not publisher authenticity.

This supplement is an opt-in display-name procedure, not a replacement package or executable installer. After verified-source review and explicit local approval, the framework display name becomes Witburrow. The manager default becomes Wit only when the local profile explicitly identifies the current name as an uncustomized legacy default. Preserve custom names, including deliberately chosen legacy-sounding names. Preserve unknown preferences and ask; never guess. Record prior display values, apply only the approved display changes, read back the result and retain rollback. No new permissions, schedules, technical identifiers or private data are involved.

Older installations may read only `release_id` and therefore not surface this optional notice automatically. A strict legacy parser may reject unfamiliar optional fields; do not disable validation. In either case, review the official setup/reference page or ask the manager to inspect this named supplement. Updating these public records does not update an existing installation remotely or prove host compatibility.

## Privacy-preserving check counter

The `/mos/check` request exists only to make aggregate scheduled update-check traffic measurable.

Do not attach an installation ID, user identity, device fingerprint, local state, prompts, transcripts, files, secrets, credentials, or custom query parameters containing local information.

A check-counter failure must not block safe update verification. Fall back to the configured official release records and respect the normal retry budget.

The resulting metric is **update-check requests**, not unique installations. See `docs/OBSERVABILITY.md`.

## Getting a reviewed tool improvement

The framework release ID and each public tool version are separate. A new tool version need not change the stable framework release ID. Check the [existing catalogue](https://www.ijaspers.com/post/witburrow-tools) and the exact tool source/version; a pull request or metadata-only idea is not an approved download. The public contribution policy remains limited to the IDs in [CONTRIBUTING.md](../CONTRIBUTING.md).

Before choosing an update, compare the current and proposed tool versions, reviewed source commit, changed behavior, known failures, runtime/input compatibility and release evidence. Keep your prior package and working record. The release handoff must state whether inputs or saved outputs require migration; unknown migration behavior means HOLD, not assumed compatibility. Never overwrite original user records as a test.

After explicit local approval, try the approved version with synthetic fixtures in the permitted host, verify the result and save the exact version with the work. If the check fails, stop using the candidate, keep the evidence, and restore the retained prior version and record only when that rollback is safe. A prior version with a known unsafe defect is not a safe fallback; disable the affected capability and request review instead. Rollback does not undo external actions or recover overwritten data automatically.

Publication and catalogue visibility are not notification delivery, installation, adoption or user acceptance. No new subscription, telemetry, schedule, permission or automatic installation is introduced. Existing configured update checks stay unchanged.

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

