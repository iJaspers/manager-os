# WIT opportunity discovery checkpoint | 2026-11-19 continuation

## DONE
- Used connected GitHub issue search and authenticated issue fetch to retrieve a real public issue: https://github.com/Tiny-Robot-Lab/autonomous-agent-lab/issues/58 (open, created 2026-11-05).
- Manual classification: context-window budgeting issue is topically relevant, but an implementation task, not an explicit request for a WIT product recommendation. Do not contact or promote.
- Found a safety flaw: offline GitHub adapter set status_checked=True solely from caller-provided JSON. Changed default to False until trusted verification is supplied by an authorized source.
- Added a stdlib-only Hacker News normalization adapter, with six test scenarios. No API requests or credentials.
- Existing offline scoring, SQLite persistence and safety rules retained. No stable release modifications.

## TEST STATUS
- Prior 24/24 local test result belongs to the earlier code snapshot, NOT this updated snapshot.
- New Hacker News tests are written but NOT executed. Full regression after these commits remains pending.
- GitHub tool fetch verified the example issue's live state at observation time. This does NOT independently validate community promotion permission, buyer intent, or WIT feature fit.
- Current runtime cannot clone GitHub directly (DNS unavailable). GitHub connector writes/readbacks do not equal a runtime acceptance test.

## NEXT
1. Run full unittest discovery on a local checkout, including the new HN tests.
2. Use approved, read-only source acquisition to normalize issue/HN records, preserving origin timestamps and evidence.
3. Improve provenance: a caller-supplied boolean must never substitute for independently verified rules, live status, product evidence or user intent.
4. Test crash/replay/concurrency and source-to-record roundtrip before promotion.

## WAITING ON
Runtime regression and live HN feed acceptance. No external posts, account connection, spend or schedule.

## COMBO-BREAKER
One experimental owner and branch; no duplicate watcher, daemon, master or scheduler. No automatic adoption into stable WIT.
