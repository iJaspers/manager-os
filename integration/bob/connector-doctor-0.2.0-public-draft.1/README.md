# Optional Bob connector supplement

Attach `BOB_WITH_CONNECTOR_DOCTOR_0.2.0-public-draft.1.txt` to an existing WIT chat. Ask Bob for one fictional task. Bob should use current host tools when actually available, respect permissions, check results, and otherwise continue in conversation. No Node installation is needed to use the text.

This is WIP, separate from the frozen 2026.11.01-rc1 release. It inserts one optional host-check step and a visible WIP banner. Bob's original text and MIT notice remain byte recoverable. It does not install apps or transfer credentials between AIs. See NOVEMBER_6_ACCEPTANCE.md for the existing trial milestone.

Rebuild from the repository root: `python3 integration/bob/connector-doctor-0.2.0-public-draft.1/build-candidate.py OUTPUT_DIRECTORY`. The builder refuses an RC1 base hash mismatch. Run `python3 integration/bob/connector-doctor-0.2.0-public-draft.1/test_integration.py`.

MIT applies to this supplement's original code and text. Preserve the included RC1 notices. Rollback: stop using this optional text and return to the original RC1; no account or file deletion is required.
