# Source-linked handoff presentation — November 22, 2026

Status: **EXPERIMENTAL / REVIEW ONLY**. This extends the existing Scout experiment and draft PR 14. It is not a deployed WIT interface or a release. Implementation base: `3a843a6ef1f0060c7196dd452bf6468bb5ae5b6e`.

## Problem and resulting behavior

The previous handoff checked citations but did not put the statement, exact excerpt and usable source location together. It also had no comparison with an earlier review's inputs. A reader could therefore have difficulty finding the evidence or noticing that a recommendation had changed since review.

`research_handoff.py` now adds three presentation fields to its existing v1 output. Existing positional inputs and strict claim-v1 schema remain compatible.

- `claim_details`: exact claim text, effective verdict, separate structural and semantic precheck results, cited excerpts, expected/observed hashes and navigation metadata.
- `quick_view`: the same effective claim verdicts and issues, with material limitations retained at every explanation level. Changing depth cannot hide a hold or suggest a runtime test happened.
- `review_binding`: a versioned SHA-256 fingerprint of the question, existing claim bundle and source navigation identities. It records the previous fingerprint and `NEW`, `UNCHANGED` or `INPUTS_CHANGED`. An input change holds the current handoff for fresh review. No earlier approval is imported, even when the fingerprint is unchanged.

The binding is a comparison of supplied inputs, not authentication, semantic equivalence or an action receipt. Wording-only changes may conservatively trigger review. Callers must retain the old handoff in their existing history and pass its fingerprint when comparing an update; this module does not create a persistence store.

```python
first = build_handoff(payload, goal, claims, documents, "simple")
updated = build_handoff(
    payload, goal, revised_claims, documents, "technical",
    previous_binding=first["review_binding"]["sha256"],
)
```

## Source navigation contract

| Evidence | Navigation provided |
|---|---|
| Unique exact quote in an immutable GitHub file read through the existing trusted connector adapter | Commit-pinned source URL with calculated inclusive line anchors |
| Unique exact quote in another host-fetched text | Source page URL plus quote and character offsets into the retained decoded text |
| Repeated exact quote | Source page and excerpt, explicitly marked ambiguous; no invented unique location |
| Missing source, changed content digest or absent quote | Unavailable navigation and an explicit evidence issue |

Only matched host text is labelled `MATCHED_HOST_TEXT`. Other displayed quotes remain supplied citations. The output contains untrusted strings for a consuming renderer to escape; it does not render HTML or execute source text. Generic offsets are not PDF pages, audio timestamps, byte offsets or browser DOM coordinates. A provider's `official`, `tested` or `approved` field does not establish those statuses.

## Real-source exercise: TenderLayer

The user-supplied Reddit screenshot describes an autonomous submission capability. The inspected desktop README describes that agent as planned. The documentation does not by itself establish current runtime capability, and the discrepancy does not prove that no implementation exists elsewhere.

An actual GitHub connector read retrieved the complete README at this immutable revision:

- Repository: `arhamkhnz/tenderlayer`
- Commit: `abd966220d6bd461d6326e5a39a5a7ec37d6543f`
- File: `apps/desktop/README.md`
- Git blob SHA-1: `0f04f07ead8fa359d2d0d710cf825aa515409599`
- Text SHA-256: `0f4e8cd050a5dc751a037e8ca509ff9de8da7a8a57beab2473bd8effd9558bf5`
- Observation: `2026-11-23T04:44:28Z` (November 22 in the user's local date)

The actual connector response was then replayed offline through the existing GitHub adapter, trusted host bridge and updated handoff. The adapter checked the Git blob checksum. The README digest matched the earlier source review. This is a real fetched-source replay, not a continuous deployed connector or a product runtime test.

Observed outcomes:

1. The documentation claim stayed `REVIEW_REQUIRED`, with the semantic precheck still `NEEDS_SEMANTIC_REVIEW`.
2. The two unique excerpts produced links to the [planned-features heading at line 37](https://github.com/arhamkhnz/tenderlayer/blob/abd966220d6bd461d6326e5a39a5a7ec37d6543f/apps/desktop/README.md?plain=1#L37) and [agent item at line 47](https://github.com/arhamkhnz/tenderlayer/blob/abd966220d6bd461d6326e5a39a5a7ec37d6543f/apps/desktop/README.md?plain=1#L47). These positions were checked against the exact fetched file; browser clicking was not exercised. A separate agent's code review identified GitHub's rendered-Markdown line-link limitation; the final implementation forces source view with `plain=1`, following [GitHub's guidance](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-a-permanent-link-to-a-code-snippet#linking-to-markdown).
3. Moving from the simple to the technical view kept the same claim status and fingerprint (`58739acc629d05ba0882585cfd44a10152e96dcfbf34b60c3946bc93d5190728`).
4. Replacing the statement with an assertion that a working agent already exists changed the fingerprint to `c6a4f8c8f84231f7822f0147d788ac3022d354e4ffa84423dfe380d28667e19e`. Passing the earlier fingerprint yielded `INPUTS_CHANGED` and effective `HOLD` in both views.

The final hold comes from detecting changed review inputs. It is not an automated semantic determination that the new statement is false. No TenderLayer code was installed, run, copied or licensed for adoption. The original screenshot remains screenshot evidence; it was not misrepresented as host-fetched web text.

## Verification

Local baseline at the implementation base: **75 Python tests and 9 Node tests passed**. After this change: **87 Python tests and 9 Node tests passed**. Commands from repository root:

```sh
python3 -B -m unittest discover -s experiments/wit-scout-explain -p 'test_*.py' -v
node --test experiments/wit-scout-explain/test_*.mjs
git diff --check
```

The twelve new Python tests use synthetic source content. They cover unique and ambiguous excerpts, immutable versus mutable GitHub locations, newline boundaries, unavailable evidence, changed claims and documents, changed question/target/retrieval method, explanation-depth consistency, forged prior verdicts, promotional provider flags and unsupported completion claims. The existing suite remains passing. The diff whitespace check passed.

These are bounded regression and real-source replay checks. Browser/mobile UI, deployed host orchestration, restart of a consuming app, independent factual judgments and external security acceptance remain unestablished.

## Ownership, next integration and rollback

This patch adapts source-navigation and layered-explanation ideas from the reviewed projects without importing implementation code or dependencies. It adds no scheduler, task owner, external action or second evidence store.

Next-actor and exact sent-artifact presentation must consume the existing authoritative task/receipt interface. This Scout API has no such input. That separate integration is left explicit rather than inventing an owner or treating a prepared artifact as delivered. A consuming interface should persist the binding with its existing handoff, display the shared effective verdict, and treat all excerpts as untrusted text.

Rollback: revert this scoped change to `research_handoff.py`, its new test module and this checkpoint/README pointer. Keep the existing experiment isolated; no merge, stable packaging or deployment follows from passing tests.
