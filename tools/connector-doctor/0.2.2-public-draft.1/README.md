# Connector Doctor 0.2.2-public-draft.1

Optional WIP for Bob: diagnose real tool support, distinguish setup from permission, and check actual results. Original Node helper and a narrow read-only adapter; no account, dependency install, service, subscription or scheduler.

0.2.2 repairs the read adapter's authorization binding: capture intent before callbacks, freeze copied request/observation data, reject extra action fields, pin callbacks and stop changed requests or expired local check windows. The host still enforces current permissions at invocation. Use this successor for new trials; 0.2.0/0.2.1 remain historical and their read adapter should not be used for new authorization-sensitive work.

For Everyday use, attach the [optional Bob text](../../../integration/bob/connector-doctor-0.2.0-public-draft.1/BOB_WITH_CONNECTOR_DOCTOR_0.2.0-public-draft.1.txt) to your existing WIT chat. Say: **Bob, check which tools this chat actually supports, then make a fictional packing checklist. Keep it here if no connection is needed.** Loading this text cannot add apps or credentials. The supplement keeps Bob's existing SAVE and ordinary-chat workflow.

For Power/Super use, download this version's ZIP, extract it and run:

```sh
node doctor-cli.mjs example.json
node --test *.test.mjs
```

Node 18+ API target; tested on Node 24.22.1. No npm install. The fictional example returns READY_TO_REQUEST, with can_execute:false and executed:false. It checks supplied observations; it does not discover your actual accounts by itself. An AI with no code tool can follow the optional instructions conversationally.

AVAILABLE means the current host offers setup; INSTALLED still needs current callable-tool and authentication evidence; UNVERIFIED means missing/stale evidence; DENIED stops the operation; UNSUPPORTED means evidence says this host or exact tool lacks that action. Use only the setup method exposed by the host. Do not treat denial as an invitation to reconnect or switch accounts.

## Host adapter

Import `evaluate`, `requestHash`, and `verifyResult` from `connector-doctor.mjs`. Every observation must bind host, session, account and exact tool/action schema. See `example.json`. The five-minute evidence window is a conservative local policy, not a vendor guarantee.

`runReadOnly(request, host)` in `host-read.mjs` requires four trusted functions: `now()`, `observe(request)`, `authorize(request)`, `invoke(request)`. It discards supplied observations, rechecks after authorization, calls once, and verifies receipt consistency. The disposable-filesystem test demonstrates a complete adapter. The host must allowlist exact tools and arguments; an arbitrary shell/API is never globally read-only.

Writes and provider-side drafts are advisory evaluation only. Bind all recipients, timing, attachments and other parameters in the exact payload. Valid local hashes or approval IDs are not permission tokens. The host owns authentication, approval, durable attempt history and revocation. Never put credentials in requests or resume cards. The key-name screen is not a complete secret detector.

`verifyResult(request, receipt)` requires an eligible request, bound invocation, matching target and observed result. Mutations require a matching post-action readback. A matching forged receipt is still forged; the host must supply trustworthy evidence. Failed or unknown outcomes never trigger retries. `node doctor-cli.mjs result.json --verify` accepts `{request,receipt}`. CLI input is limited to 65,536 UTF-8 bytes before decoding/parsing; invalid input emits a generic error without reflecting contents.

## Portable preferences and resume (new in 0.2.1)

Everyday users can stay in the same RC1 chat and say: **Bob, save where we stopped. In my next chat, check its tools again before continuing.** The existing SAVE/owner-record workflow remains authoritative. No installation or global configuration change is required for ordinary conversation.

Power users can run the complete synthetic demonstration in a new disposable directory:

```sh
node demo.mjs ./demo-output
```

It creates a fictional checklist, a metadata-only handoff, local preferences, a backup and `receipt.json`. It uses the existing read adapter, verifies the observed file hash, and restores the original preferences. It refuses an existing output directory. It never calls an external AI or provider.

For your own **private, trusted local workspace** (create the directory first):

```sh
node portable-cli.mjs init ./my-workspace preferences.example.json
node portable-cli.mjs plan ./my-workspace preferences.example.json > plan.json
# Review plan.json. Change only language/detail/mode in a separate desired file.
node portable-cli.mjs apply ./my-workspace plan.json --consent
```

The plan contains exact before/after values and revisions. A changed profile causes `DRIFT_CONFLICT`; missing consent refuses the write. A changed plan must be reviewed again. An unchanged plan creates no backup. Successful changes retain one previous version in `wit-preferences.previous.json`, then read back the actual file. Roll back using the exact `next_revision` from the applied plan:

```sh
node portable-cli.mjs rollback ./my-workspace <next_revision> --consent
```

Only language (`en`, `fr`, `es`), detail (`brief`, `normal`, `detailed`) and mode (`everyday`, `power`, `super`) travel. These are WIT preferences, not elevated privileges. No MCP files, provider configuration, credentials, paths, approvals or account settings are synchronized. This is a local helper, not automatic cross-device sync.

```sh
node portable-cli.mjs handoff handoff.example.json
node portable-cli.mjs resume-check handoff.example.json example.json
node portable-cli.mjs drift example.json example.json handoff.example.json
```

Handoffs allow a tool/version/step and artifact digest, plus required **read** capabilities. Unknown fields and mutation actions are rejected. The example digest is deliberately all zeros: it proves no completed work. Recover the real artifact through the existing owner record and compare its digest. Then ask the current host for fresh tools and authorization for the exact task. Supplied observations and hashes are not authenticated evidence. No previous account, session or permission is inherited. A denial stops the requested operation; unavailable capabilities permit ordinary conversation for allowed work.

The local store uses exclusive locks, bounded UTF-8 reads, regular files only, private file modes, atomic file replacement and one backup. It refuses symlinked workspaces/files and hardlinked profiles. It is tested on Linux in a trusted user-owned directory, **not** a tenant isolation boundary or protection against a malicious same-user process. A crash may leave a lock or backup with an unchanged profile; inspect both before manually clearing the lock. Multi-file power-loss durability, Windows behavior and automatic stale-lock recovery are not claimed.

## Test evidence

147 local Node tests passed for this version; six unchanged Bob packaging regressions are tracked in the sprint receipt. No live external provider adapter, OAuth flow, fresh Gemini/ChatGPT chat, Android device, independent security audit or product acceptance is claimed. See [test evidence](TEST_RESULTS.md) and [November 6 cases](../../../integration/bob/connector-doctor-0.2.0-public-draft.1/NOVEMBER_6_ACCEPTANCE.md).

0.2.0 tightens 0.1.0 observations with context, time and exact tool-action support. This public derivative additionally bounds CLI reads and rejects malformed UTF-8. The upstream MIT license is preserved, scoped to this directory. Public source is WIP, not a full WIT launch or automatic installation.

Rollback: stop using the optional supplement and return to the unchanged published RC1 Bob. Older versions and downloads remain intact. Revert the publication/catalogue commits through review if needed; preserve history and inspect later dependent changes first.
