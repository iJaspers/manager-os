# Multi-platform opportunity discovery: experimental runtime

This directory contains an offline, Python-standard-library opportunity evaluator and SQLite state store. No live network adapters, account access, automated posting, or paid APIs.

## Files
- `opportunity.py`: source URL normalization, explicit eligibility gates, scoring and JSON stdin/stdout CLI.
- `store.py`: durable SQLite record persistence and append-only feedback event history.
- `test_opportunity.py`: evaluator tests.
- `test_store.py`: restart, replay, feedback and safety tests.

## Run tests
```bash
cd tools/opportunity_discovery
python -m unittest discover -v
```

## Run a standalone scoring batch
```bash
python opportunity.py < input.json > scored.json
```

Optional `fit_requirements` records name up to 12 **required** capabilities.
Each row has a unique short lowercase `id`, a reviewer-supplied `status`,
and `evidence_index`: a zero-based position in the existing `evidence_urls`
for `SUPPORTED` or `NOT_MET`, or `null` for `UNKNOWN`. Use generic IDs,
not private names or raw snippets. A pointer does not prove what its source
says. Any unknown or unmet requirement blocks advancement regardless of score;
all supported requirements still cannot bypass existing fit, freshness, rules,
or authority gates. Omitting the field preserves the original output shape.

To persist records from another Python program:
```python
from store import Store
s = Store("data/wit_opportunities.sqlite")
try:
    results = s.ingest(items) # items are normalized input dictionaries
    s.feedback(results[0]["id"], "GOOD", "genuine help request")
finally:
    s.close()
```

## Boundaries
- Offline only; supplied records are not independently verified.
- A score is not a posting authorization.
- Source-specific rules and live status must be checked externally.
- SQLite uses WAL and FULL synchronous writes, but backups, crash injection and concurrent writer acceptance have not been independently tested.
- Existing records are not automatically re-scored when input or scoring rules change.
- Records are keyed by normalized URL, not cross-platform content similarity.
- No credential storage or automated external actions.
- Unit test source exists; passing test results must be obtained by actually executing it, not inferred from the test definitions.
- Stable WIT remains unchanged; human approval required for promotion.

Upstream architectural inspiration: OctoSift (AGPL-3.0-only); no copied implementation code.
