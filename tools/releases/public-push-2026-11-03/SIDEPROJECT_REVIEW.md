# SideProject integration — bounded public WIP, 2026-11-03

This continues the existing public release and Product ownership. It adds no tool identity, master tracker, service or orchestrator. October framework/tools remain historical releases; the newer November 1 RC1 is main at `6fc0c50a5c93a6eefc66b60418d78541e98171bc`. November 3 source and discovery changes are public on PR #10 at `edbb5e79a1c18dec8f31d2afce81acb8ae48ef71` and `c322916e4f7495c31c16c2e4722a266d67c7b872`, not merged or product accepted. This supplement preserves all those releases.

## Publication scope and review

Current maintainer instructions authorize safe, generic, licensed public WIP on the existing review branch. No automatic merge, stable acceptance, deployment, permission change or subscription is authorized here.

| Exact scope | License / privacy decision | Claim |
| --- | --- | --- |
| `tools/connector-doctor/0.2.1-public-draft.1/` and matching ZIP | Existing MIT copyright retained; original WIT additions; synthetic fixtures only; complete selected contents reviewed | Successor to 0.2.0, local tests and disposable filesystem adapter only |
| This release directory: preflight, tests, builder changes and SideProject receipts | Scoped MIT original WIT utilities; public source links and synthetic evidence; no private authority documents or identifiers | Release guardrails, not a security certification |
| Existing `tools/CATALOGUE.json` and `tools/README.md` entries | Same Connector Doctor identity; only verified commit-pinned public download promoted | WIP, `public_ready:false`; old versions remain |

The exact file manifest and hashes are in `SIDEPROJECT_FILES.json`. This is the consolidated scope under the maintainer's existing publication authority, not a request for broader permissions. Source-risk flags in test harnesses were reviewed: fixed Node subprocesses, synthetic dynamic-code strings, and ordinary local file operations; none execute candidate third-party code. The profile store writes only explicit user-selected local preferences, never global AI configuration. The bounded scanner has one exact fictional key sentinel; adjacent real-looking assignments still fail its negative test. No broad file exemptions.

## Candidate decisions

Pinned commits, license-file hashes and available dependency-license metadata are in [SIDEPROJECT_SOURCES.json](SIDEPROJECT_SOURCES.json). Public source and relevant manifests were inspected in quarantine; none were installed or executed. License labels in lockfiles do not clear all transitive rights. No candidate dependency or asset is redistributed.

| Candidate | Useful capability and WIT equivalent | License / dependencies / risk | Decision, cost and measurable result |
| --- | --- | --- | --- |
| [Caliber ai-setup](https://github.com/caliber-ai-org/ai-setup) 1.55.2 | Deterministic configuration comparison, manual-edit protection, backup. WIT has host checks and SAVE; lacked a bounded preferences helper | Root MIT (Caliber AI); preserve copyright/license if copying. Node SDK/auth/telemetry dependencies and global/provider configuration increase scope. Reviewed `src/sync/reconcile.ts`, `src/writers/backup.ts`, manifests | **ADAPT / BUILD OUR OWN**: original metadata-only WIT implementation; small, zero dependency. 47 added tests prove conflict, consent, rollback and cross-context behavior |
| [skill-file-security](https://github.com/Netxeo/skill-file-security) 1.3.1 | Security review instructions. WIT already has release privacy/rights gates, but builder lacked automated failure checks | Package declares MIT, but no license file found in pinned tree. Installer writes agent rules; inquirer dependency. A prompt is not a scanner or audit | **BUILD OUR OWN** guardrails; **HOLD** vendoring pending a verifiable license grant. Small; 39 positive/negative release tests |
| [Wayflow](https://github.com/TahaSh/wayflow) 0.3.0 | Handler suspension, checkpoints and graph drift. Existing Bob/read adapter and recovery already own execution and authorization | MIT, Taha Shashtari; workspace agent/core dependencies. Runtime fingerprint excludes node configuration; exact action parameters still need host binding. Session store default is memory, resume deletes checkpoint before running. Reviewed runtime, sessions, tool definitions and manifests | **HOLD adapter / ALREADY COVERED execution**. Medium/high integration cost, no demonstrated authorization benefit. Isolation probe failed before execution: network namespace setup was not permitted. No sandbox execution or compatibility result claimed |
| [Cursiva](https://github.com/Heishigan/Cursiva) | Separate source-based review of generated claims, in a **job-application/CV pipeline**, not a general factual verification engine. WIT already checks receipts and regression outputs | Root MIT; FastAPI/LangGraph/OpenAI, Clerk, PDF/LaTeX/template stack. Dependency/template rights not fully cleared. Reviewed `backend/core/agent.py`, requirements and frontend manifest | **ADAPT review principle**, no runtime reuse. Independent expected hashes, actual readback and actionable rule/line findings added. No AI review score presented as proof; independent human acceptance pending |
| [Seeder](https://github.com/danielsyauqi/Seeder) 2.1.1 | Before/after activity history and blockers. Existing Product task, source inventory and catalogue already own WIT progress | MIT Daniel Syauqi and Thaqif Rosdi; NOTICE and trademark restrictions must remain if reused. Next/Drizzle/Auth/Cloudflare stack would add a project store. Reviewed activity diff code and manifests | **ALREADY COVERED**. No second PM installation. Existing task/inventory and release receipts receive verified outcomes, changes and blockers |
| [agent-knowledge-system](https://github.com/sidhanthapoddar99/agent-knowledge-system) | Persistent linked knowledge. Existing source identities/owner records and recovery already serve this role | Root MIT; archived/deprecated exact repository, Bun/Rust and bundled vendor assets require further per-file review | **REJECT adoption of archived engine**. High migration cost; no RC1 benefit. Do not silently substitute its successor repository |
| [Reddibee](https://reddibee.com) | Source-linked demand signals and approval before posting. Existing research records can retain links | Commercial service; public product page is not source licensing or API authorization. Account/provider access, personal thread data and paid features would add scope | **HOLD service integration**. No signup, scrape, posting, monitoring or spending. No measured demand result claimed |
| [side-project-census](https://github.com/siropkin/side-project-census) | Linkable aggregate discovery and static charts. WIT can already record candidate evidence | No license file found; repository includes copied thread data and browser-session collection scripts. Reviewed `sp_collect3.sh`, build/analyze files and repository metadata | **HOLD source/data reuse; REJECT collection script** for this sprint. No reuse of authors, posts or browser credentials; original aggregate discovery can wait for a permitted data source |
| [Shire](https://github.com/victor36max/shire) | Persistent agents and team activity. Bob and current owner/task records already cover coordination | MIT Victor Chan; Bun, several AI SDKs, DB/UI stack; prepare script changes git hook configuration. Reviewed agent manager and manifests | **REJECT installation / ALREADY COVERED**. A second orchestrator conflicts with scope; high dependency and permissions cost |
| [Gitleaks](https://github.com/gitleaks/gitleaks) | Secret detection including history; complements bounded WIT patterns | Core MIT; action licensing is separate. Binary absent | **HOLD execution: not installed**. No download or arbitrary install. No clean-history claim |
| [OSV-Scanner](https://github.com/google/osv-scanner) | Vulnerability and dependency/license metadata checks | Apache-2.0; database/network/cache needed; binary and cache absent | **HOLD execution: unavailable**. The new package adds no external dependencies; this is not a vulnerability clearance |
| [CodeQL](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/codeql-cli) | Semantic code analysis | Separate CodeQL terms and query licenses; public repository eligibility does not mean it ran. CLI absent | **HOLD execution: unavailable**. Existing CI/security policy unchanged; no auto-enablement |

## Release preflight use

```sh
python tools/releases/public-push-2026-11-03/preflight.py --root . --manifest tools/releases/public-push-2026-11-03/SIDEPROJECT_FILES.json
python -m unittest discover -s tools/releases/public-push-2026-11-03 -p 'test_preflight.py'
python tools/releases/public-push-2026-11-03/build-packages.py
```

The existing builder now stops before creating any ZIP when selected source fails the bounded checks. ZIP scanning never extracts or executes members. It rejects path traversal, case collisions, symlinks, extra fields/comments, suspicious compression, excessive depth/size, missing license files and mismatching member hashes. New runtime dependencies/lifecycle scripts require review. UTF-8 text is screened for several secret/private-reference patterns; findings contain paths/rules/line numbers, not matched values. Nontext assets require a separate reviewed path. All three external scanners report `NOT_RUN` truthfully.

This checks the selected public change, not private originals or the entire historical repository. Exact hashes bind reviewed bytes; hashes alone do not prove safety, ownership or authenticity. Source-risk flags need human inspection. Pattern checks can miss personal records or secrets, so complete-content review remains required. MIT detection is not an exhaustive legal judgment.

## November 6 acceptance (not executed here)

| Case, separately in a fresh ChatGPT and Gemini session | Expected evidence |
| --- | --- |
| Follow the existing one-link RC1 installation; ask for a fictional packing checklist | Ordinary chat works without code execution or account setup; actual host/version and trace recorded |
| Ask Bob which tools this session exposes | Only host-native callable tools reported; absent tools stay unverified/unsupported; another host's observations rejected |
| Read one authorized synthetic artifact | Exact target and current authorization checked, observed output retained; no automatic retry after failure |
| Deny the read, change account or target, expire approval | Requested operation stops; no alternate-route bypass or inherited credentials |
| SAVE, close session, recover through the existing owner record | Exact artifact/version/hash recovered; handoff carries no approval; missing/ambiguous source holds |
| Transfer preferences and compare capability drift | Only three allowlisted preferences travel; manual drift conflicts; local backup/readback/rollback verified where code is supported |
| Host has no code runner or connector | Conversational help remains available for permitted work; no claim that the CLI ran |
| Separate synthetic users/workspaces | No shared authority or cross-user retrieval; local tests do not establish provider tenant isolation |

Working local tests do not establish cross-AI compatibility, browser/mobile acceptance or independent security acceptance. November 6 remains the acceptance milestone.

Rollback: select the preserved 0.2.0 package and unchanged RC1; stop optional portability use. Local profile rollback requires the recorded next revision and explicit consent. Revert this sprint's source/catalogue commits through review after checking dependents. Preserve history, old downloads and private originals. No website or user installation was updated.
