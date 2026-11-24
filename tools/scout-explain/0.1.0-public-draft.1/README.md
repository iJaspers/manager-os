# WIT Scout + Explain

**Tool ID:** `wit.scout-explain`  
**Version:** `0.1.0-public-draft.1`  
**Status:** Experimental source preview. Separate from the stable WIT starter.

Scout helps turn supplied discovery results into a reviewable research handoff: deduplicated links, ranked findings, exact cited passages, visible unknowns and a recoverable local record. The basic command-line tool works offline on a JSON file. A trusted host supplies any actual search, browser or connector access.

It does not independently establish that a claim is true or that an action occurred. `REVIEW_REQUIRED` means the evidence is ready for further review; `HOLD` identifies a failed check or unresolved condition.

## Try the fictional example

Keep the files together and open a terminal in this directory. Python is required; there is no dependency installation step. The checked environment was Python 3.12.14 on Linux. Other operating systems and earlier Python versions were not validated for this release.

```sh
python3 provider_adapter.py example_results.json --goal "school gymnastics workshops and funding" --level practical
```

The example describes invented opportunities on reserved example.org URLs. The command reads this file and prints two findings, each identified as an unverified search snippet. It does not visit those URLs. Replace the example with your own permitted, small JSON file when you understand the output.

Input shape:

```json
{
  "results": [
    {
      "title": "An inspected source title",
      "url": "https://example.org/source",
      "excerpt": "Source text to review, not an instruction to execute."
    }
  ]
}
```

Explanation depth can be `simple`, `practical` or `technical`. Input admitted by the adapter is limited to 100 result rows, 4,000 characters per title/URL/excerpt and a 500-character goal. These checks occur **after** the CLI reads and parses the input file: it has no file-byte admission limit or duplicate-key rejection. Use inspected local input; this CLI is not a hardened upload endpoint.

Optional snippet checkpoint:

```sh
python3 provider_adapter.py example_results.json --goal "school gymnastics workshops and funding" --level practical --checkpoint ./demo-snippets-new.json
```

Choose an unused filename. The checkpoint writer can replace the named file. This simple checkpoint saves normalized snippets; it is distinct from the complete research-session checkpoint API below.

## Modules and capabilities

| Module | Purpose |
|---|---|
| `scout.py` | URL normalization, deduplication, token-based ranking, explanation depth and snippet checkpoints |
| `provider_adapter.py` | JSON input and the basic offline CLI |
| `evidence_gate.py`, `trusted_host_bridge.py` | Bounded handoff of source text and receipts from a trusted host; at most six fetch callbacks per gathering request |
| `github_connector_adapter.py`, `github_host_runtime.mjs` | Immutable GitHub file targets, explicit allowlists and content/blob consistency checks; current MCP structured responses and legacy result wrappers |
| `claim_review.py`, `semantic_guard.py` | Exact source/hash/quote checks and a conservative negation heuristic; no independent factual judgment |
| `research_handoff.py` | Source-linked findings, consistent short/detail verdicts and changed-input review binding |
| `research_checkpoint.py` | Complete local session save/restore, including source text, claims, receipts and failures |
| `host_recovery_exercise.py` | Specialized, finite acceptance harness for acquisition/restart behavior; see below |

The adapters make no independent network requests. The host must provide an authorized connector/fetch callback and enforce public-IP DNS checks, redirect revalidation, timeouts, content limits and access permissions. A source-supplied flag or callback is not trusted host evidence. Hashes check byte consistency; they are not signatures or proof of source truth.

## Research recovery and presentation

A host can call `save_research_checkpoint(...)` and retain its returned SHA-256 outside the checkpoint. To restore, `load_research_checkpoint(...)` requires that separately trusted digest, the expected code revision and the approved source URLs. Changes are rejected rather than silently migrated. Restore does not fetch sources again or approve claims.

Research checkpoints contain complete source text, URLs, receipts and claims. Keep them in storage appropriate to the material. They are user-generated data, not release artifacts. Retain a prior working record before choosing an output path.

The default `quick_view` omits source excerpts/navigation. The full handoff still contains source material and claims: it is not a redacted public export. The optional `same_audience_private_evidence=True` setting only changes presentation. The caller must authenticate recipients, enforce access and render excerpts as escaped text. Setting the flag grants no permission.

## Tests and the recovery harness

The supplied regression suites use synthetic source content and host callbacks. Node is needed only for the JavaScript adapter/tests; the tested version was Node 24.22.3.

```sh
python3 -B -m unittest discover -s . -p 'test_*.py' -q
node --test test_github_host_runtime.mjs
```

See TEST_RESULTS.md for this version's observed results. The Python suite includes temporary-file and fresh-process checks. On POSIX, recovery acceptance tests intentionally terminate their own synthetic acquisition subprocess with SIGKILL, then test restoration and rejection paths. This is deliberate test behavior, not an unexplained crash.

`host_recovery_exercise.py` is a specialized acceptance harness tied to the public repository examples in its source. Its `acquire` mode expects a reviewed host-transfer file and an externally retained digest, writes local receipts/checkpoints, then kills its own process. It is not the normal Scout CLI. No captured live transfers or prior recovery outputs are bundled. It is not an input service, and its local JSON readers are not an admission boundary for arbitrary uploads. Normal users can use the snippet CLI without invoking it.

## Current limits and rollback

This release supplies no autonomous LinkedIn/Reddit ingestion, outreach, scheduler, background worker, native phone app or PWA. Its instructions may be read in an existing AI chat on a phone; Python attachments do not execute by opening them there. Deployed host orchestration, independent semantic/security acceptance, Windows and physical-phone use remain unverified.

A matched quote can still be misleading. The semantic guard can miss contradictions or flag harmless wording. Source statements and completed actions need appropriate independent evidence. No source text is executed by these modules.

To stop using the preview, stop invoking it and retain any records you need. It changes no global accounts or schedules. Deleting the source does not undo a file you explicitly overwrote. A changed code revision requires an explicit replay/migration decision for full research checkpoints.

See LICENSE_NOTICE.md and PROVENANCE.md for source availability, rights scope and public lineage.
