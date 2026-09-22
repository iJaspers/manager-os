# Manager OS Observability

## Purpose

Manager OS uses minimal, privacy-preserving operational telemetry to answer basic public-project questions such as:

- how often the official update channel is checked;
- how often public MOS downloads are requested;
- which public MOS pages and buttons are used;
- whether a release is being discovered after publication.

This is observability, not user profiling.

## Update-check counter

A network-capable MOS installation SHOULD request:

`https://www.ijaspers.com/mos/check`

once per scheduled upstream check cycle.

That URL redirects to the authoritative public release channel. The request exists so the maintainer can count aggregate update-check traffic separately from ordinary site traffic.

### Do not attach identifiers

The request must not include:

- a user name or email address;
- an installation ID or device fingerprint;
- local project names or canonical state;
- prompts, transcripts, files, or memory;
- secrets, tokens, or credentials;
- custom query parameters containing local state.

No cookie, account, sign-in, or per-install telemetry is required by the MOS protocol.

### Metric meaning

A request to `/mos/check` is an **update-check request**, not proof of a unique active installation.

One installation can produce more than one request because of retries, manual checks, restores, proxies, or multiple environments. Reporting must not silently relabel request counts as unique installs.

If the check-counter URL is unavailable, update verification may fall back to the configured official release records. Observability failure must not block safe update discovery.

## Download counters

Official public download links may use stable redirect paths such as:

- `https://www.ijaspers.com/mos/download/pdf`
- `https://www.ijaspers.com/mos/download/txt`

These redirects allow aggregate request counting while preserving the existing downloadable files.

A download request is not proof that the file finished transferring, was opened, installed, or remains in use.

## Website analytics

The public site may use aggregate analytics for:

- page views and sessions;
- referral/source categories;
- device class;
- coarse geography;
- public button/link clicks;
- public navigation paths;
- search impressions/clicks/rankings;
- bot/crawler hits.

MOS does not require keystroke capture, private form contents, cross-site fingerprinting, or identity correlation.

## Reporting rule

Operational reports should distinguish:

- **update-check requests**;
- **download requests**;
- **button clicks**;
- **website visitors/sessions**;
- **known crawler traffic**.

Do not merge these into a single number called "users" or "installations".
