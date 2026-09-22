# Manager OS Observability

## Purpose

Manager OS uses minimal, privacy-preserving operational telemetry to answer basic public-project questions such as:

- how often public MOS pages are visited;
- how often public MOS download controls are used;
- which public distribution source sent traffic;
- whether a release is being discovered after publication.

This is observability, not user profiling.

## Current production status

### Verified live

The public iJaspers site can currently report:

- page views, sessions, and unique visitors;
- referral category, source, domain, and often the exact referring URL;
- public button/link interactions, including MOS PDF/TXT download controls;
- blog reading and engagement metrics;
- Google Search page metrics;
- UTM campaign/source/content attribution on tagged landing-page traffic.

### Not yet verified as route-level counters

The following stable redirect paths are live, but **their direct request counts are not currently verified as separately persisted telemetry**:

- `https://www.ijaspers.com/mos/check`
- `https://www.ijaspers.com/mos/download/pdf`
- `https://www.ijaspers.com/mos/download/txt`

Do not report redirect-route hits as update checks, downloads, users, or installations unless a dedicated counter is later implemented and verified.

Website button-click analytics can still measure people clicking the MOS download controls on the tracked landing page. That is a different metric from direct redirect requests originating elsewhere.

## Update-check path

A network-capable MOS installation MAY request:

`https://www.ijaspers.com/mos/check`

once per scheduled upstream check cycle.

That URL currently redirects to the authoritative public release channel.

### Do not attach identifiers

The request must not include:

- a user name or email address;
- an installation ID or device fingerprint;
- local project names or canonical state;
- prompts, transcripts, files, or memory;
- secrets, tokens, or credentials;
- custom query parameters containing local state.

No account, sign-in, or per-install identifier is required by the MOS protocol.

### Metric meaning

If dedicated route-level counting is implemented later, a request to `/mos/check` will mean an **update-check request**, not proof of a unique active installation.

One installation may produce more than one request because of retries, manual checks, restores, proxies, or multiple environments. Reporting must never silently relabel request counts as unique installs.

If the check URL is unavailable, update verification may fall back to the configured official release records. Observability failure must not block safe update discovery.

## Download paths

Official public download links use stable redirect paths:

- `https://www.ijaspers.com/mos/download/pdf`
- `https://www.ijaspers.com/mos/download/txt`

A direct redirect request is not currently a verified counted download metric.

A tracked website button click is also not proof that the file finished transferring, was opened, installed, or remains in use.

## Distribution attribution

For future public promotion, use source-specific short links that redirect to the MOS landing page with UTM attribution:

- LocalLLaMA: `https://www.ijaspers.com/go/mos-reddit-localllama`
- ChatGPTCoding: `https://www.ijaspers.com/go/mos-reddit-chatgptcoding`
- SideProject: `https://www.ijaspers.com/go/mos-reddit-sideproject`
- GitHub: `https://www.ijaspers.com/go/mos-github`
- LinkedIn: `https://www.ijaspers.com/go/mos-linkedin`
- Hacker News: `https://www.ijaspers.com/go/mos-hackernews`

These links carry only distribution attribution. They must not be extended with user identity, device identity, project state, or private MOS data.

## Website analytics

The public site may use aggregate analytics for:

- page views and sessions;
- referral/source categories;
- UTM source/campaign/content;
- device class;
- coarse geography;
- public button/link clicks;
- public navigation paths;
- search impressions/clicks/rankings;
- bot/crawler hits.

MOS does not require keystroke capture, private form contents, cross-site fingerprinting, or identity correlation.

## Reporting rule

Operational reports should distinguish:

- **tracked landing-page visits**;
- **referral/UTM source**;
- **website download-button clicks**;
- **direct redirect requests** (only after dedicated counting is verified);
- **website visitors/sessions**;
- **known crawler traffic**;
- **GitHub repository activity**.

Do not merge these into a single number called "users" or "installations".
