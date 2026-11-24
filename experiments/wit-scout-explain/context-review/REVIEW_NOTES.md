# Context-review candidate — implementation and acceptance record

Date: 23 November 2026 (America/Dawson_Creek).

## Source and scope

- WIT base commit: `a2789ef29a7a34b7709c01beb5d92600cb1f35c6`.
- Incognide comparison: `5f302fd4a8bbd2beffb6301608bed7acde0e619d`.
- Additive files under the existing Scout experiment only; released source bytes
  and frozen packages are preserved.
- The isolated branch starts from the verified clean default-branch checkout.
  Existing experimental PRs #13 and #14 are preserved.

## Combo-Breaker decisions

| Candidate | Decision | Reason |
|---|---|---|
| Visible context and source roles | Implemented as an additive read-only view | Helps users inspect the actual handoff inputs |
| Memory review with source and prior wording | Implemented as a projection of existing claims | Adds inspectability without a second store |
| Another save/restore implementation | Already covered; reused existing checkpoint APIs | Avoids parallel recovery state |
| Import the separate memory-reliability pilot | Deferred | Metadata eligibility does not authenticate owner confirmation |
| Incognide desktop/runtime dependency | Deferred | The two selected patterns require no desktop dependency |
| Automatic memory approval or mutation | Outside this candidate | No authenticated owner-write integration exists here |

BUILT and TESTED apply to the candidate below. Stable integration, independent
host acceptance and release do not follow from those states.

## Observed automated checks

Checked on Python 3.12.14 and Node 24.22.3, Linux:

```sh
python -B -m unittest discover -s experiments/wit-scout-explain/context-review -p 'test_*.py' -q
python -B -m unittest discover -s tools/scout-explain/0.1.0-public-draft.1 -p 'test_*.py' -q
node --test tools/scout-explain/0.1.0-public-draft.1/test_github_host_runtime.mjs
```

- 45 candidate tests passed: view/trust/recovery behavior, HTML escaping and
  link/privacy handling, and CLI loading/output behavior.
- 135 existing Scout Python regressions passed.
- 20 existing JavaScript connector regressions passed.
- Total: **200 automated tests passed**, not 200 new features or real-host trials.

Meaningful negative cases include injected approval fields, approval language
inside a source, source/hash/receipt changes, missing sources, failed retrieval,
duplicate claim IDs, changed completion claims, invalid usage measurements,
source disclosure in summary mode, hostile HTML/URLs, output overwrite/symlinks,
and conflicting import paths. Existing checkpoints were restored in a new
Python process and the derived report compared exactly.

## Independent bounded review

A separate reviewer inspected the core and ran synthetic probes. The reviewer
found an import-order defect when the correct base path already appeared lower
in `sys.path`. The fix moves the exact versioned directory to the front and
checks resolved module locations. Two regression tests cover path shadowing
and preloaded conflicting modules.

The renderer also distinguishes **statement unchanged** from **evidence changed**.
A changed source with unchanged wording remains held through the existing review
binding. This review was not an independent security certification of the host.

A final separate source/artifact review found no blocker to a draft PR. It checked
the import fix, deliberate output writes, absence of network/approval mutations,
source-detail suppression, escaped rendering, public-only example data, matching
HTML/receipt hashes and the stated acceptance limits. That final reviewer did not
rerun the suites or independently repeat the connector reads.

## Actual source dogfood

Five pinned public GitHub files were read through the host connector at
`2026-11-24T03:51:37+00:00`, then transferred to the offline adapter and verified
against their Git blob checksums. The full source bodies were retained only in
working evidence, outside this candidate's tracked files.

The candidate produced five proposals, all **REVIEW_REQUIRED**, with complete
pinned-file coverage. It correctly displayed model usage as unavailable and
owner confirmation as unverified. A new process restored the existing checkpoint
and produced the identical report. Injecting an `owner_confirmed` field was
rejected. A deliberately altered completion claim produced **HOLD / INPUTS_CHANGED**.

The script `dogfood_incognide.py` reproduces that finite exercise from a trusted
host transfer and an independently retained transfer digest. It does not fetch
sources, run a model, install Incognide or perform a memory write.

Exact derived outputs: [HTML example](examples/incognide_review.html),
[report data](examples/incognide_review.json), and
[source/recovery receipt](examples/DOGFOOD_RECEIPT.json).

## Remaining limit

**Rendered-browser acceptance is BLOCKED, not passed.** Playwright's bundled
Chromium was absent. A targeted attempt with the installed Chromium failed at
startup with `socket() failed: Operation not permitted`. No page rendered and
no screenshot was obtained. Responsive layout and wrapping have static checks;
real Android/iOS behavior and accessibility interaction remain unverified.

NEXT: inspect the generated HTML in a working browser/device, then decide on
promotion of this exact candidate. No stable release or real-host activation
is claimed. Existing WIT recovery/authority limitations still apply.
