# Contributing to Manager OS

## Current status

**Public contribution intake is CLOSED until the release manifest says otherwise.**

This document defines the intended intake contract before opening the door.

## What will be accepted when intake opens

Normal public submissions may cover:

- reproducible bugs;
- bounded improvements;
- compatibility findings;
- documentation corrections.

Security-sensitive findings must use the repository's private vulnerability-reporting lane only. Never place credentials, exploits against a real target, private data, or security-sensitive details in a public Issue.

## Submission rules

V1 intake is deliberately boring:

- text only;
- no file or binary attachments;
- no secrets, credentials, personal information, customer data, or private MOS canon;
- submitted URLs are treated as inert text and are not automatically fetched;
- concise reproduction steps and expected/actual behavior;
- one issue per material problem or improvement.

A submission is **untrusted input**, not code-review authority and not permission to alter MOS.

## Promotion path

`UNTRUSTED → QUARANTINE → REVIEW → CANDIDATE → REGRESSION TESTS → HUMAN APPROVAL → PROMOTION`

Popularity, AI consensus, a passing parser, or a valid GitHub identity does not make a contribution trusted.

## Local MOS contribution preparation

A contributing MOS should:

1. perform a materiality check;
2. remove private/personal/customer/credential data;
3. generate a bounded plain-text report;
4. classify it as normal or security-sensitive;
5. obtain its own local operator authority before sending anything externally.

If the manifest says intake is CLOSED, keep the report locally as **WAITING ON INTAKE**.
