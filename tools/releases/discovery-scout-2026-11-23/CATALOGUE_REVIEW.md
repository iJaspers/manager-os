# Catalogue publication record

The two new catalogue entries point to immutable source commit [`bddae0091d1487ff18fcaa6223ec2ce811d5182f`](https://github.com/iJaspers/manager-os/commit/bddae0091d1487ff18fcaa6223ec2ce811d5182f). Each download, source directory, provenance file and test record is pinned to that same commit and exact tool version.

| Tool | Version | Public availability | Readiness |
|---|---|---|---|
| `wit.scout-explain` | `0.1.0-public-draft.1` | Source and ZIP available | Locally tested, nonproduction WIP; `public_ready: false` |
| `wit.school-contact-scout` | `0.1.0-preview.1` | Source and ZIP available | Locally tested, nonproduction WIP; `public_ready: false` |

The catalogue now contains **17 tool entries**, with **12 publicly available source entries** and **five private metadata-only candidates**, plus the separate starter. The two new records have matching privacy, authority and rights-scope review records. Existing entries, private candidate identities, contribution events and the outside contribution intake scope are preserved.

All **65 existing catalogue regression checks passed** after updating their explicit inventory expectations for the two additions. The current repository projection produces zero holds. No ranking, usage, contribution credit or readiness claim was invented.

The earlier frozen website embeds were not deployed or changed in this release. Their tests still show that they hold GitHub ZIP entries; adding repository metadata does not imply a live website rollout. Use the release's GitHub links for the new downloads.

The exact source commit also passed the new read-only GitHub Actions workflow: [run 45311269991](https://github.com/iJaspers/manager-os/actions/runs/45311269991). That run covers Scout Python/JavaScript, School Contact Scout self-tests and the catalogue as it existed at the source commit. The metadata publication has a separate exact-head CI run; inspect the main-targeted publication PR for its current result.

No released source or ZIP bytes were changed to add these metadata pins. FILE_MANIFEST.json records the preceding source publication; this metadata follow-up is represented by its own Git commit and PR diff.
