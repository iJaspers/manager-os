"""Strict read-only GitHub connector binding for WIT Scout.

The network-facing GitHub connector is supplied by a trusted host, not
implemented here. Only allowlisted immutable commit/file targets may be read.
Returned Git blob SHA-1 is checked against exact UTF-8 content. This catches
content/metadata mismatch; it does not cryptographically authenticate a tool.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import re
from urllib.parse import quote

from scout import canonical_url
from trusted_host_bridge import HostRead

_COMMIT = re.compile(r"[a-f0-9]{40}\Z")
_OWNER_REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
_PATH = re.compile(r"[A-Za-z0-9_./-]+\Z")
_MAX_BYTES = 200_000


@dataclass(frozen=True)
class GitHubTarget:
    repository: str
    path: str
    commit: str

    @property
    def url(self):
        return f"https://github.com/{self.repository}/blob/{self.commit}/{quote(self.path, safe='/')}"

    def __post_init__(self):
        if not _OWNER_REPO.fullmatch(self.repository) or not _PATH.fullmatch(self.path):
            raise ValueError("invalid GitHub target")
        if any(part in ("", ".", "..") for part in self.path.split('/')):
            raise ValueError("invalid target path")
        if not _COMMIT.fullmatch(self.commit):
            raise ValueError("pin source to a full immutable commit SHA")


def github_blob_sha(text: str) -> str:
    if not isinstance(text, str):
        raise ValueError("expected decoded UTF-8 source text")
    raw = text.encode('utf-8')
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def _connector_data(response):
    """Normalize one explicit connector payload; presentation text is not data.

    The host may return a direct payload, legacy result wrapper or current MCP
    structuredContent wrapper. Reject competing locations instead of choosing
    whichever happens to contain plausible source bytes. No recursive unwrap.
    """
    def check_error(value):
        if 'isError' in value and value['isError'] is not False:
            raise ValueError("GitHub connector error or invalid status")

    if not isinstance(response, dict):
        raise ValueError("invalid connector response")
    check_error(response)
    wrappers = [key for key in ('result', 'structuredContent') if key in response]
    if len(wrappers) > 1:
        raise ValueError("ambiguous connector response")
    result = response
    if wrappers:
        if any(key in response for key in ('sha', 'display_url', 'encoding')) or (
                'content' in response and not isinstance(response['content'], list)):
            raise ValueError("conflicting connector payload locations")
        result = response[wrappers[0]]
        if not isinstance(result, dict) or any(key in result for key in ('result', 'structuredContent')):
            raise ValueError("invalid or nested connector result")
        check_error(result)
    if 'encoding' in result and result['encoding'] != 'utf-8':
        raise ValueError("expected decoded UTF-8 GitHub source")
    return result


class GitHubConnectorAdapter:
    """Bind existing host mcp__GitHub__fetch_file to the Scout HostRead API.

    fetch_file must be a trusted host-owned callable accepting exactly
    repository_full_name, path and ref, returning the GitHub connector's
    payload directly or in a result/structuredContent wrapper. Do NOT pass an
    untrusted callable or let web text select
    allowlist entries. This adapter performs no network access itself.
    """
    def __init__(self, fetch_file, targets: tuple[GitHubTarget, ...], clock=None):
        if not callable(fetch_file) or not isinstance(targets, tuple) or not targets:
            raise ValueError("trusted connector and pinned targets required")
        if len(targets) > 6 or any(not isinstance(t, GitHubTarget) for t in targets):
            raise ValueError("invalid target allowlist")
        self._fetch_file = fetch_file
        self._targets = {canonical_url(t.url): t for t in targets}
        if len(self._targets) != len(targets):
            raise ValueError("duplicate targets")
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def __call__(self, source):
        key = canonical_url(getattr(source, 'url', None))
        target = self._targets.get(key)
        if not target:
            raise PermissionError("source not on pinned allowlist")
        response = self._fetch_file(repository_full_name=target.repository,
                                    path=target.path, ref=target.commit)
        result = _connector_data(response)
        value = result.get('content')
        digest = result.get('sha')
        display = result.get('display_url')
        if (not isinstance(value, str) or len(value) > _MAX_BYTES or not value.strip()
                or len(value.encode('utf-8')) > _MAX_BYTES):
            raise ValueError("invalid GitHub content")
        if not isinstance(digest, str) or not _COMMIT.fullmatch(digest):
            raise ValueError("missing GitHub blob checksum")
        if github_blob_sha(value) != digest:
            raise ValueError("GitHub blob mismatch")
        if 'display_url' in result and display != target.url:
            raise ValueError("GitHub returned different file/ref")
        observed = self._clock()
        if not isinstance(observed, datetime) or observed.tzinfo is None or observed.utcoffset() is None:
            raise ValueError("host must provide timezone-aware observation time")
        return HostRead(requested_url=target.url, final_url=target.url, text=value,
                        retrieval_method='github_connector',
                        provider_ref=f"github-blob:{digest}",
                        observed_at=observed.isoformat())
