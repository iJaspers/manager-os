"""Reproduce a host-orchestrated live acquisition and abrupt local restart.

The connected host reads exact pinned files with github_host_runtime.mjs and
transfers the *actual complete MCP returns* as JSON, supplying the transfer's
Git blob digest out of band. This CLI validates that transfer with the Python
adapter, persists the existing research state, and deliberately kills only its
own acquisition process. Resume uses a caller-held checkpoint receipt and makes
no network requests. This is a finite acceptance exercise, not a deployed
autonomous connector or a source-authenticity signature.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import signal
import socket

from github_connector_adapter import GitHubConnectorAdapter, GitHubTarget
from research_checkpoint import load_research_checkpoint, save_research_checkpoint
from research_handoff import build_handoff
from semantic_guard import review_meaning, semantic_review_request
from trusted_host_bridge import gather


def _json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n', encoding='utf-8')


def code_fingerprint():
    root = Path(__file__).resolve().parent
    files = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(root.iterdir())
             if p.suffix in {'.py', '.mjs'} and not p.name.startswith('test_')}
    digest = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()
    return 'sha256:' + digest, files


def _no_network(*args, **kwargs):
    raise AssertionError('This local runner must never access the network')


def acquire(args):
    raw = args.transport.read_bytes()
    transfer_blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    if transfer_blob != args.expected_transport_blob:
        raise ValueError('Host transfer bytes changed or were truncated')
    data = json.loads(raw)
    if data.get('schema') != 'wit.connected-host-transfer.v1':
        raise ValueError('Unsupported host transfer')
    rows = data.get('records')
    if not isinstance(rows, list) or not 1 <= len(rows) <= 6:
        raise ValueError('Invalid bounded host records')
    targets = tuple(GitHubTarget(r['target']['repo'], r['target']['path'], r['target']['commit']) for r in rows)
    approved_urls = [t.url for t in targets]
    if len(set(approved_urls)) != len(rows):
        raise ValueError('Duplicate host record')
    table = {(t.repository, t.path, t.commit): row for t, row in zip(targets, rows)}
    state = {'validations': 0, 'observed_at': data['observed_at']}

    def received_file(*, repository_full_name, path, ref):
        row = table[(repository_full_name, path, ref)]
        state['validations'] += 1
        state['observed_at'] = row.get('js_receipt', {}).get('observed_at', data['observed_at'])
        return row['reply']

    def observed_clock():
        return datetime.fromisoformat(state['observed_at'].replace('Z', '+00:00'))

    adapter = GitHubConnectorAdapter(received_file, targets, clock=observed_clock)
    payload = {'results': [{'title': r['target']['title'], 'url': t.url,
                            'excerpt': r['target']['excerpt']}
                           for t, r in zip(targets, rows)]}
    goal = 'Review verification limits and API-key requirements from the user-supplied workflow repositories'
    gathered = gather(payload, goal, adapter, max_fetch=len(targets))
    source_docs = {d.source.url: d for d in gathered.documents}
    by_file = {(t.repository, t.path): t for t in targets}
    specs = [
        ('verification_limit', 'Neeeophytee/awesome-ai-workflows',
         'The README says its AI-generated steps are never claimed as machine-checked.',
         'the AI-generated step of a recipe (the part where a model produces output) is marked separately and is never claimed as machine-checked.'),
        ('api_key', 'oxylabs/web-api-mcp',
         'The README says the hosted Remote MCP server uses a Web API key in the Authorization header for each request.',
         '## Connect to the Remote MCP server\n\n'
         'The server is hosted and maintained by Oxylabs. There is nothing to install or update.\n\n'
         '```\nhttps://mcp.oxylabs.io/web-api-mcp\n```\n\n'
         'The server authenticates each request with your Web API key, sent as an `Authorization: Bearer <key>` header.'),
    ]
    claims = []
    for ident, repo, statement, quote in specs:
        target = by_file[(repo, 'README.md')]
        doc = source_docs.get(target.url)
        if doc is None or quote not in doc.text:
            raise ValueError('The actual source no longer supports this exercise claim')
        claims.append({'id': ident, 'statement': statement, 'completed_action': False,
                       'evidence': [{'source_url': target.url, 'quote': quote, 'sha256': doc.sha256}]})
    if len(gathered.documents) != 2 or len(gathered.failures) != 1:
        raise ValueError('Expected two acquired sources and one deliberate missing-file failure')
    revision, code_hashes = code_fingerprint()
    args.output.mkdir(parents=True, exist_ok=False)
    checkpoint = args.output / 'research_checkpoint.json'
    checksum = save_research_checkpoint(checkpoint, payload=payload, goal=goal, claims=claims,
                                       gathered=gathered, code_revision=revision,
                                       approved_urls=approved_urls)
    receipt = {'schema': 'wit.recovery-exercise-receipt.v1',
               'source_selection': 'Official repository URLs supplied in the screenshot; no autonomous search claim.',
               'connected_host_reads': data['connected_fetch_calls'],
               'local_adapter_validations': state['validations'],
               'transport_git_blob': transfer_blob,
               'checkpoint_sha256': checksum, 'code_revision': revision,
               'code_hashes': code_hashes, 'approved_urls': approved_urls,
               'source_sha256': {d.canonical_url: d.sha256 for d in gathered.documents},
               'source_utf8_bytes': {d.canonical_url: len(d.text.encode('utf-8')) for d in gathered.documents},
               'receipts': [asdict(r) for r in gathered.receipts],
               'failures': list(gathered.failures), 'claim_count': len(claims),
               'acquisition_pid': os.getpid(), 'deliberate_signal': 'SIGKILL',
               'checkpoint_path': str(checkpoint.resolve()),
               'semantic_truth_verified': False}
    _json(args.output / 'acquisition_receipt.json', receipt)
    with (args.output / 'acquisition_receipt.json').open('rb') as saved:
        os.fsync(saved.fileno())
    print(json.dumps({'checkpoint_written': True, 'sha256': checksum,
                      'source_count': len(gathered.documents), 'failure_count': len(gathered.failures),
                      'pid': os.getpid(), 'next': 'deliberate SIGKILL before explanation'}), flush=True)
    os.kill(os.getpid(), signal.SIGKILL)


def resume(args):
    receipt = json.loads((args.output / 'acquisition_receipt.json').read_text())
    revision, _ = code_fingerprint()
    if revision != receipt['code_revision']:
        raise ValueError('Implementation changed since acquisition; explicit replay needed')
    session = load_research_checkpoint(args.output / 'research_checkpoint.json',
                                      expected_sha256=receipt['checkpoint_sha256'],
                                      expected_code_revision=revision,
                                      approved_urls=receipt['approved_urls'])
    docs = session.gathered.documents
    # These are runtime acceptance gates, including under Python -O. The
    # separate receipt remains a trusted local-host anchor, not a signature.
    if {d.canonical_url: d.sha256 for d in docs} != receipt['source_sha256']:
        raise ValueError('Restored source hashes differ from acquisition receipt')
    if [asdict(r) for r in session.gathered.receipts] != receipt['receipts']:
        raise ValueError('Restored provider receipts differ from acquisition receipt')
    if list(session.gathered.failures) != receipt['failures']:
        raise ValueError('Restored failures differ from acquisition receipt')
    if os.getpid() == receipt['acquisition_pid']:
        raise ValueError('Recovery requires a different process from acquisition')
    handoff = build_handoff(session.payload, session.goal, session.claims, docs, level='practical')
    handoff['host_failures'] = list(session.gathered.failures)
    handoff['recovery'] = {'source_reads_on_resume': 0,
                            'acquisition_pid': receipt['acquisition_pid'], 'resume_pid': os.getpid(),
                            'checkpoint_sha256': receipt['checkpoint_sha256']}
    _json(args.output / 'restored_handoff.json', handoff)
    _json(args.output / 'semantic_review_request.json', semantic_review_request(session.claims, docs))
    # Deliberate counterclaims are kept outside the real findings.
    original = session.claims[0]
    inverted = dict(original, id='inverted_verification',
                    statement='the AI-generated step of a recipe is claimed as machine-checked.')
    completed = dict(original, id='false_completed_action', completed_action=True,
                     statement='Installed the workflow and completed its release.')
    absent = dict(original, id='absent_quote', evidence=[dict(original['evidence'][0], quote='UNSUPPORTED_TEST_QUOTE_54d6')])
    negative = review_meaning([inverted, completed, absent], docs)
    if not all(row.verdict == 'HOLD' for row in negative):
        raise ValueError('Unsupported recovery counterclaims did not remain held')
    if handoff['verdict'] != 'REVIEW_REQUIRED':
        raise ValueError('Recovered handoff does not have the expected review-required state')
    if handoff['independent_semantic_review_completed'] is not False:
        raise ValueError('Recovery cannot certify independent semantic review')
    if not all(row['verdict'] == 'NEEDS_SEMANTIC_REVIEW' for row in handoff['semantic_precheck']):
        raise ValueError('Recovered claims do not retain the expected semantic-review state')
    result = {'schema': 'wit.live-recovery-result.v1',
              'status': 'PASS', 'same_complete_source_hashes': True,
              'same_provider_receipts': True, 'failure_preserved': True,
              'fresh_process': True, 'network_disabled_on_resume': True,
              'source_reads_on_resume': 0, 'documents': len(docs),
              'utf8_source_bytes': sum(len(d.text.encode('utf-8')) for d in docs),
              'findings_require_review': True, 'independent_semantic_review_completed': False,
              'negative_claims': [asdict(row) for row in negative],
              'code_revision': revision}
    _json(args.output / 'recovery_result.json', result)
    print(json.dumps(result, sort_keys=True))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['acquire', 'resume'])
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--transport', type=Path)
    p.add_argument('--expected-transport-blob')
    args = p.parse_args()
    socket.socket = _no_network
    socket.create_connection = _no_network
    if args.mode == 'acquire':
        if args.transport is None or not args.expected_transport_blob:
            p.error('acquire needs the host transfer and its caller-held digest')
        acquire(args)
    else:
        resume(args)


if __name__ == '__main__':
    main()
