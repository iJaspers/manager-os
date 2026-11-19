# WIT Scout + Explain | Experimental checkpoint | 2026-11-19

## DONE
- Experimental branch `experiment/wit-scout-explain-20261119` holds scout.py, provider_adapter.py, evidence_gate.py and their tests.
- Recovered files locally and ran `python -m unittest discover -s /mnt/data/wit_scout -p 'test*.py' -q`: **18 tests passed**.
- Fresh GitHub connector reads verified three real READMEs: cedarsaam/agent-search, theYahia/qsearch, soumics/adaptive-ai-tutor.
- No stable merge, public publication, outreach or paid API use.

## LIMITS / RISKS
- No autonomous live search provider implemented: adapter ingests supplied JSON.
- Host attestation flag is caller-controlled, not cryptographic; safe only when a trusted integration controls the call.
- URL string checks alone do not enforce DNS/redirect protections. Network fetch must be handled by a trusted host.
- A fetched README proves the source text was retrieved, not that claims are independently true.
- Explanation levels are templates, not yet demonstrated comprehension improvement.

## NEXT
1. Implement trusted search-provider orchestration with strict separation of untrusted result fields and host attestation.
2. Add a live end-to-end fixture that searches, fetches and compares against a baseline with provenance.
3. Add human comprehension checks and regression cases.
4. Run Combo-Breaker and review before any merge.

## WAITING ON
None for isolated experiments. Production release remains blocked by end-to-end evidence and security acceptance.
