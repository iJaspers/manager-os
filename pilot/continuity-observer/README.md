# Witburrow Continuity Observer 0.1 (optional pilot)

**Status: EXPERIMENTAL PUBLIC SOURCE PREVIEW / NOT A STABLE WIT RELEASE.** Original, dependency-free Python tooling for comparing *recorded structured answers* against fictional decision/authority scenarios. It is not a new WIT agent, memory engine, source synchronizer, host extension, scheduler, or stable-tool installation.

## What it adds beyond the existing WIT test-plan forge

WIT's current plan-forge generates proposed regression scenarios. This separate, optional observer **scores structured response records** against a hidden golden set and reports specific mismatched fields. It closes a narrow testing gap without duplicating the plan generator, touching a canonical record, copying proprietary software, or executing instructions from third-party content.

The 10 **fictional** cases cover: current-versus-archived decisions, no duplicate completed work, prompt-injection authority boundaries, zero-spend decisions, missing primary evidence, unsupported cross-AI sync, project isolation, release gates, draft-versus-sent honesty, and uncertain write readback. Every case uses invented records and identifiers.

## Adversarial review and limits

A separate local Grey Goo-style attack suite (`test_grey_goo.py`) now adds 16 negative tests for forged authority, fake source citations, unauthorized action claims, answer-key leakage, input parsing, and incomplete comparisons. These are deterministic checks of the scorer, **not a native Grey Goo Shadow Analyst review** or independent, fresh-host model acceptance. See `GREY_GOO_LOCAL_REVIEW_2026-11-12.md` for exact results and hold conditions.

The code is publicly inspectable as a **work-in-progress source preview**. It is not automatically installed or adopted by existing WIT users, and nobody should rely on its output as proof of safety, memory, confidentiality, source retrieval or tool execution.

## Run entirely offline (Python 3, standard library only)

From this directory:

```sh
python observer.py prompts --cases cases.json > prompts_only.json
python observer.py score --cases cases.json --observations synthetic_pass.json
python observer.py score --cases cases.json --observations synthetic_fail.json
python observer.py compare --cases cases.json --baseline synthetic_pass.json --candidate synthetic_fail.json
python -m unittest discover -s . -p 'test_*.py' -v
```

- `prompts` omits the golden-set expectations. **Send only each generated `context` and `question`, together with `response_contract`, to the test AI.** Never provide `cases.json` or the synthetic answer files to the system being evaluated.
- In an **independent, fresh session**, ask that AI to return exactly one JSON response per case with `status`, `decision_id`, `next_action_id`, `source_ids`, `claimed_actions`.
- Manually collect actual responses into a *new local file* matching `synthetic_pass.json`'s schema. Do not overwrite the shipped fictional samples. Keep any real or sensitive source material outside this public pilot.
- `score` requires `--observations FILE`; it checks exact status/decision/action IDs, the *claimed* source IDs, and claimed external effects. It prints a limited JSON summary without input text.
- `compare` accepts **two recordings for the same case set** (`--baseline` and `--candidate`), labels each case as IMPROVEMENT, REGRESSION, UNCHANGED_MATCH, UNCHANGED_MISMATCH, or INCOMPLETE, and does not mislabel an unobserved case as progress. This only compares recorded fields, not genuine host behavior. A green CLI result requires a complete candidate with no remaining mismatches. A partial baseline returns `3`, even if the candidate matches all fields.
- Return codes: `0` complete field match, `1` one or more candidate field mismatches, `2` invalid input, `3` incomplete comparison or unrun cases without a mismatch. Use the JSON report rather than the exit code to distinguish changes and baseline/candidate coverage.
- The bundled `synthetic_pass.json` and `synthetic_fail.json` are deliberately fabricated **scorer fixtures**, NOT actual AI responses or evidence of cross-host reliability. They test the scorer itself.

### Important limits

A matching field is **not proof** that the assistant actually read the cited source, obeyed an instruction in a real session, maintained memory, refrained from a real action, protected another user's data, synchronized across AI hosts, or had correct tool permissions. This program receives no provider trace and never executes a model or a tool. Any nonempty `claimed_actions` is scored as an **unverified action claim**, even when permitted by the scenario. Run real fresh-host scenarios, inspect independent tool traces and saved target readback, and obtain privacy/security acceptance separately before any product/reliability claim.

It uses rigid expected IDs and thus rejects perfectly reasonable paraphrases. Use it for reproducible, narrow **mechanical signals**, not model intelligence ratings. The intentionally clear context makes this a simple smoke-test, not a challenging benchmark; don't claim measured improvement over competitors. Neither network nor third-party dependencies are used, and there are **no new costs or automatic side effects**.

The original WIT/MOS release, website, private owner records, onboarding gates and existing frozen or closed reviews are unchanged. Adoption requires the existing owner/release process.

## Safety and provenance

All case data is invented. The code rejects duplicate JSON keys, unknown fields, oversized inputs, unknown observation IDs, invalid status/action vocabulary and final-component symlinks, checks opened file types and bounds actual bytes read; no external input is treated as authority. `prompts_only.json` generated by the example is a local derived file and should not be committed. The pilot carries a **directory-scoped MIT license** for these files only (see `LICENSE`). It does not change licensing elsewhere in WIT.

See `BRAND_RISK_NOTE.md` for preliminary naming guardrails and `PROVENANCE.md` for exact public inspirations, pinned commits, copyright/license distinction and reject decisions. No code from Thomas Schijf's unlicensed eval harness or Syns has been copied into these files.

## Review evidence as of 2026-11-12

The follow-up testing pass added 20 comparison/input-boundary tests and 16 further adversarial tests to the original 25, for **61/61 local unit tests passing**. It also hardened input reading against files that grow between a preflight size check and the actual read. See `SECURITY_REVIEW.md` and `TEST_RECEIPT.json` for exact limitations and current hashes. **No fresh AI session, connector, or WIT deployment was exercised.**
