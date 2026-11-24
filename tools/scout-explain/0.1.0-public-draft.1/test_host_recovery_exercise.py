"""Regression for distinct source files in one repository during acquisition."""
from argparse import Namespace
from contextlib import redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import signal
import tempfile
import unittest
from unittest.mock import patch

from github_connector_adapter import GitHubTarget, github_blob_sha
from host_recovery_exercise import acquire
from research_checkpoint import load_research_checkpoint


class HostRecoveryExerciseTests(unittest.TestCase):
    def test_missing_file_after_same_repository_readme_does_not_replace_source(self):
        # Deliberately synthetic complete source bytes and immutable refs. The
        # last row shares Oxylabs' repository but identifies a different file.
        timestamp = '2026-11-22T22:00:00+00:00'
        sources = [
            ('Neeeophytee/awesome-ai-workflows', 'a' * 40,
             '# Synthetic verification fixture\n'
             'the AI-generated step of a recipe (the part where a model produces output) '
             'is marked separately and is never claimed as machine-checked.\n'),
            ('oxylabs/web-api-mcp', 'b' * 40,
             '# Synthetic API-key fixture\n'
             '## Connect to the Remote MCP server\n\n'
             'The server is hosted and maintained by Oxylabs. There is nothing to install or update.\n\n'
             '```\nhttps://mcp.oxylabs.io/web-api-mcp\n```\n\n'
             'The server authenticates each request with your Web API key, sent as an `Authorization: Bearer <key>` header.\n'),
        ]
        rows = []
        expected_urls = set()
        for repository, commit, text in sources:
            target = GitHubTarget(repository, 'README.md', commit)
            expected_urls.add(target.url)
            rows.append({
                'target': {'repo': repository, 'path': 'README.md', 'commit': commit,
                           'title': repository, 'excerpt': text.splitlines()[1]},
                'reply': {'content': [{'type': 'text', 'text': 'Synthetic host fixture'}],
                          'structuredContent': {'content': text, 'encoding': 'utf-8',
                                                'sha': github_blob_sha(text),
                                                'display_url': target.url},
                          'isError': False},
            })
        missing = GitHubTarget('oxylabs/web-api-mcp', 'MISSING_RECOVERY_PROBE.md', 'b' * 40)
        rows.append({
            'target': {'repo': missing.repository, 'path': missing.path, 'commit': missing.commit,
                       'title': 'Deliberate missing file', 'excerpt': 'Missing-file control'},
            'reply': {'content': [{'type': 'text', 'text': 'Synthetic missing-file response'}],
                      'isError': True},
        })
        transfer = {'schema': 'wit.connected-host-transfer.v1', 'records': rows,
                    'observed_at': timestamp, 'connected_fetch_calls': len(rows)}
        raw = json.dumps(transfer, ensure_ascii=False).encode('utf-8')
        digest = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        with tempfile.TemporaryDirectory() as tmp:
            transport = Path(tmp) / 'transport.json'
            transport.write_bytes(raw)
            output = Path(tmp) / 'acquisition'
            args = Namespace(transport=transport, expected_transport_blob=digest, output=output)
            with patch('host_recovery_exercise.os.kill') as kill, \
                    patch('socket.socket', side_effect=AssertionError('No network in this test')), \
                    patch('socket.create_connection', side_effect=AssertionError('No network in this test')), \
                    redirect_stdout(io.StringIO()):
                acquire(args)
            kill.assert_called_once_with(os.getpid(), signal.SIGKILL)
            receipt = json.loads((output / 'acquisition_receipt.json').read_text())
            self.assertEqual(receipt['local_adapter_validations'], 3)
            self.assertEqual(set(receipt['source_sha256']), expected_urls)
            self.assertEqual(receipt['failures'], [{'url': missing.url, 'reason': 'ValueError'}])
            restored = load_research_checkpoint(
                output / 'research_checkpoint.json', expected_sha256=receipt['checkpoint_sha256'],
                expected_code_revision=receipt['code_revision'], approved_urls=receipt['approved_urls'])
            self.assertEqual({doc.canonical_url for doc in restored.gathered.documents}, expected_urls)
            self.assertEqual(len(restored.gathered.receipts), 2)
            self.assertEqual(list(restored.gathered.failures), receipt['failures'])
            self.assertEqual({item['source_url'] for claim in restored.claims
                              for item in claim['evidence']}, expected_urls)
            remote_claim = next(claim for claim in restored.claims if claim['id'] == 'api_key')
            self.assertIn('hosted Remote MCP server', remote_claim['statement'])
            self.assertTrue(remote_claim['evidence'][0]['quote'].startswith('## Connect to the Remote MCP server\n'))


if __name__ == '__main__':
    unittest.main()
