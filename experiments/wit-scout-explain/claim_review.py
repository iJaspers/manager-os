"""Deterministic evidence check for WIT research handoffs.

This is NOT a semantic truth judge or independent AI reviewer. Callers must
supply trusted-host VerifiedDocument objects; the module never fetches URLs,
reads credentials, makes external calls, executes source text, or grants approval.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from evidence_gate import VerifiedDocument
from scout import canonical_url

MAX_CLAIMS = 32
MAX_EVIDENCE_PER_CLAIM = 8
MAX_STATEMENT = 2000
MAX_QUOTE = 2000
MAX_DOCUMENTS = 100
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}\Z")
_SHA = re.compile(r"[a-f0-9]{64}\Z")


@dataclass(frozen=True)
class ReviewOutcome:
    verdict: str
    source_count: int
    results: tuple[dict, ...]
    bundle_sha256: str
    limitations: tuple[str, ...] = (
        "Exact quote matches do not establish semantic support or factual truth.",
        "Completed actions require independent provider or filesystem receipts.",
        "Host attestation and retrieval security remain the trusted caller's duty.",
    )

    def as_dict(self):
        return {
            "schema": "wit.research-claim-review.v1",
            "verdict": self.verdict,
            "source_count": self.source_count,
            "results": [dict(result) for result in self.results],
            "bundle_sha256": self.bundle_sha256,
            "limitations": list(self.limitations),
        }


def _documents_index(documents):
    if not isinstance(documents, (tuple, list)) or len(documents) > MAX_DOCUMENTS:
        raise ValueError("invalid document collection")
    index = {}
    for doc in documents:
        if not isinstance(doc, VerifiedDocument):
            raise ValueError("only verified host document objects accepted")
        source = canonical_url(doc.source.url)
        final = canonical_url(doc.canonical_url)
        if not source or not final:
            raise ValueError("invalid document source URL")
        if not isinstance(doc.text, str) or not doc.text.strip():
            raise ValueError("empty document")
        # Treat a mutated or forged digest as a broken evidence bundle.
        if not isinstance(doc.sha256, str) or not _SHA.fullmatch(doc.sha256):
            raise ValueError("invalid document hash")
        if hashlib.sha256(doc.text.encode("utf-8")).hexdigest() != doc.sha256:
            raise ValueError("document hash does not match content")
        if source in index:
            raise ValueError("ambiguous duplicate source document")
        index[source] = doc
    return index


def verify_claims(claims, documents):
    """Check source links and verbatim quotes; fail closed on action claims.

    A REVIEW_REQUIRED result means structural evidence matched, not that the
    claim is true, the action happened, or anyone approved a release.
    """
    index = _documents_index(documents)
    if not isinstance(claims, (list, tuple)) or not 1 <= len(claims) <= MAX_CLAIMS:
        raise ValueError("claims must be a nonempty bounded list")
    ids, results, normalized = set(), [], []
    for claim in claims:
        if not isinstance(claim, Mapping) or set(claim) != {"id", "statement", "evidence", "completed_action"}:
            raise ValueError("claim must use the exact v1 schema")
        ident, statement = claim["id"], claim["statement"]
        if not isinstance(ident, str) or not _ID.fullmatch(ident) or ident in ids:
            raise ValueError("invalid or duplicate claim ID")
        ids.add(ident)
        if not isinstance(statement, str) or not statement.strip() or len(statement) > MAX_STATEMENT:
            raise ValueError("invalid claim statement")
        if type(claim["completed_action"]) is not bool:
            raise ValueError("completed_action must be a boolean")
        evidence = claim["evidence"]
        if not isinstance(evidence, (list, tuple)) or len(evidence) > MAX_EVIDENCE_PER_CLAIM:
            raise ValueError("invalid evidence array")
        issues, matches, source_links, normalized_evidence = [], 0, set(), []
        if not evidence:
            issues.append("NO_EVIDENCE")
        for entry in evidence:
            if not isinstance(entry, Mapping) or set(entry) != {"source_url", "quote", "sha256"}:
                raise ValueError("evidence must use the exact v1 schema")
            src, quote, digest = entry["source_url"], entry["quote"], entry["sha256"]
            if not isinstance(src, str) or len(src) > 2048 or not canonical_url(src):
                raise ValueError("invalid source_url")
            if not isinstance(quote, str) or not quote or len(quote) > MAX_QUOTE:
                raise ValueError("invalid exact quote")
            if not isinstance(digest, str) or not _SHA.fullmatch(digest):
                raise ValueError("invalid evidence digest")
            canon = canonical_url(src)
            doc = index.get(canon)
            if doc is None:
                issues.append("SOURCE_NOT_HOST_FETCHED")
            elif digest != doc.sha256:
                issues.append("SOURCE_HASH_MISMATCH")
            elif quote not in doc.text:
                issues.append("QUOTE_NOT_FOUND_VERBATIM")
            else:
                matches += 1
                source_links.add(canon)
            normalized_evidence.append({"source_url": canon, "quote": quote, "sha256": digest})
        if claim["completed_action"]:
            # A fetched web page cannot prove a tool or human actually did work.
            issues.append("INDEPENDENT_ACTION_RECEIPT_REQUIRED")
        unique_issues = sorted(set(issues))
        results.append({
            "id": ident,
            "verdict": "HOLD" if unique_issues else "REVIEW_REQUIRED",
            "matched_quotes": matches,
            "source_links": len(source_links),
            "issues": unique_issues,
        })
        normalized.append({
            "id": ident,
            "statement": statement,
            "completed_action": claim["completed_action"],
            "evidence": normalized_evidence,
        })
    verdict = "HOLD" if any(result["verdict"] == "HOLD" for result in results) else "REVIEW_REQUIRED"
    # This fingerprint can detect mutation of this supplied bundle. It does not
    # authenticate the original source or sign an external provider receipt.
    contents = json.dumps({
        "claims": normalized,
        "source_hashes": sorted((url, d.sha256) for url, d in index.items()),
        "results": results,
    }, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(contents.encode("utf-8")).hexdigest()
    return ReviewOutcome(verdict, len(index), tuple(results), digest)
