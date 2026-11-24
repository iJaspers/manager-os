# Publication review — 23 November 2026

## Decision and authority

Publish the selected, sanitized WIT research tools as **experimental source previews** under the existing maintainer publication route. The project owner explicitly authorized updating and publishing the material after private data was removed. This is a scoped publication decision, not a new framework-stable release, production acceptance or expansion of outside contribution intake.

The publication was prepared from default-branch commit `8e856b13f189a9e2f9c27ea445a69f440e582bd4`. Public experiment [PR #14](https://github.com/iJaspers/manager-os/pull/14) targets a different experiment branch; its history was not merged wholesale. The new default-branch publication preserves the newer first-task guide and existing release artifacts.

## Included scope

| Component | Identity and scope |
|---|---|
| Scout + Explain | `wit.scout-explain`, `0.1.0-public-draft.1`; 25 selected runtime/test files plus five fresh public documentation/example files |
| School Contact Scout | `wit.school-contact-scout`, `0.1.0-preview.1`; generic original utility, fictional baseline and scope-specific documentation |
| Phone guide | Existing-host WIT setup, capabilities, manual return note and accurate Python/runtime limits |
| Combined bundle | Both tool previews and the unchanged public starter text, handbook and optional companion RC1 |
| Repository discovery | README links, changelog, experiment-path continuation note and version-pinned catalogue records |
| CI | Reviewed branch/main paths; read-only token, pinned checkout, bounded runtime, no dependency install, secrets or pull-request trigger |

## Privacy and source review

The selected source and new documentation were read before execution. A separate reviewer checked the candidate inventories, private-reference patterns, network boundaries and public claims. Real contact baselines and recipient details, private source captures, task/account links, operational records, historical integration notes and generated recovery outputs were excluded. School examples use reserved domains and fictional people and institutions.

Archive contents are enumerated and checksummed. Tool ZIP members match the reviewed source, and the combined bundle contains those same bytes plus the previously public starter artifacts. Hashes identify content; they do not authenticate an author or certify source truth. The final package hashes and byte sizes are in PACKAGES.json.

No copied external runtime library was identified in the selected implementation. Public-source excerpts/identifiers retained in Scout fixtures are identified in its provenance. Each tool has its own source-visible rights notice; no blanket MIT grant is inferred. The optional companion's existing scoped notice is preserved inside its unchanged archive.

## Observed local verification

Environment: Python 3.12.14, Node.js 24.22.3, Linux x86_64. Checks used fictional inputs and stub host/connector responses; no live school requests or marketing messages were sent for this public release.

| Check | Result |
|---|---|
| Scout Python regressions, source and extracted tool ZIP | 135 passed in each run |
| Scout JavaScript regressions, source and extracted tool ZIP | 20 passed in each run |
| School Contact Scout self-tests, source and extracted tool ZIP | 21 passed in each run |
| School network-boundary independent focused checks | 8 passed, with live DNS/socket calls guarded |
| Fictional Scout CLI example | Two findings, explicitly unverified snippets; exit 0 |
| Archive integrity and member readback | Three ZIPs passed; per-member hashes checked |

Counts refer to distinct tests reported by each runner, not a cumulative claim that repeated runs create new tests. Catalogue projection checks are rerun when the new records are pinned to the immutable source commit. Remote CI status and public download readback must be assessed from the actual publication commit/run, not assumed from these local results.

The School Contact Scout review found and fixed two concrete network weaknesses in the earlier implementation: hostname validation did not validate/pin resolved public IPs, and inherited redirect handling drained an unbounded response body. The preview now validates all DNS answers, pins connections, preserves TLS hostname checks, disables proxies, skips/closes redirect bodies and tests those boundaries. It still has per-operation timeouts and OS-controlled DNS resolution, not a strict total wall-clock deadline or complete hosted-service sandbox.

## Remaining limits and next useful step

Both tools remain locally tested, nonproduction previews. Scout's host is responsible for authorized retrieval; its local input readers are not arbitrary-upload admission boundaries. Checkpoints contain complete source material and require appropriate private storage. Quote/hash agreement does not establish semantic truth. School publication observations do not establish employment, deliverability or permission to contact.

Native phone execution, Windows, live end-to-end hosted acquisition, independent security/semantic acceptance and production capacity have not been established. The recovery tests intentionally terminate their own synthetic POSIX acquisition subprocesses. The release includes no autonomous LinkedIn crawler, scheduled background service or automatic outreach.

The next useful step is a bounded trial with an authorized host and a small reviewed input, followed by inspection of the saved result and return note. A separate website embed or existing installation does not update merely because this repository changed.

## Rollback

Retain previous version directories and release artifacts. Users can stop invoking the previews and keep their working records. Maintainers can withdraw the catalogue entries or revert the additive publication commits; never replace a released ZIP with different bytes or rewrite public history. No permissions, accounts or schedules need to be reversed by these source tools.
