# WIT Discovery and Scout: start with any question

Discovery finds candidate sources when your AI host has search or a connector. Scout + Explain ranks supplied results and helps you review the evidence. Neither requires a school, contact, or outreach workflow.

## Start on your phone

Follow steps 1–3 in [the phone setup guide](START_HERE_PHONE.md), then send this instead of its school example:

> Help me investigate [question] so I can [make a decision or understand something]. Use available search tools or tell me what sources I can provide. Prefer authoritative sources for the topic. Show the best-supported finding, put its source link next to it, distinguish what the source actually says from inference, and flag what still needs checking. End with one useful next step.

Try comparing two repair options, finding the official guidance for a form, or planning a trip around a constraint. If the host cannot search, paste sources or search-result text. If you only supplied snippets, the answer should say so. Keep evidence, gaps, and the next step in your return note.

## Try offline on a computer

From the repository root, use the existing Scout Python CLI with the [fictional multi-topic fixture](general_inquiry_results.json):

```shell
python tools/scout-explain/0.1.0-public-draft.1/provider_adapter.py tools/releases/discovery-scout-2026-11-23/general_inquiry_results.json --goal "bicycle brake pad compatibility" --level simple
python tools/scout-explain/0.1.0-public-draft.1/provider_adapter.py tools/releases/discovery-scout-2026-11-23/general_inquiry_results.json --goal "ferry bicycle reservation rules" --level simple
```

The different goals should rank different sources first without changing tools or settings. These results are invented snippets, not real guidance. The CLI ranks results you provide; it does not browse or run outreach.

**Optional:** [School Contact Scout](../../school-contact-scout/0.1.0-preview.1/) rechecks recorded public source pages for known contacts. Skip it unless that is the job. It does not establish permission to contact anyone. Do not upload private datasets or unpublished checkpoint material to a public repo or unfamiliar service.

This companion guide doesn't change the previously released bundle or any tool version.
