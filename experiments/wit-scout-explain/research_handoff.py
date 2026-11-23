"""Readable source-first research handoff using existing WIT Scout modules.

Source search and retrieval remain host-owned. Neither a snippet nor a matched
quote is a completed task or an independent factual endorsement.
"""
from __future__ import annotations

import hashlib
import json
import re

from claim_review import _documents_index, verify_claims
from semantic_guard import review_meaning
from provider_adapter import ingest
from scout import canonical_url, rank

MAX_FINDINGS = 20
_SHA256 = re.compile(r"[a-f0-9]{64}\Z")
_PINNED_GITHUB = re.compile(
    r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/blob/"
    r"[a-f0-9]{40}/[A-Za-z0-9_./-]+\Z"
)
_LIMITATIONS = (
    "Matched source text still requires review of what it means.",
    "Runtime behavior has not been tested by this handoff.",
    "A source or review binding does not authorize an action or prove completion.",
)


def _review_binding(goal, review, doc_index, previous):
    if previous is not None and (not isinstance(previous, str) or
                                 not _SHA256.fullmatch(previous)):
        raise ValueError("previous_binding must be a SHA-256 fingerprint")
    # The existing claim bundle binds statements, quotes and source text. Add
    # the question and actual navigation identities so changed targets cannot
    # silently reuse a review. Presentation depth is intentionally excluded.
    material = {
        "schema": "wit.research-handoff-binding.v1",
        "goal": goal,
        "claim_bundle_sha256": review.bundle_sha256,
        "sources": [
            {"source_url": source, "final_url": canonical_url(doc.canonical_url),
             "sha256": doc.sha256, "retrieval_method": doc.retrieval_method}
            for source, doc in sorted(doc_index.items())
        ],
    }
    digest = hashlib.sha256(json.dumps(
        material, ensure_ascii=False, sort_keys=True,
        separators=(",", ":")).encode("utf-8")).hexdigest()
    return {
        "schema": material["schema"], "sha256": digest,
        "previous_sha256": previous,
        "state": ("NEW" if previous is None else
                  "UNCHANGED" if previous == digest else "INPUTS_CHANGED"),
        # Even identical inputs do not import an old factual/action verdict.
        "prior_verdict_carried_forward": False,
    }


def _evidence_detail(entry, doc_index):
    source = canonical_url(entry["source_url"])
    doc = doc_index.get(source)
    quote = entry["quote"]
    navigation = {"kind": "UNAVAILABLE", "url": None,
                  "start_line": None, "end_line": None,
                  "start_offset": None, "end_offset": None}
    if doc is None:
        state = "SOURCE_NOT_HOST_FETCHED"
    elif doc.sha256 != entry["sha256"]:
        state = "SOURCE_HASH_MISMATCH"
    elif quote not in doc.text:
        state = "QUOTE_NOT_FOUND_VERBATIM"
    else:
        state = "MATCHED_HOST_TEXT"
        target = canonical_url(doc.canonical_url)
        start = doc.text.find(quote)
        end = start + len(quote)
        navigation.update(kind="SOURCE_PAGE_WITH_QUOTE", url=target)
        if doc.text.find(quote, start + 1) >= 0:
            # A matching string in several places is not a unique locator.
            navigation["kind"] = "AMBIGUOUS_QUOTE"
        else:
            # These offsets always refer to the retained UTF-8-decoded text,
            # not a PDF page, audio timestamp, DOM position or byte offset.
            navigation.update(start_offset=start, end_offset=end)
            if (doc.retrieval_method == "github_connector" and
                    source == target and _PINNED_GITHUB.fullmatch(target) and
                    not any(part in (".", "..") for part in target.split("/"))):
                # Only the existing exact GitHub file adapter guarantees that
                # retained text lines correspond to a pinned source file.
                first = doc.text.count("\n", 0, start) + 1
                last = doc.text.count("\n", 0, end - 1) + 1
                anchor = f"#L{first}" + (f"-L{last}" if last != first else "")
                # GitHub renders Markdown by default; plain=1 selects source
                # view so its #L anchors refer to the inspected file lines.
                navigation.update(kind="PINNED_GITHUB_LINES", url=target + "?plain=1" + anchor,
                                  start_line=first, end_line=last)
    return {
        "source_url": source,
        "final_url": canonical_url(doc.canonical_url) if doc else None,
        "sha256": entry["sha256"],
        "observed_sha256": doc.sha256 if doc else None,
        # This remains the supplied citation unless state is MATCHED_HOST_TEXT.
        "quote": quote, "evidence_state": state, "navigation": navigation,
    }


def build_handoff(payload, goal, claims, documents, level="practical", *,
                  previous_binding=None):
    """Build bounded presentation data; never inherit a prior approval.

    A caller retaining earlier reviews should supply the previous handoff's
    review_binding.sha256. Any input change conservatively requires re-review;
    this comparison does not decide whether a wording change altered meaning.
    All titles, statements and excerpts remain untrusted text for the renderer.
    """
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
            "description": (doc.text[:120 if level == "simple" else 320].strip() if doc
                            else (item.title if level == "simple" else item.excerpt)),
            "description_origin": "HOST_FETCHED_TEXT" if doc else "PROVIDER_SNIPPET",
        }
        if level == "technical" and doc:
            found["sha256"] = doc.sha256
            found["retrieval_method"] = doc.retrieval_method
        findings.append(found)
    review = verify_claims(claims, documents)
    interpretation = review_meaning(claims, documents)
    binding = _review_binding(goal, review, doc_index, previous_binding)
    details = []
    for claim, structural, semantic in zip(claims, review.results, interpretation):
        issues = set(structural["issues"]) | set(semantic.issues)
        if binding["state"] == "INPUTS_CHANGED":
            issues.add("INPUTS_CHANGED_REVIEW_REQUIRED")
        details.append({
            "id": claim["id"], "statement": claim["statement"],
            "verdict": "HOLD" if issues else "REVIEW_REQUIRED",
            "issues": sorted(issues),
            "structural_verdict": structural["verdict"],
            "semantic_verdict": semantic.verdict,
            "evidence": [_evidence_detail(entry, doc_index)
                         for entry in claim["evidence"]],
        })
    overall_verdict = ("HOLD" if any(item["verdict"] == "HOLD" for item in details)
                       else "REVIEW_REQUIRED")
    note = {
        "simple": "These are leads. A matched quote still needs someone to check what it means.",
        "practical": "Check the original sources, then review meaning and authorizations before adoption.",
        "technical": "Host fetch attestation is caller-owned. Verbatim quote matching is not a semantic or execution oracle.",
    }[level]
    if binding["state"] == "INPUTS_CHANGED":
        note = "The question, claim or evidence changed. Review this version before using an earlier decision."
    return {
        "schema": "wit.research-handoff.v1",
        "goal": goal,
        "level": level,
        "verdict": overall_verdict,
        "findings": findings,
        "omitted_findings": max(0, len(ranked) - MAX_FINDINGS),
        "claim_review": review.as_dict(),
        "review_binding": binding,
        "claim_details": details,
        "quick_view": {
            "verdict": overall_verdict,
            "claims": [{key: item[key] for key in ("id", "statement", "verdict", "issues")}
                       for item in details],
            "limitations": list(_LIMITATIONS),
            "next_step": note,
        },
        "limitations": list(_LIMITATIONS),
        "semantic_precheck": [
            {"claim_id": item.claim_id, "verdict": item.verdict,
             "issues": list(item.issues)} for item in interpretation],
        "independent_semantic_review_completed": False,
        "next_step": note,
    }
