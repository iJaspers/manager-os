# Local execution evidence — 2026-11-03

`node --test tools/connector-doctor/0.2.1-public-draft.1/*.test.mjs`: **129 passed, 0 failed, 0 skipped**, Node 24.22.1.

Covers positive reads; five connection states; missing/denied tools; stale, copied and cross-AI observations; exact tool/action schema; credentials-key rejection; drafts; expired, changed-target and used approvals; failures, wrong receipts and readbacks; read-only adapter invocation and revocation; disposable actual filesystem read; bounded CLI bytes and malformed UTF-8. Synthetic data only.

`python3 integration/bob/connector-doctor-0.2.0-public-draft.1/test_integration.py`: **6 passed**, Python 3.12.14. Covers exact RC1 restoration, deterministic ZIP, member hashes/license, changed-base refusal, all five frozen RC1 member hashes and private-reference scan.

Not run: live provider OAuth/writes, fresh ChatGPT/Gemini chat trials, Android, visual/device acceptance, external independent security/product acceptance. These local checks are not those acceptance milestones. Original private 0.1.0 baseline had 22 passing tests in prior recovery; no new execution of that obsolete baseline is claimed here.

47 added tests cover strict portable metadata, no inherited access, capability drift, consent, changed plans, changed local files, symlinks/hardlinks, bounded input, backup tampering, exclusive locks, fresh-process use, actual synthetic file reads and retained evidence. The demo leaves a real receipt and restores preferences.

Release preflight: 39 Python tests pass. The first archive round-trip test exposed an archive member basename defect, repaired before publication. Preflight also caught a known fictional key sentinel and missing CJS support; the exact sentinel exception has two regression checks and no file exemption.

See the existing release directory SIDEPROJECT_REVIEW.md for candidate decisions, scope, limitations and current November 6 cases. All third-party runtime evaluation and external security scanners are NOT RUN; sandbox namespace creation was unavailable and scanners were not installed.
