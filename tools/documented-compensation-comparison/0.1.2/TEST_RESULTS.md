# Test evidence for wit.documented-compensation-comparison@0.1.2

Date: 2026-10-22. Synthetic fixtures only.

34 executable checks passed: 13 built-in, 8 existing unittest checks and 13 new admission-boundary checks. They cover exact/over 8 MiB, 10,000/10,001 offers, depth64/65, duplicate keys, invalid UTF-8, escaped braces and text limits. Synthetic Python CLI/engine checks only.

Stress failures motivated this new version; earlier passing suites were incomplete, not a comprehensive correctness guarantee. Local isolated tests and a separate bounded stress campaign do not establish standalone browser/device/mobile acceptance, simultaneous traffic, production capacity, outsider adoption or an independent security audit. Source and runtime limitations remain in README.md. Prior pickup/return-patch checks and the internal documentation PR remain historical evidence.

Five CLI retry checks passed using `python3 check_retry.py`: repeated output bytes are identical, input bytes stay unchanged, malformed input has repeatable INVALID_INPUT output, correction restores the result, and no extra files are created in the input directory. This harness has a 12-second subprocess timeout, not a cross-device capacity promise or persistent queue.
