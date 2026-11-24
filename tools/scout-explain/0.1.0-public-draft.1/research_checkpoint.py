"""Complete, bounded local recovery for the existing WIT research handoff.

The host must retain the returned checkpoint digest outside the checkpoint and
provide that digest, the expected code revision and its approved source URLs on
restore. Loading does not fetch anything or perform a new source attestation.
These checks detect changed bytes and incompatible sessions; they are not a
signature, protection against a compromised host, or proof a source is true.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import hmac
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from claim_review import verify_claims
from github_connector_adapter import GitHubTarget, github_blob_sha
from provider_adapter import ingest, MAX_RESULTS, MAX_FIELD
from scout import Evidence, canonical_url, rank, _atomic_write_checkpoint
from trusted_host_bridge import (
    Gathered, HostRead, MAX_FETCH, _checked_read,
)

SCHEMA = 'wit.research-checkpoint.v1'
MAX_CHECKPOINT_BYTES = 4_000_000
MAX_DOCUMENT_BYTES = 200_000
_DIGEST = re.compile(r'[a-f0-9]{64}\Z')
_FAILURE = re.compile(r'[A-Za-z][A-Za-z0-9_]{0,99}\Z')


@dataclass(frozen=True)
class ResearchSession:
    payload: dict
    goal: str
    claims: tuple[dict, ...]
    gathered: Gathered
    code_revision: str
    approved_urls: tuple[str, ...]


def _fields(value, keys, label):
    if type(value) is not dict or set(value) != set(keys):
        raise ValueError(f'invalid {label} schema')


def _list(value, maximum, label):
    if type(value) is not list or len(value) > maximum:
        raise ValueError(f'invalid {label} collection')
    return value


def _revision(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise ValueError('expected bounded code revision')
    return value


def _url(value):
    if not isinstance(value, str) or len(value) > 2048:
        raise ValueError('invalid source URL')
    result = canonical_url(value)
    if not result:
        raise ValueError('invalid source URL')
    return result


def _approved(values):
    # Up to one requested and one explicitly approved final URL per source.
    if not isinstance(values, (tuple, list)) or len(values) > 2 * MAX_FETCH:
        raise ValueError('invalid source allowlist')
    canonical = tuple(sorted(_url(value) for value in values))
    if len(canonical) != len(set(canonical)):
        raise ValueError('duplicate approved source')
    return canonical


def _evidence(value):
    _fields(value, ('title', 'url', 'excerpt', 'fetched', 'official'), 'evidence')
    if any(not isinstance(value[key], str) or len(value[key]) > MAX_FIELD
           for key in ('title', 'url', 'excerpt')):
        raise ValueError('invalid evidence field')
    if any(type(value[key]) is not bool for key in ('fetched', 'official')):
        raise ValueError('invalid evidence flags')
    _url(value['url'])
    return Evidence(**value)


def _github_receipt(receipt, text):
    if receipt.retrieval_method != 'github_connector':
        return
    parsed = urlsplit(receipt.requested_url)
    parts = parsed.path.split('/')
    if (parsed.scheme != 'https' or parsed.netloc != 'github.com' or
            parsed.query or parsed.fragment or len(parts) < 6 or parts[3] != 'blob'):
        raise ValueError('GitHub receipt must identify an immutable file')
    target = GitHubTarget(f'{parts[1]}/{parts[2]}', '/'.join(parts[5:]), parts[4])
    if (target.url != receipt.requested_url or
            receipt.final_url != receipt.requested_url or
            receipt.provider_ref != f'github-blob:{github_blob_sha(text)}'):
        raise ValueError('GitHub receipt does not match source bytes')


def _restore(data, expected_code_revision, approved_urls):
    _fields(data, ('schema', 'code_revision', 'approved_urls', 'payload',
                   'goal', 'claims', 'gathered'), 'checkpoint')
    if data['schema'] != SCHEMA:
        raise ValueError('unsupported research checkpoint')
    if _revision(data['code_revision']) != _revision(expected_code_revision):
        raise ValueError('research code revision changed')
    allowed = _approved(approved_urls)
    if _approved(data['approved_urls']) != allowed:
        raise ValueError('research source allowlist changed')
    goal = data['goal']
    if not isinstance(goal, str) or not goal.strip() or len(goal) > 500:
        raise ValueError('invalid goal')
    payload = data['payload']
    _fields(payload, ('results',), 'provider payload')
    for row in _list(payload['results'], MAX_RESULTS, 'provider results'):
        # Persist the inputs used by ingest, not arbitrary provider metadata.
        _fields(row, ('title', 'url', 'excerpt'), 'provider result')
    expected_ranked = tuple(rank(ingest(payload), goal))

    saved = data['gathered']
    _fields(saved, ('ranked', 'documents', 'receipts', 'failures',
                    'evidence_state'), 'gathered')
    if saved['evidence_state'] != 'HOST_READ_REVIEW_REQUIRED':
        raise ValueError('checkpoint cannot promote evidence state')
    ranked = tuple(_evidence(item) for item in
                   _list(saved['ranked'], MAX_RESULTS, 'ranked evidence'))
    if ranked != expected_ranked:
        raise ValueError('ranked evidence does not match original inputs')
    sources = {canonical_url(item.url): item for item in ranked}
    raw_docs = _list(saved['documents'], MAX_FETCH, 'documents')
    raw_receipts = _list(saved['receipts'], MAX_FETCH, 'receipts')
    if len(raw_docs) != len(raw_receipts):
        raise ValueError('each document requires its receipt')
    documents, receipts, completed = [], [], set()
    for raw_doc, raw_receipt in zip(raw_docs, raw_receipts):
        _fields(raw_doc, ('source', 'canonical_url', 'sha256', 'text',
                          'retrieval_method'), 'document')
        _fields(raw_receipt, ('requested_url', 'final_url', 'retrieval_method',
                              'provider_ref', 'observed_at', 'sha256'), 'receipt')
        if any(not isinstance(value, str) for value in raw_receipt.values()):
            raise ValueError('invalid receipt field')
        _url(raw_receipt['requested_url'])
        _url(raw_receipt['final_url'])
        source = _evidence(raw_doc['source'])
        key = canonical_url(source.url)
        if (key in completed or key not in allowed or
                source != sources.get(key) or
                _url(raw_doc['canonical_url']) not in allowed):
            raise ValueError('document source is duplicate, changed or unapproved')
        text = raw_doc['text']
        if (not isinstance(text, str) or not text.strip() or
                len(text.encode('utf-8')) > MAX_DOCUMENT_BYTES):
            raise ValueError('invalid saved document text')
        doc, receipt = _checked_read(source, HostRead(**{
            key: value for key, value in raw_receipt.items() if key != 'sha256'
        }, text=text))
        if asdict(doc) != raw_doc or asdict(receipt) != raw_receipt:
            raise ValueError('saved document and receipt disagree')
        _github_receipt(receipt, text)
        documents.append(doc)
        receipts.append(receipt)
        completed.add(key)

    failures, failed = [], set()
    for failure in _list(saved['failures'], MAX_FETCH, 'failures'):
        _fields(failure, ('url', 'reason'), 'failure')
        key = _url(failure['url'])
        if (failure['url'] != key or key not in sources or key in completed or
                key in failed or not isinstance(failure['reason'], str) or
                not _FAILURE.fullmatch(failure['reason'])):
            raise ValueError('invalid or conflicting failure record')
        failures.append(dict(failure))
        failed.add(key)
    attempted = len(completed) + len(failed)
    if attempted > MAX_FETCH or completed | failed != {
            canonical_url(item.url) for item in ranked[:attempted]}:
        raise ValueError('retrieval outcomes do not match the bounded source plan')
    gathered = Gathered(ranked, tuple(documents), tuple(receipts), tuple(failures))
    claims = data['claims']
    # A valid HOLD is preserved, not rejected or upgraded to factual approval.
    verify_claims(claims, gathered.documents)
    return ResearchSession(payload, goal, tuple(claims), gathered,
                           data['code_revision'], allowed)


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON field')
        result[key] = value
    return result


def _decode(raw):
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=_unique_object,
                          parse_constant=lambda value: (_ for _ in ()).throw(
                              ValueError('invalid JSON constant')))
    except (UnicodeError, RecursionError) as exc:
        raise ValueError('invalid checkpoint encoding or nesting') from exc


def save_research_checkpoint(path, *, payload, goal, claims, gathered,
                             code_revision, approved_urls):
    """Validate then atomically save; return the exact-byte digest for the host.

    The host must supply its already-trusted Gathered result, not objects made
    from arbitrary source JSON. No factual or execution approval is persisted.
    """
    if not isinstance(gathered, Gathered):
        raise ValueError('existing trusted host Gathered result required')
    data = {'schema': SCHEMA, 'code_revision': code_revision,
            'approved_urls': _approved(approved_urls), 'payload': payload,
            'goal': goal, 'claims': claims, 'gathered': asdict(gathered)}
    try:
        raw = json.dumps(data, ensure_ascii=False, sort_keys=True,
                         indent=2, allow_nan=False).encode('utf-8')
    except (TypeError, UnicodeError, RecursionError) as exc:
        raise ValueError('checkpoint must be bounded JSON data') from exc
    if len(raw) > MAX_CHECKPOINT_BYTES:
        raise ValueError('checkpoint exceeds byte budget')
    _restore(_decode(raw), code_revision, approved_urls)
    _atomic_write_checkpoint(path, raw)
    return hashlib.sha256(raw).hexdigest()


def load_research_checkpoint(path, *, expected_sha256, expected_code_revision,
                             approved_urls):
    """Reopen a host-anchored checkpoint without any network or callback.

    Never take expected_sha256 or approved_urls from the checkpoint itself.
    A changed revision requires an explicit migration/re-run, not silent reuse.
    """
    if not isinstance(expected_sha256, str) or not _DIGEST.fullmatch(expected_sha256):
        raise ValueError('caller-held checkpoint SHA-256 required')
    with Path(path).open('rb') as source:
        raw = source.read(MAX_CHECKPOINT_BYTES + 1)
    if len(raw) > MAX_CHECKPOINT_BYTES:
        raise ValueError('checkpoint exceeds byte budget')
    if not hmac.compare_digest(hashlib.sha256(raw).hexdigest(), expected_sha256):
        raise ValueError('checkpoint bytes changed')
    return _restore(_decode(raw), expected_code_revision, approved_urls)
