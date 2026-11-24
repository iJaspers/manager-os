# WIT research tools — public preview release

Release date: **23 November 2026**. This maintainer publication adds two versioned source previews and a phone start guide to the existing public WIT starter.

## Downloads and source

- [Start on your phone](START_HERE_PHONE.md): use the existing WIT starter in your chosen chat host.
- [Complete public bundle](WIT_Discovery_Scout_Public_2026-11-23.zip): starter text, handbook, optional companion, public guides and both research tools with fictional examples.
- [Scout + Explain 0.1.0-public-draft.1](../../scout-explain/0.1.0-public-draft.1/): source, setup, evidence/checkpoint behavior, tests and limitations.
- [School Contact Scout 0.1.0-preview.1](../../school-contact-scout/0.1.0-preview.1/): source, fictional baseline, offline demo and bounded refresh behavior.
- [Package checksums](PACKAGES.json) and [publication review](PUBLICATION_REVIEW.md).

## What changed

**Scout + Explain** makes the existing research experiment available from the default branch as a complete versioned preview. It includes result ranking and explanations, source/quotation checks, current connector response handling, qualified claim presentation, and checkpoint save/restore. Optional GitHub adapters require a trusted host and explicit allowed targets. The provider CLI consumes supplied JSON; it does not independently search the internet.

**School Contact Scout** provides a generic version of the public-source contact refresher. It preserves the baseline and separate school affiliations, distinguishes display/link conflicts, retains opt-outs and produces dated observations. URL checks reject internal destinations, connections use vetted public IP addresses, proxies are disabled, and redirects, source counts and response sizes are bounded. These safeguards do not make it a complete sandbox for an untrusted hosted service.

**Phone setup** now has one public starting point. The stable starter files retain their existing versions and bytes. The optional companion remains a release candidate. The new tools are local source previews, with no claim of native mobile acceptance, continuous search, LinkedIn scraping or automated email delivery.

## Privacy and rights

Only code, fictional examples, fresh public documentation and previously public starter artifacts are distributed here. Personal contact databases, campaign exports, recipient details, private source snapshots, account links, operational records and private integration history are excluded.

Each tool includes its provenance, observed test results and scope-specific rights notice. Source availability does not create a blanket MIT or commercial reuse grant. The companion's existing notice applies only to its defined contents. Third-party runtimes are external prerequisites, not bundled binaries.

## Versioning and rollback

This release is additive. It does not change the declared stable framework release or expand outside contribution intake. The existing nine-tool contribution policy remains in force. The older experiment PR and its history are retained; this publication selects and reviews source rather than merging the old experimental branch wholesale.

To stop using a preview, stop invoking it and return to your previous pinned version. Preserve your private working data and checkpoints. A maintainer can withdraw the catalogue entry or revert the publication commits without rewriting historical downloads. Do not overwrite a released ZIP with different bytes; choose a new version.

The repository catalogue and these links are the publication surface for this release. No claim is made that a separately deployed website embed or a user's existing installation has updated itself.
