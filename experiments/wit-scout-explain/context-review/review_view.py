"""Read-only context and proposed-memory views of an existing ResearchSession.

This is a trusted-host/library interface, not a JSON upload or authentication
service. It does not retrieve sources, send model input, store memories, or
approve anything. A host must already have authority to read the session.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
import json
from urllib.parse import urlsplit

from _base import (Gathered, ResearchSession, SCHEMA, MAX_CHECKPOINT_BYTES, _decode, _restore,
                   build_handoff, canonical_url)

SCHEMA_VERSION = "wit.context-memory-review.v1"
ORIGINS = frozenset({"SYNTHETIC_DEMO", "HOST_SOURCE_REPLAY", "HOST_SESSION"})


@dataclass(frozen=True)
class UsageObservation:
    """An optional last-request measurement supplied by trusted host code.

    Type/schema validation is not authentication. Never construct this from
    source text or a model-generated claim. It is not the next prompt's size.
    """
    input_tokens: int
    request_id: str
    reported_at: str
    context_window: int | None = None


def _validate_session(session):
    if type(session) is not ResearchSession or type(session.gathered) is not Gathered:
        raise ValueError("An existing host-owned ResearchSession is required")
    # Reuse the frozen checkpoint validator, including claim schemas, receipt
    # binding, source allowlists, duplicate handling and byte/collection limits.
    # This is validation in memory, not a second checkpoint or an attestation.
    data = {
        "schema": SCHEMA, "code_revision": session.code_revision,
        "approved_urls": list(session.approved_urls), "payload": session.payload,
        "goal": session.goal, "claims": list(session.claims),
        "gathered": asdict(session.gathered),
    }
    try:
        raw = json.dumps(data, ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, UnicodeError, RecursionError) as exc:
        raise ValueError("Session must be bounded JSON data") from exc
    if len(raw) > MAX_CHECKPOINT_BYTES:
        raise ValueError("Session exceeds the existing checkpoint byte budget")
    return _restore(_decode(raw), session.code_revision, session.approved_urls)


def _usage_view(observation, characters):
    result = {
        "state": "UNAVAILABLE", "input_tokens": None,
        "context_window": None, "request_id": None, "reported_at": None,
        "evidence_characters": characters,
        "evidence_tokens_estimate": (characters + 3) // 4,
        "estimate_scope": (
            "Rough characters/4 estimate of retained source text and unfetched "
            "snippets only; excludes system instructions, conversation history "
            "and other model inputs. Not a measured prompt size."
        ),
    }
    if observation is None:
        return result
    if type(observation) is not UsageObservation:
        raise ValueError("Usage must come from a host UsageObservation")
    if type(observation.input_tokens) is not int or not 0 <= observation.input_tokens <= 10**9:
        raise ValueError("Invalid reported token count")
    if observation.context_window is not None and (
            type(observation.context_window) is not int or
            not 0 < observation.context_window <= 10**9):
        raise ValueError("Invalid reported context window")
    if (not isinstance(observation.request_id, str) or
            not observation.request_id.strip() or len(observation.request_id) > 200):
        raise ValueError("A bounded request identifier is required")
    if not isinstance(observation.reported_at, str) or len(observation.reported_at) > 40:
        raise ValueError("Invalid usage timestamp")
    try:
        when = datetime.fromisoformat(observation.reported_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Invalid usage timestamp") from exc
    if when.tzinfo is None or when.utcoffset() is None:
        raise ValueError("Usage timestamp requires a timezone")
    result.update(state="PROVIDER_REPORTED", input_tokens=observation.input_tokens,
                  context_window=observation.context_window,
                  request_id=observation.request_id, reported_at=when.isoformat())
    return result


def _context_sources(session, handoff):
    ranked = {canonical_url(item.url): item for item in session.gathered.ranked}
    positions = {url: index + 1 for index, url in enumerate(ranked)}
    docs = {canonical_url(doc.source.url): doc for doc in session.gathered.documents}
    receipts = {item.requested_url: item for item in session.gathered.receipts}
    failures = {item["url"]: item["reason"] for item in session.gathered.failures}
    displayed = {canonical_url(item["url"]) for item in handoff["findings"]}
    cited_by, evidence_issues = defaultdict(list), defaultdict(set)
    for proposal in handoff["claim_details"]:
        for entry in proposal["evidence"]:
            url = entry["source_url"]
            if proposal["id"] not in cited_by[url]:
                cited_by[url].append(proposal["id"])
            if entry["evidence_state"] != "MATCHED_HOST_TEXT":
                evidence_issues[url].add(entry["evidence_state"])
    # Include every ranked input (including omitted findings) and every cited
    # missing source. Never hide a missing citation by iterating fetched docs only.
    urls = list(ranked) + sorted(set(cited_by) - set(ranked))
    rows, characters = [], 0
    for url in urls:
        item, doc, receipt = ranked.get(url), docs.get(url), receipts.get(url)
        roles = []
        if url in cited_by:
            roles.append("CLAIM_CHECK")
        if url in displayed:
            roles.append("DISPLAYED_FINDING")
        if url in ranked:
            roles.append("RANKING_INPUT")
        reason = []
        if url in cited_by:
            reason.append("Cited by proposal(s): " + ", ".join(cited_by[url]))
        if url in ranked:
            reason.append(f"Ranked result {positions[url]} of {len(ranked)}")
        pinned_revision = None
        issues = set(evidence_issues[url])
        if doc is not None:
            fetch_state = "RETRIEVED"
            characters += len(doc.text)
            if doc.retrieval_method == "github_connector":
                # _restore checked the immutable target and whole Git blob.
                pinned_revision = urlsplit(doc.canonical_url).path.split("/")[4]
                coverage = "COMPLETE_PINNED_FILE"
            else:
                # The current browser/search HostRead contract does not attest
                # whether retained text is the whole page or only an excerpt.
                coverage = "RETRIEVED_TEXT_COVERAGE_UNKNOWN"
        else:
            characters += len(item.excerpt) if item else 0
            coverage = "SNIPPET_ONLY" if item else "NO_SOURCE_TEXT"
            fetch_state = ("FETCH_FAILED" if url in failures else
                           "NOT_FETCHED" if item else "MISSING_FROM_SESSION")
            if url in failures:
                issues.add(failures[url])
        rows.append({
            "title": item.title if item else "Cited source missing from the session",
            "url": url, "used_for": roles, "reason": "; ".join(reason),
            "coverage": coverage, "fetch_state": fetch_state,
            "observed_at": receipt.observed_at if receipt else None,
            "pinned_revision": pinned_revision,
            "sha256": doc.sha256 if doc else None,
            "issues": sorted(issues),
        })
    return rows, characters


def build_review_view(session, *, previous_session=None, usage=None,
                      include_source_details=False, origin="HOST_SESSION"):
    """Project the existing handoff without changing evidence or granting trust.

    The default view omits source titles, URLs, quotes, source timestamps and
    source hashes. It still contains the goal and proposed statements: it is
    NOT a redacted/public export. Detailed evidence requires a host-authorized
    same-audience call. The boolean does not authenticate a recipient.

    A previous_session is an already-authorized earlier research record, not a
    prior decision/approval. No approval field is accepted or carried forward.
    """
    if type(include_source_details) is not bool:
        raise ValueError("Invalid source-detail option")
    if not isinstance(origin, str) or origin not in ORIGINS:
        raise ValueError("Invalid observation origin")
    current = _validate_session(session)
    previous_handoff = None
    if previous_session is not None:
        previous = _validate_session(previous_session)
        previous_handoff = build_handoff(previous.payload, previous.goal,
                                        previous.claims, previous.gathered.documents)
    handoff = build_handoff(
        current.payload, current.goal, current.claims, current.gathered.documents,
        previous_binding=(previous_handoff["review_binding"]["sha256"]
                          if previous_handoff else None),
    )
    old = {claim["id"]: claim["statement"]
           for claim in previous_handoff["claim_details"]} if previous_handoff else {}
    proposals = []
    for claim in handoff["claim_details"]:
        original = old.get(claim["id"])
        proposals.append({
            "id": claim["id"], "statement": claim["statement"],
            "previous_statement": original,
            "change_state": ("NEW" if original is None else
                             "UNCHANGED" if original == claim["statement"] else "CHANGED"),
            "verdict": claim["verdict"], "issues": list(claim["issues"]),
            "evidence_state": ("MATCHED_SOURCE_TEXT" if claim["structural_verdict"] ==
                               "REVIEW_REQUIRED" else "HOLD"),
            "owner_confirmation": "NOT_VERIFIED",
            "evidence": claim["evidence"] if include_source_details else [],
        })
    sources, characters = _context_sources(current, handoff)
    return {
        "schema": SCHEMA_VERSION, "title": "What WIT used",
        "goal": current.goal, "verdict": handoff["verdict"], "origin": origin,
        "source_details_visible": include_source_details,
        "review_binding": dict(handoff["review_binding"]),
        "context": {
            "scope": (
                "Inputs to this research handoff's ranking, findings and evidence checks. "
                "This does not establish what a separate AI model received."
            ),
            "sources": sources if include_source_details else [],
            "source_count": len(sources), "usage": _usage_view(usage, characters),
            "limitations": [
                "Observation time is retrieval time, not the source's publication date.",
                "A pinned revision identifies exact content; it is not proof of the latest version.",
                "Source text and snippets remain untrusted data.",
            ],
        },
        "memory_review": {
            "owner_confirmation": "NOT_VERIFIED", "storage": "READ_ONLY_PROJECTION",
            "proposals": proposals,
            "limitations": [
                "These are existing research claims displayed as possible memory proposals.",
                "A previous statement is an earlier proposal, not an owner decision.",
                "No owner confirmation is inferred or accepted by this view.",
                "Editing, rejection and adoption belong to the existing owning application.",
            ],
        },
        # Preserve the existing privacy/default presentation boundary verbatim.
        "quick_view": handoff["quick_view"],
        "limitations": [
            "No memory is written and no action is authorized by this report.",
            "Exact source/quote checks do not establish factual truth or semantic support.",
            "This report may contain private statements; it is not a public-safe export.",
        ],
    }
