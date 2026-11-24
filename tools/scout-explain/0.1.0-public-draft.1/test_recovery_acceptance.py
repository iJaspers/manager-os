"""Acceptance gates must survive optimization in real recovery subprocesses.

Inputs are explicit synthetic sources. No live connector or approval is implied.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import unittest

from github_connector_adapter import GitHubTarget, github_blob_sha

ROOT = Path(__file__).resolve().parent


@unittest.skipUnless(hasattr(signal, 'SIGKILL'), 'Recovery exercise requires POSIX SIGKILL')
class RecoveryAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        folder = Path(self.temp.name)
        self.output = folder / 'recovery'
        sources = [
            ('Neeeophytee/awesome-ai-workflows', 'a' * 40,
             '# Synthetic source\n'
             'the AI-generated step of a recipe (the part where a model produces output) '
             'is marked separately and is never claimed as machine-checked.'),
            ('oxylabs/web-api-mcp', 'b' * 40,
             '# Synthetic source\n'
             '## Connect to the Remote MCP server\n\n'
             'The server is hosted and maintained by Oxylabs. There is nothing to install or update.\n\n'
             '```\nhttps://mcp.oxylabs.io/web-api-mcp\n```\n\n'
             'The server authenticates each request with your Web API key, '
             'sent as an `Authorization: Bearer <key>` header.'),
        ]
        rows = []
        for repository, commit, text in sources:
            target = GitHubTarget(repository, 'README.md', commit)
            rows.append({
                'target': {'repo': repository, 'path': target.path, 'commit': commit,
                           'title': repository, 'excerpt': 'Synthetic recovery source'},
                'reply': {'structuredContent': {'content': text, 'encoding': 'utf-8',
                                                'sha': github_blob_sha(text),
                                                'display_url': target.url}, 'isError': False},
            })
        missing = GitHubTarget('oxylabs/web-api-mcp', 'MISSING_RECOVERY_PROBE.md', 'b' * 40)
        rows.append({
            'target': {'repo': missing.repository, 'path': missing.path,
                       'commit': missing.commit, 'title': 'Deliberate missing file',
                       'excerpt': 'Synthetic missing-file control'},
            'reply': {'isError': True},
        })
        transfer = {'schema': 'wit.connected-host-transfer.v1', 'records': rows,
                    'observed_at': '2026-11-23T12:00:00+00:00', 'connected_fetch_calls': 3}
        raw = json.dumps(transfer).encode('utf-8')
        transport = folder / 'transport.json'
        transport.write_bytes(raw)
        digest = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        acquired = self.child(False, 'host_recovery_exercise.py', 'acquire',
                              '--transport', str(transport), '--expected-transport-blob', digest,
                              '--output', str(self.output))
        self.assertEqual(acquired.returncode, -signal.SIGKILL, acquired.stdout + acquired.stderr)
        self.receipt_path = self.output / 'acquisition_receipt.json'
        self.receipt = json.loads(self.receipt_path.read_text())

    def child(self, optimized, *args):
        command = [sys.executable, '-B', *(['-O'] if optimized else []), *args]
        environment = os.environ.copy()
        environment.pop('PYTHONOPTIMIZE', None)
        return subprocess.run(command, cwd=ROOT, env=environment, capture_output=True,
                              text=True, timeout=10, check=False)

    def resume(self, optimized):
        return self.child(optimized, 'host_recovery_exercise.py', 'resume',
                          '--output', str(self.output))

    def assert_rejected(self, result, message):
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn('ValueError: ' + message, result.stderr)
        self.assertNotIn('"status": "PASS"', result.stdout)
        self.assertFalse((self.output / 'recovery_result.json').exists())

    def test_valid_recovery_passes_in_normal_and_optimized_processes(self):
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                result = self.resume(optimized)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                report = json.loads(result.stdout)
                self.assertEqual(report['status'], 'PASS')
                self.assertTrue(report['same_complete_source_hashes'])
                self.assertFalse(report['independent_semantic_review_completed'])

    def test_changed_receipt_is_rejected_with_and_without_optimization(self):
        changes = (
            ('source_sha256', {url: '0' * 64 for url in self.receipt['source_sha256']},
             'Restored source hashes differ from acquisition receipt'),
            ('receipts', [], 'Restored provider receipts differ from acquisition receipt'),
            ('failures', [], 'Restored failures differ from acquisition receipt'),
        )
        for field, value, message in changes:
            altered = copy.deepcopy(self.receipt)
            altered[field] = value
            self.receipt_path.write_text(json.dumps(altered))
            for optimized in (False, True):
                with self.subTest(field=field, optimized=optimized):
                    self.assert_rejected(self.resume(optimized), message)

    def test_same_process_cannot_be_certified_as_a_restart(self):
        code = '''
from argparse import Namespace
import json, os, sys
from pathlib import Path
from host_recovery_exercise import resume
output = Path(sys.argv[1])
path = output / 'acquisition_receipt.json'
receipt = json.loads(path.read_text())
receipt['acquisition_pid'] = os.getpid()
path.write_text(json.dumps(receipt))
resume(Namespace(output=output))
'''
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                result = self.child(optimized, '-c', code, str(self.output))
                self.assert_rejected(result, 'Recovery requires a different process from acquisition')

    def test_held_handoff_cannot_be_certified_in_either_mode(self):
        # Supply a new trusted digest deliberately: this exercises acceptance
        # state after valid checkpoint loading, not a self-authentication claim.
        checkpoint = self.output / 'research_checkpoint.json'
        data = json.loads(checkpoint.read_text())
        data['claims'][0]['completed_action'] = True
        raw = json.dumps(data).encode('utf-8')
        checkpoint.write_bytes(raw)
        altered = copy.deepcopy(self.receipt)
        altered['checkpoint_sha256'] = hashlib.sha256(raw).hexdigest()
        self.receipt_path.write_text(json.dumps(altered))
        for optimized in (False, True):
            with self.subTest(optimized=optimized):
                self.assert_rejected(self.resume(optimized),
                    'Recovered handoff does not have the expected review-required state')


if __name__ == '__main__':
    unittest.main()
