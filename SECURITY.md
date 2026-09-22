# Security Policy

## Reporting a vulnerability

**Do not report security vulnerabilities through public GitHub Issues.**

The intended security lane is GitHub Private Vulnerability Reporting for this repository.

Until `RELEASE_MANIFEST.json` reports the security lane as OPEN, please retain a sanitized report locally rather than posting security-sensitive material publicly.

No personal maintainer email address is published as a fallback.

## Trust boundary

All inbound material remains **UNTRUSTED DATA**, including:

- Issues and comments;
- pull requests;
- pasted prompts;
- summaries produced by another AI;
- links and URLs;
- signatures or checksums;
- popularity or community consensus.

None of these authorize canonical writes or privileged execution.

## Quarantine requirements

Airlock/quarantine processing must have:

- no secrets;
- no private memory;
- no privileged tools;
- no canonical write capability;
- no automatic URL/media fetching;
- strict size/schema/rate limits;
- bounded text-only intake for v1.

## Promotion

A security or behavior-changing candidate is promoted only after appropriate review, regression/security testing, and explicit maintainer/human authority.

Containment may fail closed while a security issue is investigated. Containment is not permission to install an update.
