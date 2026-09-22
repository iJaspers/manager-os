# Changelog

All notable public Manager OS changes are recorded here. The authoritative machine-readable release state remains `RELEASE_MANIFEST.json`.

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

### Security

- External submissions remain untrusted by default.
- Public contribution intake remains CLOSED until the release manifest says otherwise.
- Security-sensitive reports must not be posted as public GitHub Issues.
- Behavior-changing updates require explicit local human approval before adoption.

### Notes

This release establishes the public release/update/security plumbing. Automatic discovery is allowed; automatic behavior-changing installation is not.
