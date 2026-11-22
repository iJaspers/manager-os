"""WIT Scout host bridge: bounded read-only retrieval through a trusted caller.

This module makes NO network calls. The caller supplies a trusted, read-only
fetch callback implementing actual host/plugin/web tools. Do not construct that
callback from user or search-result input: the callback owns security checks,
redirect verification, auth and provenance. \`host_verified\` is not a signature.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlsplit
from collections.abc import Callable

from evidence_gate import VerifiedDocument, verify_host_fetch
from provider_adapter import ingest
from scout import Evidence, canonical_url, rank

MAX_FETCH = 6
MAX_REF = 200
MAX_FAILURE = 100
ALLOWED_METHODS = frozenset({'github_connector', 'trusted_browser', 'trusted_search_fetch'})


@dataclass(frozen=True)
class HostRead:
    """From trusted host code, not from an untrusted JSON payload."""
    requested_url: str
    final_url: str
    text: str
    retrieval_method: str
    provider_ref: str
    observed_at: str


@dataclass(frozen=True)
class FetchReceipt:
    requested_url: str
    final_url: str
    retrieval_method: str
    provider_ref: str
    observed_at: str
    sha256: str


@dataclass(frozen=True)
class Gathered:
    ranked: tuple[Evidence, ...]
    documents: tuple[VerifiedDocument, ...]
    receipts: tuple[FetchReceipt, ...]
    failures: tuple[dict, ...]
    # An experimental host fetch is a sourced text handoff, not semantic review.
    evidence_state: str = 'HOST_READ_REVIEW_REQUIRED'


def _hostname(url):
    p = urlsplit(url)
    return (p.hostname or '').lower().removeprefix('www.').rstrip('.')


def _checked_read(source: Evidence, read: HostRead):
    if not isinstance(read, HostRead):
        raise ValueError('host callback did not return a HostRead')
    if canonical_url(read.requested_url) != canonical_url(source.url):
        raise ValueError('host response does not match requested source')
    if not canonical_url(read.final_url):
        raise ValueError('unsafe final URL')
    # A redirected host must be approved by the host before it reaches this
    # bridge. Default fail-closed avoids naive cross-site evidence swaps.
    if _hostname(source.url) != _hostname(read.final_url):
        raise ValueError('unexpected cross-host redirect')
    if read.retrieval_method not in ALLOWED_METHODS:
        raise ValueError('unrecognized host retrieval method')
    if not isinstance(read.provider_ref, str) or not read.provider_ref.strip() or len(read.provider_ref) > MAX_REF:
        raise ValueError('missing provider reference')
    if not isinstance(read.observed_at, str) or len(read.observed_at) > 40:
        raise ValueError('invalid observation time')
    try:
        observed = datetime.fromisoformat(read.observed_at.replace('Z', '+00:00'))
    except ValueError as exc:
        raise ValueError('invalid observation time') from exc
    if observed.tzinfo is None or observed.utcoffset() is None:
        raise ValueError('observation time must contain timezone')
    # Only trusted host integration code may call this function with its own
    # trusted response. Do not take \`host_verified\` from JSON or web content.
    doc = verify_host_fetch(source, final_url=read.final_url, text=read.text,
                            retrieval_method=read.retrieval_method, host_verified=True)
    receipt = FetchReceipt(
        requested_url=canonical_url(source.url), final_url=canonical_url(read.final_url),
        retrieval_method=read.retrieval_method, provider_ref=read.provider_ref,
        observed_at=observed.isoformat(), sha256=doc.sha256)
    return doc, receipt


def gather(payload, goal, fetch_from_trusted_host: Callable[[Evidence], HostRead], max_fetch=MAX_FETCH):
    """Fetch only bounded ranked results; preserve failures instead of making them up.

    The host callback must enforce public-IP DNS, redirect/IP rechecks,
    timeouts, content/mime limits, and tool permissions before returning text.
    """
    if not isinstance(goal, str) or not goal.strip() or len(goal) > 500:
        raise ValueError('invalid goal')
    if type(max_fetch) is not int or not 0 <= max_fetch <= MAX_FETCH:
        raise ValueError('invalid max_fetch')
    if not callable(fetch_from_trusted_host):
        raise ValueError('trusted host fetch callback required')
    items = rank(ingest(payload), goal)
    documents, receipts, failures = [], [], []
    for source in items[:max_fetch]:
        try:
            read = fetch_from_trusted_host(source)
            doc, receipt = _checked_read(source, read)
        except (ValueError, PermissionError, TypeError, OSError, TimeoutError) as exc:
            # No arbitrary exception message: it may include credentials,
            # source contents, or user-private endpoint details.
            failures.append({'url': canonical_url(source.url), 'reason': type(exc).__name__[:MAX_FAILURE]})
            continue
        documents.append(doc)
        receipts.append(receipt)
    return Gathered(tuple(items), tuple(documents), tuple(receipts), tuple(failures))
