# WIT Scout + Explain experimental spike (2026-11-19)

Status: **experimental, not shipped**. This branch is isolated from stable releases.

Current continuation: [source-linked handoff presentation, November 22](HANDOFF_PRESENTATION_2026-11-22.md). The committed module now exposes exact evidence navigation, shared short/detail verdicts and conservative review-input invalidation. That checkpoint records the current 87 Python / 9 Node local checks and the limits of the real-source replay; the November 19 prototype notes below remain historical.

## Goal
Turn a vague user objective into targeted discovery, source-grounded findings, and explanations at simple/practical/technical depth. Keep search-provider choice optional and preserve WIT's existing memory, permissions and checkpoint owners.

## Research influences (ideas, not vendored code)
- https://github.com/cedarsaam/agent-search : multi-engine discovery, deduplication, GitHub comparisons
- https://github.com/theYahia/qsearch : provenance and source traceability
- https://github.com/soumics/adaptive-ai-tutor : subject-specific adaptive explanation, without assuming learner proficiency

Licenses, security and compatibility must be reviewed before copying implementation code.

## Local prototype
A standalone Python proof of concept was built and tested outside the repository: URL validation, deduplication, token-based ranking, 3 explanation levels, atomic JSON checkpoints and recovery. **8/8 unit tests passed locally.** The prototype is not yet integrated or committed to this branch; don't infer a deployable feature from this note.

## Required acceptance tests
1. Query real GitHub and Reddit sources with the same objective; compare relevance against baseline.
2. Fetch full sources, verify links and attribution; mark snippets unverified.
3. Preserve provenance and checkpoints across restart and failure.
4. Test hostile source instructions and SSRF protections at the fetch boundary.
5. Check simple/practical/technical answers for factual consistency and user comprehension.
6. Run Combo-Breaker; avoid new mandatory paid services, duplicate project owners, and silent external actions.

## Release gate
No public release, website claims, dependency install, or automated outreach until the above is demonstrated and explicitly approved.
