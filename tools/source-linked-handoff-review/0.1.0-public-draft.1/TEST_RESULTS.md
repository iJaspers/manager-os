# Executed checks — 2026-11-03

`python -B -m unittest discover -s tools/source-linked-handoff-review/0.1.0-public-draft.1 -p 'test_*.py'`: **25 passed**, Python 3.12.14 on Linux.

Nine recovered BOB-089 scenarios preserve source behavior with fictional owner/task and a timezone-qualified observation. Sixteen additional cases cover bounded fields/evidence, typed flags, timezone requirements, unknown fields, malformed UTF-8, duplicate JSON keys, oversized CLI input, final symlinks, missing files, successful execution and a nonzero HOLD exit. No third-party runtime dependency.

The actual PR #10 handoff was also checked: a source-linked proposal returned REVIEWABLE_HANDOFF_PROPOSAL; missing evidence and an unsupported resolution claim returned HOLD. The output was saved, read back and hash-checked in a new local process. See the existing release directory SHIP_DOGFOOD.json and the subsequent SHIP_RELEASE_RECEIPT.json for durable public readback.

Not run: Windows/mobile behavior, fresh native ChatGPT/Gemini trials or independent security/product acceptance. A reviewable proposal is not verified source truth, owner approval or completed work.
