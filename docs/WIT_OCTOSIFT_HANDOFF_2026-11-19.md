# OctoSift → WIT handoff | 2026-11-19

Status: SAVED / REVIEW CANDIDATE. Owner: existing WIT project; no new loop or automation.

## Done
- Read canonical MOS Home and relevant WIT public README.
- Reviewed upstream OctoSift README, AGPL-3.0-only LICENSE, architecture, sources, privacy, Docker and package manifest.
- Compared with WIT's existing Continuity Observer experimental prototype (commit 57c8de2, 61 reported synthetic tests), avoiding a duplicate observer.
- Created isolated branch `review/wit-octosift-patterns-20261119` from main.
- Committed `tools/WIT_OPPORTUNITY_DISCOVERY_EXPERIMENTAL_2026-11-19.md` as ec158d07583ff64bfd1cd7f84a31b73b1ed6f904 and verified GitHub readback.
- Independent design only; no upstream code copied, no secrets, accounts, purchases, outreach, or stable-release edits.

## Decision
ADOPT AS EXPERIMENTAL DOCUMENTED WORKFLOW ONLY. NOT an executable integration, live lead monitor, tested persistence implementation, or stable release. No promotion without evidence and operator approval.

## Next
When useful, dogfood on 10 public discussion examples with legitimate access, record scoring precision, human-reviewed drafts, source evidence, false positives and interruption/recovery. Reuse existing WIT state machinery. Do not pursue OctoSift runtime installation unless evidence justifies it.

## Blockers
No live Reddit access or runtime acceptance testing in this session. Reddit RSS and API restrictions remain an external dependency. No background task enabled.

## Links
- Branch: https://github.com/iJaspers/manager-os/tree/review/wit-octosift-patterns-20261119
- Workflow: https://github.com/iJaspers/manager-os/blob/review/wit-octosift-patterns-20261119/tools/WIT_OPPORTUNITY_DISCOVERY_EXPERIMENTAL_2026-11-19.md
- Upstream: https://github.com/Octosift/octosift

Combo-Breaker: one WIT owner; no duplicate scheduler, master, observer, or unverified success claim.
