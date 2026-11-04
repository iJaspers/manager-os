# Bob verification supplement 0.1.0-public-draft.1

Optional maintainer test tools for the existing Bob/RC1 and Connector Doctor 0.2.1. This is public WIP source, not a new Bob, connector engine, skill installer or production acceptance. No third-party code or runtime is bundled. Existing directory-specific licenses still apply.

**Everyday users:** open the [current WIT Starter reference](https://www.ijaspers.com/post/witburrow-starter-reference) and follow its Bob instructions in your current AI. If that host lacks a tool, continue conversationally. This supplement does not change the frozen RC1 install or require a new service.

**Power/Super users and maintainers:** use a checkout of the existing repository's `release/wit-public-2026-11-03` review branch. Run commands from the repository root. Tested with Node 24.22.1 on Linux; other operating systems and Node versions are unverified. The base tests need only Node:

```sh
node --test integration/bob/verification-0.1.0-public-draft.1/*.test.mjs
```

Keep the repository layout: these files import the existing Doctor rather than shipping another copy. Use the commit-pinned source linked from the release receipt for repeatability. Removing this optional directory restores the prior test setup; no host configuration, account permissions or RC1 files are modified.

## Available checks

| Check | Actual behavior | Evidence boundary |
| --- | --- | --- |
| Promptfoo 0.125.1 | Runs 20 fixed cases through the existing Doctor via a local JavaScript provider; positive run and deliberate failing assertion | Synthetic host contracts, not ChatGPT/Gemini model evaluations or a red-team certification |
| MCP Inspector 2.13.0 | Real stdio `tools/list` and `tools/call` through the existing read-only adapter, with consent, denial and failure checks | Only the bundled inert fictional-checklist fixture; no real external connector tested |
| SkillSpector 2.12.0 report review | Checks bounded report/source hashes, external sandbox receipt, complete coverage and findings before human review | Scanner was not run here; no automatic installation; caller receipts are not authenticated |
| Playwright 1.62.1 | Fetches the fixed public RC1 page and Bob file, checks exact link presence and frozen checksum; optional static rendered-link check | HTTP checks work. Rendered check and native AI account journey were not run successfully |
| First useful result | Computes local elapsed time only after capability review and confirmation of the supplied artifact hash; checks save/resume consistency | No telemetry or storage; human-entered events are not independently authenticated |

### Optional external test tools

Provide an already reviewed, exact-version local CLI/package. The wrappers do **not** download or install dependencies. Do not point them at unfamiliar code, private connector configurations or a real account. Review the [dependency record](../../../tools/releases/public-push-2026-11-03/REDDIT_DEPENDENCY_REVIEW.json) before reproducing the optional environment. Its license metadata is not complete transitive rights or vulnerability clearance; the tested runtime bundle is not offered for redistribution.

These placeholders mean paths to your reviewed tools; output directories must be new. Both absolute and relative paths are supported. Raw Promptfoo output can contain local paths: keep it private and share only the deliberately reduced `receipt.json` after inspection.

```sh
node integration/bob/verification-0.1.0-public-draft.1/run-promptfoo.mjs /reviewed/promptfoo/dist/src/entrypoint.js ./wit-promptfoo-positive
node integration/bob/verification-0.1.0-public-draft.1/run-promptfoo.mjs /reviewed/promptfoo/dist/src/entrypoint.js ./wit-promptfoo-negative --negative-control
node integration/bob/verification-0.1.0-public-draft.1/run-inspector.mjs /reviewed/inspector/clients/cli/build/index.js ./wit-inspector-evidence
node integration/bob/verification-0.1.0-public-draft.1/run-web-check.mjs /reviewed/playwright ./wit-web-evidence
```

Add `--browser` to the web command only when reviewed Chromium is available and its sandbox works. A missing browser gives `NOT_RUN` and a nonzero exit, not a pass. Even that check renders an inert HTTP snapshot, blocks network requests and disables site scripts; it does not replace a real user's Wix-to-AI trial. Existing HTTPS proxy configuration is respected. No TLS bypass or sandbox-disable option is provided.

Promptfoo receives a fixed local provider/config, isolated state and no model credentials; telemetry/update/remote-generation options are disabled. Inspector receives a minimal environment, memory-only secret store, fixed fixture command and no arbitrary server/config URL. These are scope restrictions, **not OS-level network isolation**. Changing the trusted executable or these fixed configurations requires a new review.

### Measure a first useful result locally

```sh
node integration/bob/verification-0.1.0-public-draft.1/measure-onboarding.mjs integration/bob/verification-0.1.0-public-draft.1/onboarding.example.json integration/bob/verification-0.1.0-public-draft.1/first-result.example.txt
```

The example returns `SYNTHETIC_ONLY`, 500 ms, and consistent save/resume flags. **500 ms is fictional test data, not measured user performance.** For an observed trial, retain a private copy of the four-field event structure, set the host and evidence kind honestly, and enter elapsed monotonic times. Confirm that the produced artifact is useful before `result_confirmed`; hashing arbitrary output is insufficient. No names, account IDs, prompts, chat text or tokens belong in the event record. Keep private artifacts and their hashes private. Actual user isolation, tool permissions and durable save/resume still require the existing November 6 acceptance process.

### Review an externally sandboxed SkillSpector report

```sh
node integration/bob/verification-0.1.0-public-draft.1/review-skill.mjs ./report.json ./sandbox-receipt.json ./reviewed-specimen
```

This reads existing evidence only. It does not execute SkillSpector or the specimen. Maximum sizes: report 1 MiB, receipt 64 KiB, specimen 2 MiB. Final symlinks, directories, malformed input and hash mismatches fail closed. The receipt fields are `scanner: "NVIDIA/SkillSpector"`, `version: "2.12.0"`, `execution: "completed"`, `isolation: "external_sandbox_no_network"`, `llm_used: false`, `exit_code: 0`, plus lowercase SHA-256 strings `report_sha256` and `artifact_sha256`. The sandbox operator must establish that the report covers exactly that specimen; this helper cannot authenticate that statement.

Require an independently configured disposable sandbox with no credentials, private mounts or network. `--no-llm` alone is insufficient because SkillSpector can still perform OSV lookups. Inspect actual full results, exclusions, dependencies and licensing; do not rely on an AI score or exit code. `READY_FOR_HUMAN_REVIEW` always has `can_install: false`. A `HOLD` requires resolving the stated evidence problem; it is never permission to install.

## November 6 and rollback

Continue the existing acceptance kit and Product owner records. In fresh ChatGPT and Gemini sessions, use the current one-link entry, verify actual host tools, perform one permitted fictional task, deny another, save/resume through that host's real mechanism, and independently inspect the retained output. Use these contract cases and local timing helper as supporting evidence. Never copy tool availability, approval, account access or a success claim from another host. A conversation-only host can pass a truthful fallback case while tool execution remains unsupported.

No fresh native-host acceptance, dynamic/rendered website acceptance, independent security audit, vulnerability scan or Windows compatibility is claimed here. See [release review and exact results](../../../tools/releases/public-push-2026-11-03/REDDIT_INTEGRATION_REVIEW.md). To roll back, stop these optional commands and retain their local evidence; revert this supplement's reviewed commits if needed. Keep prior release history and frozen RC1 intact.
