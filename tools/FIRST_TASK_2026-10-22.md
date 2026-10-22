# Your first everyday task with Witburrow

Guide ID: `WIT-FIRST-TASK-2026.10.22.1`  
Published: 2026-10-22  
Applies to the unchanged stable starter `MOS-2026.10.12.1` and public tool previews `0.1.1`.

This is an additive navigation and consent guide, not a new framework package, automatic installer or proof of host capability.

## 1. Start small and check the host

Start at the [official starter page](https://www.ijaspers.com/post/manager-os), read the setup instructions, and give the starter to the AI host you actually use. Ask for one small everyday task. Confirm where your working record will be saved and what the host can actually read, browse or run. If it cannot browse, open the catalogue yourself; if it cannot execute code, do not claim it ran a tool. Use the local browser or Python requirements below only if available and approved.

The manager's default name is Wit. Keep any chosen custom name. Existing installations review and approve the optional naming supplement locally; fetching this guide does not install it.

## 2. Match the task to a real public tool

Open the [current public catalogue](https://www.ijaspers.com/post/witburrow-tools) and choose **Public downloads & source**. A private candidate is not an available download. These three tools are public source previews, not a ranking or proof of production readiness:

- `wit.invoice-reference-review@0.1.1`: invoice and payment exception review from CSV. Requires invoice IDs **and known positive amounts**, single currency. Not a reference-only duplicate checker. No refunds, credits, FX or accounting writes.
- `wit.pretax-role-comparison@0.1.1`: two hourly/salary cash scenarios and commute costs. Modern local browser. Before tax; unknown terms remain unknown, not zero. No benefits or offer authentication.
- `wit.documented-compensation-comparison@0.1.1`: documented hourly inputs, overtime evidence, commute and dues. Python 3.9+ standard library; not salary, tax or benefit analysis.

If the inputs or runtime do not fit, clarify or keep the task manual. Never invent missing amounts, evidence, permissions or installed capabilities to make a tool appear suitable.

## 3. Inspect, consent, and try synthetic data first

Read the selected version's README, limits, provenance, license and test results. Download its ZIP only when you choose to. Compare the ZIP checksum on the catalogue and the member hashes in SHA256SUMS.json. Hash equality proves byte consistency, not safety or author identity.

Before an assistant downloads, opens or runs anything, agree on the exact tool/version, local runtime, inputs, expected output and what it may save. For example: "Use the fictional demo with wit.invoice-reference-review 0.1.1 locally. Show the exceptions only; do not upload records, post accounting entries, contact anyone or change files beyond the agreed output." The host's own permission and safety requirements still apply.

HTML tools: unzip and open `tool.html` locally in a modern browser. Python tool: unzip, inspect `example.json`, then run `python3 tool.py --input example.json`. No credentials or dependency installation are needed. Browser/device acceptance is not yet verified; published Node/Python engine tests are narrower evidence.

## 4. Invoice example: minimum inputs and no-payment evidence

References alone are **not enough** for this version. A CSV lacking `amount` is held with `Missing column: amount`. Ask for the actual known amounts or perform a clearly labelled manual reference-only review; do not fill in guessed values or zeroes.

For a fictional demonstration only, invoice CSV:

```csv
invoice_id,amount
INV-DEMO-1,100.00
```

If there are **no supplied payment rows**, paste this header-only CSV in the payment field:

```csv
invoice_id,amount,payment_id
```

Do not leave the payment field empty: empty text is held with `No CSV rows`. The header-only example produces `NO_PAYMENT_EVIDENCE` for the invoice. That means no payment evidence was supplied, not that a real invoice is unpaid or that a bank deposit was verified. The built-in fictional demo is another safe starting point.

Keep originals unchanged, review every exception against source evidence, and never treat a reference/amount candidate as an authenticated posting. Export only if needed and approved; diagnostic files can contain the inputs you supplied. Never attach real customer, financial, employer or personal records to a public report.

## 5. Save the result and hand it back

Record the exact public ID/version and source commit, input provenance (synthetic or your own permitted local records), actual action and output, test evidence, unresolved questions and one next step. Separate "prepared", "ran", "verified against evidence" and "not checked". If the host could not run it, report that instead of inventing a result.

To improve one of these three tools, follow [CONTRIBUTING.md](https://github.com/iJaspers/manager-os/blob/main/CONTRIBUTING.md), fork the repository and open a [pull request](https://github.com/iJaspers/manager-os/compare) with the template. Include exact base ID/version/commit, bounded changes, tests and actual results, known failures, unfinished work, license/provenance and preferred public attribution. Share source and synthetic fixtures only. Privacy/license/unsafe-behavior review happens before isolated manual tests; merge, new version, catalogue update and credit require review. There is no automatic execution, auto-merge or response-time promise.

The packaging path has a local simulated pickup/change/retest/return-patch check and a controlled internal documentation PR. Neither is outsider adoption or an independent security audit. Broader framework/security-sensitive intake and voting remain closed.
