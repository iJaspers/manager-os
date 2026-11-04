# Source-linked Handoff Review 0.1.0-public-draft.1

Public WIP derivative of existing **BOB-089 Source-Linked Handoff Gate v1.0.1**. It checks that a proposal identifies its owner, source, observation time and evidence, and flags unsupported resolution claims or reopening of closed work. It never writes tasks, fetches URLs, sends messages, changes ownership or grants approval. Useful for Bob/Combo-Breaker review handoffs and Spreadsheet My Life project updates; keep using the existing task owner and records.

Everyday use: ask your AI to draft a handoff with the owner, current source, evidence, proposed change and remaining unknowns. If the AI can execute this tool, have it check the draft. Without code support, review those fields conversationally and say that the software check was not run.

Power/Super use: extract this version's ZIP and run with Python 3.12+ (tested on 3.12.14/Linux; no dependency install):

```sh
python handoff.py example.json
python -B -m unittest discover -p 'test_*.py'
```

Exit 0 means `REVIEWABLE_HANDOFF_PROPOSAL`, **not accepted or resolved**. Exit 2 means `HOLD`; inspect the issue codes and correct the evidence. The included example is fictional. Source/evidence references can be HTTPS links or opaque local record references; this program neither opens them nor proves that they exist. A nonempty reference or a boolean confirmation cannot authenticate permission. Observation time must include a timezone, but its freshness is for the source owner to establish.

The CLI reads one regular UTF-8 JSON file, maximum 64 KiB, refuses final symlinks, duplicate JSON keys and malformed input, and returns generic input errors without paths or source contents. Optional action/claim flags must be booleans. Unknown fields are held. The small pure `evaluate(dict)` API implements the same review logic; callers of that API own input byte/depth limits. Keep private proposals/results in private storage. No analytics, network, global setup, scheduler or memory store is used.

The nine recovered source scenarios remain, with a fictional owner/task and timezone-qualified fixture. Additional tests cover public input and CLI boundaries. The private original and its identity are preserved; this is one public derivative, not another Bob build credit. See [PROVENANCE.md](PROVENANCE.md).

Limits: a structural check is not independent evidence review, security acceptance, legal/accounting advice or proof that a source-world task was completed. Actual cross-host, mobile and Windows behavior remain unverified. Rollback by returning to your prior manual handoff process; there are no account or global changes to undo.
