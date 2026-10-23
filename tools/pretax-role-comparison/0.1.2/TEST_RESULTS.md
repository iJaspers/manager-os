# Test evidence for wit.pretax-role-comparison@0.1.2

Date: 2026-10-22. Synthetic fixtures only.

12 named Node engine checks passed: the 10 original checks plus 2 overflow/recovery regressions. Node VM only, not browser rendering.

Stress failures motivated this new version; earlier passing suites were incomplete, not a comprehensive correctness guarantee. Local isolated tests and a separate bounded stress campaign do not establish standalone browser/device/mobile acceptance, simultaneous traffic, production capacity, outsider adoption or an independent security audit. Source and runtime limitations remain in README.md. Prior pickup/return-patch checks and the internal documentation PR remain historical evidence.

Four additional actual-handler checks passed using DOM stubs: repeated output is stable, invalid inputs replace stale results, valid retries recover, and overflow displays an explicit range error without Infinity. Run `node test_handlers.js`. These are not rendered-browser checks.
