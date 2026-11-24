# Verification — 0.1.0-preview.1

Verification date: **2026-11-23**.

## Observed result

```sh
python school_contact_scout.py --self-test
```

**21 tests passed; 0 failures or errors.** Runtime: **CPython 3.12.14**, Linux x86-64, glibc 2.41. No additional packages were installed or used.

The suite checks:

- Public text and mailto extraction; arbitrary scripts, templates and style data excluded.
- Display/link contradictions, malformed links, separate-cell conflicts and multiple-person rows.
- Standard publicly delivered Joomla mail widgets, including malformed widgets.
- Distinct missing, partial, failed and unselected-source outcomes.
- Original-record and opt-out preservation.
- Public URL syntax, recorded-host redirects and HTTPS downgrade refusal.
- Private/mixed DNS rejection before connection, pinned IP connections without a second DNS lookup, and bounded connection attempts.
- Redirect count limits, disabled environment proxies and retained TLS hostname/certificate checks.
- Redirect bodies are never read for 301/302/303/307/308 responses, including a rejected unsafe redirect; each response is closed before proceeding.
- HTML-depth and unique-address bounds, compressed/decoded response limits and CSV formula escaping.
- Baseline shape, ID, email and source validation.
- Complete fictional demo execution with network functions mocked to fail if called.

The demo produced the expected **five observations**: three `still_published`, one `source_conflict`, one `not_found_on_recorded_sources`; plus **two unreviewed candidates**. The fictional baseline remained byte-identical, its opt-out was retained, and both school affiliations for one address remained present.

`--version` returned `School Contact Scout 0.1.0-preview.1`.

An independent source review found that the inherited standard-library redirect handler drained redirect bodies without a read limit. The preview now supplies its own redirect dispatch that skips and closes those bodies, and the additional regression fails on any attempted redirect-body read. The full suite was rerun after that correction.

## Privacy review

The package was scanned for source-project identifiers, real school domains, owner details and local workspace paths. None were found. Email examples use only `example.org`; all example people and schools are fictional. No baseline from a real school, result CSV, source snapshot, recipient list or campaign data is bundled.

## Verification limits

No live source requests were run for this generic release. Network behavior was tested through mocks and standard-library boundary checks; this is not live-network acceptance or a penetration test. Python 3.9+ compatibility is the intended interface, but the observed execution environment was Python 3.12.14 only.

The tests establish the exercised cases, not completeness of every site parser or hosting configuration. Public-page publication remains distinct from current employment, mailbox delivery and permission to contact. This preview has no strict overall wall-clock deadline and is not a complete sandbox for a hosted multi-tenant fetch service.
