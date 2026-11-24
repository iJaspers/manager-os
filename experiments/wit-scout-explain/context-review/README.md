# What WIT used — context and proposed-memory review

**Status: experimental review candidate, 0.1. No stable release or host activation.**
This is an additive view for the existing `wit.scout-explain` component. It
reuses the versioned Scout source at
[`tools/scout-explain/0.1.0-public-draft.1`](../../../tools/scout-explain/0.1.0-public-draft.1/).
It does not introduce another memory store, checkpoint format, agent, or scheduler.

## What changed

- **What WIT used:** shows the sources involved in this handoff's ranking,
  displayed findings and claim checks, including failed reads, missing citations
  and results omitted from the short findings list. It explains each source's role.
- **Coverage:** separates complete, checksum-checked pinned GitHub files from
  snippets and other retrieved text whose completeness is not attested.
- **Dates and versions:** shows actual retrieval observations and pinned revisions.
  A retrieval date is not a publication date; a pinned file is not necessarily latest.
- **Usage:** keeps a host's last-request measurement separate from a rough
  source-text estimate. Missing model usage stays unavailable; no context percentage
  is invented. The report does not claim to observe another model's entire prompt.
- **Proposed memories:** displays existing research claims with their evidence,
  hold reasons, and genuine prior wording when an earlier authorized session is
  supplied. These are proposals, not automatically stored or approved memories.
- **Review changes:** reuses the existing handoff binding. Changed evidence can
  require review even when the statement text stays unchanged.

The HTML is self-contained, with native disclosure controls and no scripts,
remote assets, forms, tracking, or approval buttons. Source strings are escaped;
external navigation accepts only explicit HTTP(S) links.

## Try the fictional example

Run from the repository root with Python 3. No dependency installation is needed:

```sh
python -B experiments/wit-scout-explain/context-review/review.py --demo --include-source-details --html review-new.html
```

Open the resulting HTML file. Choose an unused output filename: existing files
and final-component symlinks are refused. The fictional example intentionally
includes a failed source and a held claim. `HOLD` is a review result, not a CLI crash.

The [Incognide example](examples/incognide_review.html) is a derived report from
five actual public connector reads, subsequently replayed offline through Scout.
[Its receipt](examples/DOGFOOD_RECEIPT.json) records exact source revisions/hashes
and the observed recovery result. It is not an Incognide runtime benchmark.

## Use an existing research session

`build_review_view(session, previous_session=None, usage=None,
include_source_details=False)` consumes the existing `ResearchSession` from
Scout's trusted host or `load_research_checkpoint()` API. `render_review(report)`
renders that derived view. Keep this experiment inside the repository so its
fixed versioned base dependency resolves correctly.

Checkpoint CLI mode requires independently retained expected values:

```sh
python -B experiments/wit-scout-explain/context-review/review.py \
  --checkpoint /authorized/path/research.json \
  --expected-sha256 CALLER_RETAINED_SHA256 \
  --code-revision EXPECTED_REVISION \
  --source https://example.org/approved-source \
  --html review-new.html
```

Repeat `--source` for every approved URL. Do not copy the expected digest,
revision or allowlist out of an untrusted checkpoint to make it pass.
The CLI performs no source retrieval. Real authorization and storage protection
remain the calling host's responsibility.

The default omits source titles, URLs, excerpts and source timestamps. It still
contains the goal and proposed statements and **is not a public-redaction tool**.
Enable source details only for an audience already authorized to see that material.
An input boolean does not authenticate the audience.

## Owner confirmation and memory boundaries

Owner confirmation is always **NOT_VERIFIED** in this candidate. No input
`human-approved`, `owner_confirmed`, `authenticated`, lifecycle status or
successful quote check can create a confirmation badge. Unknown claim fields
are rejected by the existing strict schema. A `UsageObservation` is a host-owned
measurement contract, not authentication of an imported assertion.

This view reads existing claims. Editing, rejection, adoption and authenticated
owner decisions belong to the existing owning application. The separate open
memory-reliability pilot is not merged, copied or promoted by this work.

## Verification, provenance and rollback

See [REVIEW_NOTES.md](REVIEW_NOTES.md) for exact tests, dogfooding, the independent
review correction, and the remaining browser/device limit. See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for attributed inspiration and
the source-quote notice.

Remove this experiment and its routing paragraph to stop using it. Existing
Scout releases, checkpoints, downloads, stable starter files and public catalogue
are unaffected. A generated report can be discarded; it is not a canonical store.
There is no migration or hidden background process to undo.

The WIT base's source-visible rights position remains in force; this candidate
does not add a blanket licence grant to unrelated WIT source or third-party work.
