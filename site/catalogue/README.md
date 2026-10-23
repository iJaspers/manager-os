# Self-managing public catalogue presentation

The fixed Wix renderer reads tools/CATALOGUE.json on each page visit. Approved metadata changes update cards, availability filters, continuation entries and opt-in contribution credit without another website-update prompt. Open tabs do not refresh themselves. This is request-time rendering, not an always-on approval bot or a usage tracker.

The canonical management extension contains version-scoped review records and immutable contribution events. The six seed records point to the existing exact-commit PROVENANCE.json and TEST_RESULTS.md evidence and preserve prior publication decisions. Their source_commit is the release provenance baseline, not a self-hash of this catalogue. A new self-declared provenance file is NOT authority for a new tool or version. Maintainers must record a reviewed privacy/licence/authority decision under the existing contribution policy; no automatic PR execution or merge is enabled. Source previews and WIPs are not production-ready certifications.

Five private candidates remain metadata-only with no download. WIPs stay publicly_available:true and public_ready:false. Directory-scoped MIT licences apply only to those exact tool releases, not unrelated contents.

Accepted review evidence types: canonical repository PR/commit URLs, or a pinned same-release PROVENANCE.json/PROVENANCE.md/TEST_RESULTS.md recording the existing review decision. All URL spellings are canonical; source and provenance paths must share the exact release directory and commit. Future review changes require maintainer assessment, not merely a passing parser.

Contribution events require exact tool/version, immutable event ID, opt-in public identity, review/evidence links and explicit reviewed status. Accepted contributions and pickups remain separate; duplicates cannot inflate credit. The board is alphabetical and unranked. Usage, popularity and quality rankings remain unknown. No current public contribution credits are seeded. Older-version events are held in this v1 until reviewed release-history support exists.

Malformed, duplicate-key, oversized, over-nested or inconsistent metadata is held. URL hosts are allowlisted; remote data is never executable. Reads use a 10-second timeout, at most three bounded retries and a streaming 2 MiB limit. Private/unknown fields are not projected. After fetch/integrity failure, the native Wix page stays visible with a clear stale-snapshot notice. Version control and review references provide the audit trail; no visitor telemetry or durable server error log is added.

Tests: node --test site/catalogue/tests/*.test.mjs

50 Node tests passed during preparation, including actual six-release metadata migration, WIP/not-ready preservation, private-card retention, source pinning, URL aliases, duplicate events/JSON keys, size/nesting bounds, retries and text-only DOM output. These are not live Wix/browser acceptance. Generated fixed embeds are saved under deployment for review; their deployment status must be verified separately. No workflows, write credentials, new services or paid infrastructure are introduced.

Rollback: restore the previously saved Wix embeds and/or revert a reviewed metadata commit. Do not delete immutable source or package history. Preserve the existing upstream contribution allowlist and human review gates.
