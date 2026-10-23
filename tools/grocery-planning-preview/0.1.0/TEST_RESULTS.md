# Check evidence: wit.grocery-planning-preview@0.1.0

17 functional and 9 input-boundary/recovery checks passed on 2026-10-22 and rerun for packaging on 2026-10-23. These cover supplied-price arithmetic, missing prices/inputs, unit and identifier validation, exact-cent output, duplicate keys, invalid UTF-8, exact/over 1 MiB, depth, repeated calculations and invalid-to-valid recovery. This is local Python evidence, not device/production capacity acceptance.

Commands:

```sh
python3 -m unittest -v test_tool.py test_boundaries.py
python3 tool.py example.json
```

All fixtures are synthetic. The tests inspect source behavior or use stub DOM objects; they do not establish rendered-browser, mobile, device or production-capacity acceptance. Work-in-progress publication is for transparent continuation, not a promise of correctness. Tests not run and known limitations are listed in README.md. No outsider continuation or independent security audit is claimed.
