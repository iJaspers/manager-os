# Check evidence: wit.bill-calendar-preview@0.1.0

17 Node VM/DOM-stub checks passed on 2026-10-22 and rerun for packaging on 2026-10-23. They cover labelled and legacy entries, exact-cent balances, opening/day-end/debit-first gaps, invalid dates/money/labels, 20-row and 8,192-character bounds, text-only output and static network/storage restrictions.

Commands:

```sh
node test.js
```

All fixtures are synthetic. The tests inspect source behavior or use stub DOM objects; they do not establish rendered-browser, mobile, device or production-capacity acceptance. Work-in-progress publication is for transparent continuation, not a promise of correctness. Tests not run and known limitations are listed in README.md. No outsider continuation or independent security audit is claimed.
