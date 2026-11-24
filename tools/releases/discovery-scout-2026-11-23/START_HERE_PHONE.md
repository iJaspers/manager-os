# WIT, Discovery and Scout — start on your phone

Public preview · 23 November 2026

## Start with WIT

WIT is a set of instructions and working records for the AI host you already use. The simplest phone setup uses the public text starter in an existing chat.

1. Download [the WIT starter text](https://raw.githubusercontent.com/iJaspers/manager-os/main/downloads/MOS_PUBLIC_PACK_v2026.10.12-R1.txt).
2. Open your chosen AI chat app. Attach the text file if your app and account support attachments, or open the file and paste its text.
3. Send this setup request:

   > Use this public WIT starter for this conversation. Help me complete one task at a time and keep a short record of decisions, evidence, next actions and unfinished work. Tell me which tools and storage you actually have. Ask only for missing information that blocks the task. Do not assume access to another person's account or a previous private installation.

4. Give it one real task. For example: “Help me research school program opportunities. Use official sources, retain source links and observation dates, and separate confirmed information from items needing review.”
5. At the end of a session, ask for a short return note with the current goal, completed work, evidence links, next action and any unresolved question. Save that note where you can attach or paste it next time.

The declared stable starter remains **MOS-2026.10.12.1 / v2026.10.12-R1**. This release adds separate experimental research utilities; it does not silently replace that starter. The [optional Bob companion RC1](https://github.com/iJaspers/manager-os/blob/main/downloads/WIT_Starter_Companion_2026.11.01-rc1.zip) retains its own scope and notices.

ChatGPT documents supported attachment types and account limits in its [file upload guide](https://help.openai.com/en/articles/8555545-uploading-files-and-audio-to-chatgpt). Other hosts have their own capabilities. Instructions do not create memory, connectors, background jobs or permissions that the host lacks.

## Add the research tools when useful

| Component | What it does | Where it runs |
|---|---|---|
| WIT starter | Organizes a task, decisions and handoffs | An existing AI chat host, including a phone client |
| [Scout + Explain](../../scout-explain/0.1.0-public-draft.1/) | Ranks supplied search results, records evidence and checkpoints, and helps review research claims | Python; optional JavaScript trusted-host adapter |
| [School Contact Scout](../../school-contact-scout/0.1.0-preview.1/) | Rechecks whether recorded email addresses still appear on approved source pages | Python CLI; fictional offline demo included |

Download the [complete public bundle](WIT_Discovery_Scout_Public_2026-11-23.zip) to keep the starter, handbook, guides and both tool previews together. Unzip it to read the included files. The Python tools need a suitable runtime; uploading their files to a phone chat does not install or execute them.

There is no native mobile app or demonstrated one-tap phone installation in this release. A host that supports code execution may be able to run reviewed code within its own limits. This release does not include an autonomous LinkedIn crawler, automatic outreach or a scheduled lead-generation service.

## Use your own data carefully

The examples are fictional. Real contact baselines, research checkpoints and source responses can contain personal information. Keep your working data private and review generated outputs before sharing them. A published work email does not establish that someone is still employed in a role, that the mailbox works or that promotional email is permitted.

For the exact tool commands, tests and limits, use each version's README and TEST_RESULTS file. [Release contents and review](README.md).
