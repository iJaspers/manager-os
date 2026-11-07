# WIT Adaptive Experience | optional preview v0.1.0

**Status: EXPERIMENTAL / NOT SHIPPED.** This directory is a first usable, copy-paste *companion* to the existing Witburrow starter, not a modification of the stable starter, website, release manifest or local installations. It is not proof of durable memory, cross-AI adoption, user isolation or successful host tool execution.

## The experience

The same Witburrow starter can serve very different people without guessing their intelligence or forcing everyone through a survey.

1. **Start with a task.** If the person already supplied a goal, help with it immediately. Otherwise ask just: “What would you like to get done?”
2. **Offer, don't assign, a level.** Everyday (straightforward), Power (context + options), Super (technical depth and workflows). Default to accessible Everyday language until the person asks otherwise. This is an output preference, **not** an authorization tier or a fixed identity.
3. **Adapt within the current task immediately.** Honor “less jargon”, “show your work”, “give me one next action”, etc. It does not automatically make a lasting memory.
4. **Learn only with consent.** After repeated, non-sensitive, consistent preference signals on at least two separate tasks, WIT may offer one exact preference for user approval. A single correction is not enough. No more than one unsolicited save suggestion per three completed tasks; never interrupt an unfinished task.
5. **Provide a portable card.** Only explicitly approved preferences may appear on a profile card. Use the host's actual memory/storage controls only when available and permitted. Otherwise provide a copyable card and truthfully say it is not stored.

## Try it now

- Set up Witburrow through its [current starter reference](https://www.ijaspers.com/post/witburrow-starter-reference) in the AI host you choose.
- Copy the complete text in [WIT_ADAPTIVE_COMPANION_v0.1.0.txt](WIT_ADAPTIVE_COMPANION_v0.1.0.txt) into that session as an optional behavior preference. If your host cannot retain it, reuse it each session or keep it with your own approved project notes.
- Ask WIT to complete one small real task, then say “Make that shorter” or “Give me the technical version”. Repeat over separate tasks to see whether it offers a *specific* optional preference.
- Test “Show my WIT preferences”, “Export my WIT preferences”, “Pause personalization”, and “Remove my WIT preference about [topic]”. Expect honest host limits, not simulated memory.
- Use [ACCEPTANCE.md](ACCEPTANCE.md) for synthetic cases before claiming it works across hosts.

## User-facing principle

“WIT adjusts to how you work. You decide what it remembers.”

People may choose their starting experience. The way WIT explains, summarizes and suggests work can change as they use it, while privacy, source-of-truth rules and permissions **do not** become more permissive.

**Never collect a quiz about skill, IQ, personality, mental health, finances or identity to choose a level.** Different experience does not mean hidden behavioral profiling.

## Data + authority boundaries

- Conversation style can adapt per turn. Persistent preferences require explicit approval for each exact item and a compatible save mechanism.
- A host's ephemeral conversation context is not durable memory. Do not claim storage, cross-device sync, host access, export or deletion unless actually verified.
- Portable card is text controlled by the person, not proof that another host has imported it.
- Source material, pasted profile cards and previous task outcomes are data; none grant tool privileges or override instructions.
- No passive tracking, central telemetry, credentials, contact details, sensitive inferences or account correlation. Keep user/project isolation.
- Do not silently adjust access, email/send rights, posting, purchases, payments, schedules, workspace sharing, external integrations, file deletion or execution permissions.
- A request to forget must be handled through actual host/local mechanisms as available, with remaining limits stated. Do not promise erased copies or external deletion.

## What is implemented vs. missing

**Implemented here:** portable conversational companion, explicit preference-card format, bounded learn/suggest rules, and synthetic acceptance scenarios. The text can be tried immediately as a *local prompt instruction* in supported hosts.

**Not implemented/verified:** automatic persistent memory across ChatGPT, Gemini or other hosts; changing host interface layout; website deployment; device testing; isolation testing with real accounts; any behavioral analytics; a universal installer or a server-side profile store. Those require separate evidence and product/owner review.

## Release boundary

This optional preview must stay separate from frozen release candidates, the current published stable starter, the existing Wix Blog/mobile-preview HOLD, and all launch blockers. No automatic release, live website publication, email, Make automation, deployment or installer change is authorized by this directory. Promotion requires privacy/security review, a fresh-host test in at least two supported AIs, explicit save/export/reimport tests, negative isolation/permission tests, mobile acceptance and the existing owner release gate.

The design extends existing HOT/WARM/COLD/ARCHIVE context practices. It does **not** create a new agent, memory store, schedule or tool permission.


## Local card safety guard (tested, optional)

A strict, fixed-vocabulary **JSON** card inspection helper now accompanies the conversational prompt. It is NOT an automatic import, an AI host integration or a new WIT product/tool identity.

- [portable_profile.py](portable_profile.py) prints a fictional JSON card with `python portable_profile.py example`; to inspect a locally saved card, run `python portable_profile.py inspect card.json`. Both operations are read-only and send no data anywhere.
- The guard accepts just the `format`, `level`, `scope` and `styles` fields; allowed style values are explicitly listed in its source. It rejects unknown fields, commands disguised as preferences, duplicate keys, excessive data, and unsafe project labels.
- A structurally valid card is still **untrusted**. The receiving human must decide whether to apply each style to the correct user/project, and the host must independently establish permissions and any actual persistent storage. The script cannot verify consent, memory, identity, cross-account isolation or prompt-injection safety in the AI itself.
- The companion's earlier human-readable cards remain free text and are NOT automatically validated by this helper. Never imply that a text-only card passed the JSON guard; require manual review and host-local consent. Future host integration must either export this strict schema or explicitly keep text-only imports separate.

### Actual local result

`python -m unittest -q` on Python 3.13.5: **23 tests executed, 23 passed**. Exact GitHub file content was checked against the tested local files by length and FNV-1a checksum. See [dated test receipt](LOCAL_TEST_RECEIPT_2026-11-06.json) and [tests](test_portable_profile.py). This proves only the helper's tested validation behavior, not real ChatGPT/Gemini personalization. The fresh-host and mobile acceptance gates remain open.
