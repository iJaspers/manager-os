# The Airlock

The Airlock is the inbound trust boundary for Manager OS community material.

## Principle

External content may contain useful ideas and hostile instructions at the same time.

Therefore, retrieval, parsing, summarization, signatures, reputation, or AI agreement do not make external material trusted.

## Intended v1 pipeline

`UNTRUSTED → QUARANTINE → TRIAGE → CANDIDATE → TEST → HUMAN REVIEW → PROMOTION`

### UNTRUSTED

Raw public/private submission.

### QUARANTINE

Deterministic limits are applied before deeper review:

- supported schema;
- text-only payload;
- size limit;
- encoding validation;
- rate/duplicate checks;
- URLs remain inert.

Quarantine receives no secrets, private memory, privileged tools, or canonical write access.

### TRIAGE

Classify as one of:

- MALICIOUS
- INVALID
- UNSAFE
- DUPLICATE
- OUT OF SCOPE
- NO MATERIAL VALUE
- CANDIDATE

### CANDIDATE

A bounded, reviewable proposal. Candidate status is not trust.

### TEST

Reproduce using safe fixtures where possible and run applicable regression/security checks.

### HUMAN REVIEW

A human/maintainer decides whether the change should enter MOS.

### PROMOTION

Only an explicitly authorized canonical write promotes a candidate.

## Kill conditions

Inbound processing should stop/fail closed when:

- source or transport identity is uncertain;
- quarantine isolation fails;
- candidate material can reach privileged tools or canon;
- release identity/integrity becomes uncertain;
- the intake lane cannot preserve the public-normal/private-security split.
