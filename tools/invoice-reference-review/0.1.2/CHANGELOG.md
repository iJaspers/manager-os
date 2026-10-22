# Changelog

## 0.1.2 — 2026-10-22

Correct malformed CSV quote handling and enforce the documented 1 MiB maximum in UTF-8 bytes rather than JavaScript characters. Add exact minimum-input guidance and stress regressions. Version 0.1.1 is retained as history and should not be used for matching decisions. No new network, storage, dependency, authority or accounting-write behavior.

## 0.1.1 — 2026-10-22

Documentation/identity revision: open the owner-approved scoped public-tool pull-request route, document review gates and bump visible version. Calculation behavior is unchanged from 0.1.0.

## 0.1.0 — 2026-10-22

Initial sanitized public derivative. Fixed spreadsheet formula injection in CSV export; duplicate payment references now hold every affected invoice; duplicate/blank headers and aggregate overflow fail closed. Replaced examples with explicitly fictional data and added a bounded input size.
