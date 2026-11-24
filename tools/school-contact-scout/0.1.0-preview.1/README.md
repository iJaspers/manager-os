# School Contact Scout

**Version: 0.1.0-preview.1** · Python 3.9+ · standard library only

Refresh the public source pages behind an existing school-contact list. The tool reports whether each recorded address remains published, surfaces contradictory links, and separates new addresses into a review queue. It preserves the original baseline and its record IDs, school affiliations, notes and opt-out fields.

This is a small preview component for WIT / Discovery / Scout. It checks a user-supplied list of source URLs; it does not discover every teacher, crawl the web, prove current employment or send messages.

## Try it offline

```sh
python school_contact_scout.py --version
python school_contact_scout.py --self-test
python school_contact_scout.py --demo --output-dir ./demo_runs
```

The demo uses the bundled `example_baseline.json` and HTML fixtures embedded in the script. Every person, school and email is fictional, using the reserved `example.org` domain. The demo and self-tests make no network requests. The fictional baseline is deliberately refused by live mode.

The demo should report five records: three `still_published`, one `source_conflict`, and one `not_found_on_recorded_sources`, plus two unreviewed candidates. It also preserves an opt-out and two school affiliations for the same fictional teacher.

Running the program without an explicit mode or baseline displays usage and exits without accessing the network.

## Refresh your own accepted baseline

```sh
python school_contact_scout.py --baseline ./my_contacts.json --limit 20 --workers 1 --output-dir ./refresh_runs
```

To select particular recorded sources:

```sh
python school_contact_scout.py --baseline ./my_contacts.json --source-url https://example.org/schools/north/staff --output-dir ./refresh_runs
```

The URL above is an example: replace it with a public source already recorded in your own baseline. `--source-url` is repeatable and must match an explicit baseline source exactly. Page links are never followed as crawl targets.

Defaults are 20 source URLs, two concurrent workers, and a 20-second socket timeout. Supported bounds are 1–100 URLs per run, 1–4 workers and 1–20 seconds per socket operation. A URL can follow at most four redirects, so a 100-source run can issue at most 500 HTTP requests. Connection attempts to vetted DNS answers are separately capped at four per HTTP connection. There are no application retries.

Use the smallest source selection that answers the question, respect source-site terms and access restrictions, and stop if a site rejects access. The tool reports errors instead of bypassing sign-in or challenge pages.

## Baseline format

The JSON root contains `teachers` and/or `school_contacts` arrays. Each accepted record requires:

| Field | Required content |
|---|---|
| `record_id` | Stable, nonempty string, unique across both arrays, at most 128 characters |
| `email` | Previously reviewed, explicitly published address; at most 254 characters |
| `source_url` | Public HTTP(S) URL where the address was recorded |

Alternatively, source URLs may be provided in `additional_source_url` or the `alternate_source_urls` array. Every record must have at least one source. URLs must use the scheme's standard port, have no credentials, control characters, backslashes or fragment, and use a fully qualified ASCII hostname. Use punycode for internationalized names.

Optional fields include `school`, `name`, `role`, `teacher_flag`, `source_year`, `checked_date`, `outreach_status`, `do_not_contact`, and `notes`. Unknown fields are retained in each output record's full baseline snapshot. Missing `teacher_flag` becomes `Unknown` in the observation view, without changing the baseline. An optional `reviews` array can retain `displayed_email` and `linked_email` values for unresolved address conflicts.

The input limit is 16 MiB, 10,000 accepted records, and 1,000 unique source URLs. Baseline data is never uploaded to an AI service. Live mode requests only the selected public source pages, although those requests are visible to the source websites and your network provider.

## Outputs

Each run creates a new timestamped directory:

- **`refresh_records.csv`** — One observation for every existing record ID, its original snapshot, all baseline school affiliations, publication status, and source errors/conflicts.
- **`unreviewed_candidates.csv`** — Additional addresses found on selected pages whose domains match accepted baseline domains. Names, roles, relevance and contact permission remain unverified. Existing review items remain labelled.
- **`run_summary.json`** — Source URLs, redirects, errors, content hashes, baseline hash, counts, request bounds and limitations.

Dates and timestamps use **UTC** and remain separate from the original roster year. CSV cells beginning with spreadsheet formula markers are escaped. Outputs can contain the personal and operational data in your supplied baseline; keep them in an appropriately private location. Do not publish real baseline files or generated contact reports with this source package.

The baseline is read only. Observations never overwrite its original fields or an outreach ledger. Do not import an old output snapshot over newer notes or opt-outs.

## Status meanings

| Status | Meaning |
|---|---|
| `still_published` | Address appeared on at least one successfully checked recorded source. Errors on other sources remain visible. |
| `source_conflict` | Visible email and linked email/widget disagree. Review before use. |
| `not_found_on_recorded_sources` | All recorded sources were successfully checked and lacked the address. This does not establish that someone left the school. |
| `indeterminate_fetch_error` | Address was not observed and at least one selected source could not be checked. |
| `incomplete_source_check` | Checked sources lacked the address, but some recorded sources were omitted by the run limit. |
| `not_checked_limit` | None of the record's sources was selected. |

Publication does not verify current employment, mailbox deliverability, program relevance or permission to send promotional messages. Review new or changed contacts manually and apply the sender's applicable outreach requirements before use.

## Network and parser boundaries

- Only recorded public HTTP(S) source URLs are requested. Redirect hosts must also appear in the baseline; HTTPS downgrades are refused. Bodies of 301, 302, 303, 307 and 308 redirect responses are closed without being read.
- IP-literal and local/reserved hostnames are rejected. Each connection resolves its hostname once, rejects the entire answer set if any address is nonpublic, and connects directly to a vetted address. This prevents the ordinary DNS check-then-resolve rebinding gap.
- HTTPS retains certificate and hostname verification against the original host. Environment proxies, proxy tunnels, credentials, cookies and login sessions are not used.
- Each response has a 2 MiB wire limit and 2 MiB decompressed limit. HTML is capped at 25,000 nodes, 64 nesting levels and 10,000 unique addresses per source. Socket timeouts are per operation; OS DNS lookup has its own timeout. There is no strict overall wall-clock deadline.
- HTML, XHTML and plain text are supported. Extraction reads visible text, `mailto:` links and the standard publicly delivered Joomla mail widget. It does not execute JavaScript, infer address patterns, repair malformed addresses, or automatically pair multiple names with multiple emails.
- JavaScript-rendered JSON maps, PDFs, images and authenticated directories are unsupported. The task-specific district JSON adapter from the private prototype is deliberately absent from this generic preview.

These checks are designed for a local command-line workflow. They are not a complete sandbox for offering an untrusted multi-tenant fetching service. A hosted deployment would also need network-level egress controls, authentication, operational limits and its own review.

## Verification and lineage

The included self-tests cover parsing, displayed/link conflicts, malformed-address handling, unsupported script data, partial/failing source distinctions, record preservation, URL validation, private and mixed DNS answers, pinned sockets, bounded redirects/connections, disabled environment proxies, TLS hostname checking, decompression/parser limits, CSV formula escaping, input-schema failures and a complete offline demo.

This preview was extracted and generalized from a task-specific WIT school-contact refresh utility written for the project. It is original project code built with Python's standard library; no OctoSift implementation or third-party runtime code is copied or vendored. The broader opportunity-discovery work informed the workflow, but this package is not a complete lead-generation platform.

No separate third-party license claim is made here. Apply the owning repository's licensing decision when integrating this code; this directory does not grant a new license by itself.
