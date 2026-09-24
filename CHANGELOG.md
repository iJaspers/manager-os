# Changelog

All notable public Manager OS changes are recorded here. The authoritative machine-readable release state remains `RELEASE_MANIFEST.json`.

## MOS-2026.09.24.1

Released: 2026-09-24  
Channel: stable  
Generation: v3  
Package: v2026.09.24-CG1

### Added

- Human-readable capability guide explaining what MOS adds beyond a normal AI chat.
- Privacy-scrubbed PDF handbook and TXT starter pack in the public repository.
- Twenty public capability areas covering intake, planning, projects, research, writing, coordination, tools, automation, decisions, memory, monitoring, data, documents, safety, maintenance, recovery, and improvement.
- HOT/WARM/COLD/ARCHIVE context layers for smaller working sets and more efficient retrieval.
- Clever Girl Protocol for bounded weekly update, patch, security, and obsolete-workaround scouting.
- Portable voice/email bridge guidance with authentication, bounded commands, idempotency, approval gates, and receipts.

### Changed

- Public download pointers now identify package build v2026.09.24-CG1.
- Public documentation more clearly distinguishes host-native capabilities from MOS governance.
- Workarounds must be reviewed for removal when a host patch supplies a safer native feature.

### Security

- Clever Girl performs discovery and recommendation only; it cannot auto-install behavior changes.
- The public pack excludes personal, customer, financial, health, credential, site, and security-sensitive operator data.
- External input remains untrusted and human approval remains mandatory for promotion.

## MOS-2026.09.21.1

Released: 2026-09-21  
Channel: stable  
Generation: v3

### Added

- Public stable release manifest and human-approval update policy.
- Privacy-preserving weekly update-check path at `https://www.ijaspers.com/mos/check`.
- Explicit observability rules separating update-check requests, download requests, clicks, visitors/sessions, and crawler traffic.
- Public security policy and contribution policy.
- The Airlock trust-boundary model for untrusted community material.
- Documented update discovery and verification flow with rollback/replay/source-mismatch checks.
- Source-specific distribution routes for Reddit communities, GitHub, LinkedIn, and Hacker News.

### Security

- External submissions remain untrusted by default.
- Public contribution intake remains CLOSED.
- Security-sensitive reports must not be posted as public GitHub Issues.
- Behavior-changing updates require explicit local human approval before adoption.

### Observability clarification - 2026-09-22

- Wix page/referrer analytics and MOS landing-page button interactions are verified live.
- Direct route-level request counting for `/mos/check` and `/mos/download/*` is not yet verified as persisted telemetry.
- Redirect hits are not labeled as update checks, downloads, users, or installations.
