# Provenance — WIT Scout + Explain

**Public tool ID:** `wit.scout-explain`  
**Version:** `0.1.0-public-draft.1`

## Public lineage

This preview continues the existing WIT Scout + Explain experiment in the public iJaspers/manager-os repository:

- Public research PR: https://github.com/iJaspers/manager-os/pull/14
- Immutable earlier source: https://github.com/iJaspers/manager-os/tree/782295c036df49c679864bb0aaae0e55ecf87933/experiments/wit-scout-explain

The pinned public revision is a lineage reference, not a claim that every byte in this version is identical to it. The owner authorized the subsequent refinements and preparation of this standalone preview.

Those refinements include current MCP structured-response handling and rejection of conflicting payload locations; full research-session checkpoint save/restore; retention of matched passages and their qualifiers; and synthetic acquisition/restart regression checks. They do not add an autonomous search service or independent semantic reviewer.

## Selected scope

This version retains 25 Python/JavaScript runtime and test files from the existing Scout implementation. Source selection and independent preflight review found standard-library or sibling-module imports in Python, and built-in test/runtime facilities in JavaScript. No external runtime package or copied third-party implementation was identified in that selected scope. Source code was inspected before the offline tests recorded in TEST_RESULTS.md.

README.md, LICENSE_NOTICE.md, this provenance record, TEST_RESULTS.md and example_results.json were prepared specifically for this preview. The standalone JSON example uses fictional opportunities and reserved example.org URLs. Historic working notes, captured connector returns, generated checkpoints, recipient-specific delivery material and unrelated components are not part of this package.

No whole-repository or unrelated collection licence is inferred. LICENSE_NOTICE.md states the rights position for this source-visible preview.

## Referenced public material

Existing tests use synthetic source bodies, fabricated commit strings and stub connector responses. Some fixtures retain public repository URLs as identifiers; test success does not establish a live read of those URLs.

The specialized recovery harness and its fixtures retain short documentation passages attributed in the source to these public projects:

- https://github.com/Neeeophytee/awesome-ai-workflows
- https://github.com/oxylabs/web-api-mcp

Other fixtures refer to the public WIT repository and a public Reddit discussion. These are evidence/behavior examples, not vendored engines, live credentials, provider access grants or endorsements. Original external material remains governed by its own applicable terms.

## Verification boundary

Fresh offline results belong to this exact candidate, not to an earlier checkpoint or another host. Checksums recorded by the final release packaging can identify bytes; they cannot establish authorship, signed provenance, factual truth or user acceptance. Deployment, live-host connectivity and physical-device behavior require separate evidence.
