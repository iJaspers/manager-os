# Connector Doctor 0.2.0-public-draft.1

Optional WIP for Bob: diagnose real tool support, distinguish setup from permission, and check actual results. Original Node helper and a narrow read-only adapter; no account, dependency install, service, subscription or scheduler.

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

## Evidence and limits

82 local Node tests and six Bob packaging checks passed for this public derivative. No live external provider adapter, OAuth flow, fresh Gemini/ChatGPT chat, Android device, independent security audit or product acceptance is claimed. See [test evidence](TEST_RESULTS.md) and [November 6 cases](../../../integration/bob/connector-doctor-0.2.0-public-draft.1/NOVEMBER_6_ACCEPTANCE.md).

0.2.0 tightens 0.1.0 observations with context, time and exact tool-action support. This public derivative additionally bounds CLI reads and rejects malformed UTF-8. The upstream MIT license is preserved, scoped to this directory. Public source is WIP, not a full WIT launch or automatic installation.

Rollback: stop using the optional supplement and return to the unchanged published RC1 Bob. Older versions and downloads remain intact. Revert the publication/catalogue commits through review if needed; preserve history and inspect later dependent changes first.
