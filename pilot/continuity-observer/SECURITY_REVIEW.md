# WIT Continuity Observer | bounded adversarial source review

Date: 2026-11-12. Scope: only `pilot/continuity-observer/` on review branch PR #12. This is an attended code/test review, **not an independent security certification** or live-host acceptance.

## Inspected surfaces

| Question | Finding | Evidence / remaining gap |
|---|---|---|
| Copies from third-party source? | No vendor implementation found in this pilot | Python stdlib implementation and WIT-authored synthetic fixtures; comprehensive originality/legal clearance is not claimed |
| Unintended network transmission? | None in runtime scorer | Runtime imports Python stdlib only; CLI has no HTTP client, sync hook or telemetry; executing recorded AI responses is not supported |
| Input handling? | Hardened | Strict JSON keys/IDs, duplicate-key and NaN rejection; final-component symlink/FIFO/directory rejection; bounded opened-file read. Parent-path symlink races and OS-level I/O faults are not an absolute sandbox |
| Tool/action proof? | **Not implemented, explicitly warned** | `claimed_actions` are statements from a recording. This tool does not authenticate tool logs, actual sends, user identity, file effects or external transfers |
| Oracle contamination? | Separate export | `prompts` omits expected answers, while private test conduct still needs isolation from case files and synthetic answers; real-host independence untested |
| Misleading improvements? | Guard added | Same-case baseline/candidate comparison labels missing observations INCOMPLETE and prevents a green status when candidate coverage or baseline comparability is missing |
| Scope / release permissions? | Unchanged | Review branch only, no main merge, website, stable installer, scheduled workflow, paid API or host integration |

## Reproduction (offline)

From this directory: `python -m unittest discover -s . -p 'test_*.py' -v` (45 pass on the local Python runtime). `python observer.py compare --cases cases.json --baseline synthetic_pass.json --candidate synthetic_fail.json` intentionally exits 1 with 2 regressions. The reverse comparison intentionally exits 0 with 2 *field-level* improvements, not evidence of a better live AI.

## Open acceptance gates

A separately isolated model must receive only the prompt export, produce actual recorded answers and leave an attributable run log. A human reviewer must inspect tool traces and any relevant target readbacks before calling behavior verified. Repeat in a second host before cross-AI reliability claims. Do not put real customer, tax, employee or private WIT data into a public fixture. Existing owner approval still governs merge and release.
