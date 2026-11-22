"""Readable source-first research handoff using existing WIT Scout modules.

Source search and retrieval remain host-owned. Neither a snippet nor a matched
quote is a completed task or an independent factual endorsement.
"""
from __future__ import annotations

from claim_review import _documents_index, verify_claims
from provider_adapter import ingest
from scout import canonical_url, rank

MAX_FINDINGS = 20


def build_handoff(payload, goal, claims, documents, level="practical"):
    if not isinstance(goal, str) or not goal.strip() or len(goal) > 500:
        raise ValueError("invalid goal")
    if level not in ("simple", "practical", "technical"):
        raise ValueError("invalid explanation level")
    doc_index = _documents_index(documents)
    ranked = rank(ingest(payload), goal)
    items = ranked[:MAX_FINDINGS]
    findings = []
    for item in items:
        source = canonical_url(item.url)
        doc = doc_index.get(source)
        found = {
            "title": item.title,
            "url": item.url,
            "evidence_state": "HOST_FETCHED_TEXT" if doc else "SEARCH_SNIPPET_ONLY",
            "description": (doc.text[:320].strip() if doc else item.excerpt) if level != "simple" else item.title,
            "description_origin": "HOST_FETCHED_TEXT" if doc else "PROVIDER_SNIPPET",
        }
        if level == "technical" and doc:
            found["sha256"] = doc.sha256
            found["retrieval_method"] = doc.retrieval_method
        findings.append(found)
    review = verify_claims(claims, documents)
    note = {
        "simple": "These are leads. A matched quote still needs someone to check what it means.",
        "practical": "Check the original sources, then review meaning and authorizations before adoption.",
        "technical": "Host fetch attestation is caller-owned. Verbatim quote matching is not a semantic or execution oracle.",
    }[level]
    return {
        "schema": "wit.research-handoff.v1",
        "goal": goal,
        "level": level,
        "verdict": review.verdict,
        "findings": findings,
        "omitted_findings": max(0, len(ranked) - MAX_FINDINGS),
        "claim_review": review.as_dict(),
        "next_step": note,
    }
