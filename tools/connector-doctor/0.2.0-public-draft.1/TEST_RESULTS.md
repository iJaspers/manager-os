# Local execution evidence — 2026-11-03

`node --test tools/connector-doctor/0.2.0-public-draft.1/*.test.mjs`: **82 passed, 0 failed, 0 skipped**, Node 24.22.1.

Covers positive reads; five connection states; missing/denied tools; stale, copied and cross-AI observations; exact tool/action schema; credentials-key rejection; drafts; expired, changed-target and used approvals; failures, wrong receipts and readbacks; read-only adapter invocation and revocation; disposable actual filesystem read; bounded CLI bytes and malformed UTF-8. Synthetic data only.

`python3 integration/bob/connector-doctor-0.2.0-public-draft.1/test_integration.py`: **6 passed**, Python 3.12.14. Covers exact RC1 restoration, deterministic ZIP, member hashes/license, changed-base refusal, all five frozen RC1 member hashes and private-reference scan.

Not run: live provider OAuth/writes, fresh ChatGPT/Gemini chat trials, Android, visual/device acceptance, external independent security/product acceptance. These local checks are not those acceptance milestones. Original private 0.1.0 baseline had 22 passing tests in prior recovery; no new execution of that obsolete baseline is claimed here.
