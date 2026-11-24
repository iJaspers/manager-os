import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from dataclasses import replace
from unittest.mock import patch

from github_connector_adapter import github_blob_sha
from research_checkpoint import (
    MAX_CHECKPOINT_BYTES, load_research_checkpoint, save_research_checkpoint,
)
from research_handoff import build_handoff
from scout import Evidence, load_checkpoint, save_checkpoint
from trusted_host_bridge import HostRead, gather


class ResearchCheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'research.json'
        self.urls = tuple(f'https://example.org/{name}' for name in ('a', 'b', 'c'))
        self.payload = {'results': [
            {'title': f'Workflow {name}', 'url': url, 'excerpt': 'Provider snippet'}
            for name, url in zip(('A', 'B', 'C'), self.urls)]}
        self.goal = 'workflow'
        self.revision = 'upstream-3a843a6-working-code-sha256-example'
        self.gathered = gather(self.payload, self.goal, self.read)
        self.claims = [{
            'id': 'source-a', 'statement': 'The source discusses safe retry.',
            'evidence': [{'source_url': self.urls[0], 'quote': 'café — retry safely.',
                          'sha256': self.gathered.documents[0].sha256}],
            'completed_action': False}]

    def read(self, source):
        if source.url == self.urls[1]:
            raise TimeoutError('PRIVATE TOKEN MUST NOT BE STORED')
        return HostRead(source.url, source.url, 'Source text: café — retry safely.\n',
                        'trusted_search_fetch', 'fetch-123', '2026-11-22T21:45:00-07:00')

    def save(self, **changes):
        values = dict(payload=self.payload, goal=self.goal, claims=self.claims,
                      gathered=self.gathered, code_revision=self.revision,
                      approved_urls=self.urls)
        values.update(changes)
        return save_research_checkpoint(self.path, **values)

    def load(self, digest, **changes):
        values = dict(expected_sha256=digest, expected_code_revision=self.revision,
                      approved_urls=self.urls)
        values.update(changes)
        return load_research_checkpoint(self.path, **values)

    def mutate(self, change):
        self.save()
        value = json.loads(self.path.read_text(encoding='utf-8'))
        change(value)
        raw = json.dumps(value, ensure_ascii=False).encode('utf-8')
        self.path.write_bytes(raw)
        return hashlib.sha256(raw).hexdigest()

    def test_complete_roundtrip_preserves_handoff_and_failures(self):
        digest = self.save()
        restored = self.load(digest)
        self.assertEqual(restored.gathered, self.gathered)
        self.assertEqual(restored.payload, self.payload)
        self.assertEqual(list(restored.claims), self.claims)
        self.assertEqual(build_handoff(self.payload, self.goal, self.claims,
                                       self.gathered.documents),
                         build_handoff(restored.payload, restored.goal,
                                       restored.claims, restored.gathered.documents))
        self.assertEqual(restored.gathered.evidence_state, 'HOST_READ_REVIEW_REQUIRED')
        self.assertNotIn('PRIVATE TOKEN', self.path.read_text(encoding='utf-8'))

    def test_fresh_process_restores_without_connector(self):
        digest = self.save()
        code = '''
import json, sys
from research_checkpoint import load_research_checkpoint
from research_handoff import build_handoff
s = load_research_checkpoint(sys.argv[1], expected_sha256=sys.argv[2],
    expected_code_revision=sys.argv[3], approved_urls=json.loads(sys.argv[4]))
h = build_handoff(s.payload, s.goal, s.claims, s.gathered.documents)
print(json.dumps({'documents':len(s.gathered.documents), 'failures':s.gathered.failures,
                  'verdict':h['verdict'], 'reviewed':h['independent_semantic_review_completed']}))
'''
        child = subprocess.run([sys.executable, '-B', '-c', code, str(self.path),
                                digest, self.revision, json.dumps(self.urls)],
                               cwd=Path(__file__).parent, capture_output=True,
                               text=True, timeout=10, check=True)
        observed = json.loads(child.stdout)
        self.assertEqual(observed['documents'], 2)
        self.assertEqual(observed['failures'], list(self.gathered.failures))
        self.assertEqual(observed['verdict'], 'REVIEW_REQUIRED')
        self.assertFalse(observed['reviewed'])

    def test_modified_bytes_rejected_with_original_host_digest(self):
        digest = self.save()
        self.path.write_bytes(self.path.read_bytes().replace(b'retry safely', b'retry freely'))
        with self.assertRaisesRegex(ValueError, 'bytes changed'):
            self.load(digest)

    def test_truncated_checkpoint_rejected(self):
        digest = self.save()
        self.path.write_bytes(self.path.read_bytes()[:100])
        with self.assertRaises(ValueError):
            self.load(digest)

    def test_changed_code_revision_rejected(self):
        digest = self.save()
        with self.assertRaisesRegex(ValueError, 'revision changed'):
            self.load(digest, expected_code_revision='new-code')

    def test_changed_allowlist_rejected(self):
        digest = self.save()
        with self.assertRaisesRegex(ValueError, 'allowlist changed'):
            self.load(digest, approved_urls=self.urls[:2])

    def test_unknown_schema_rejected(self):
        digest = self.mutate(lambda x: x.update(schema='wit.research-checkpoint.v99'))
        with self.assertRaisesRegex(ValueError, 'unsupported'):
            self.load(digest)

    def test_inner_source_hash_checked_even_with_new_outer_digest(self):
        digest = self.mutate(lambda x: x['gathered']['documents'][0].update(text='changed'))
        with self.assertRaisesRegex(ValueError, 'disagree'):
            self.load(digest)

    def test_receipt_source_mismatch_rejected(self):
        digest = self.mutate(lambda x: x['gathered']['receipts'][0].update(
            requested_url=self.urls[2]))
        with self.assertRaises(ValueError):
            self.load(digest)

    def test_changed_receipt_time_rejected(self):
        digest = self.mutate(lambda x: x['gathered']['receipts'][0].update(
            observed_at='2026-11-22T21:45:00'))
        with self.assertRaisesRegex(ValueError, 'timezone'):
            self.load(digest)

    def test_success_cannot_replace_recorded_failure(self):
        digest = self.mutate(lambda x: x['gathered']['failures'].clear())
        with self.assertRaisesRegex(ValueError, 'source plan'):
            self.load(digest)

    def test_completion_or_approval_cannot_be_inserted(self):
        digest = self.mutate(lambda x: x['gathered'].update(evidence_state='APPROVED'))
        with self.assertRaisesRegex(ValueError, 'promote'):
            self.load(digest)

    def test_changed_search_input_cannot_keep_old_ranked_evidence(self):
        digest = self.mutate(lambda x: x['payload']['results'][0].update(excerpt='changed'))
        with self.assertRaisesRegex(ValueError, 'original inputs'):
            self.load(digest)

    def test_source_limit_enforced(self):
        digest = self.mutate(lambda x: x['gathered'].update(
            documents=x['gathered']['documents'] * 4))
        with self.assertRaisesRegex(ValueError, 'documents collection'):
            self.load(digest)

    def test_provider_result_limit_enforced(self):
        digest = self.mutate(lambda x: x['payload'].update(
            results=x['payload']['results'] * 34))
        with self.assertRaisesRegex(ValueError, 'provider results'):
            self.load(digest)

    def test_document_utf8_byte_limit_enforced(self):
        def large(source):
            return replace(self.read(source), text='é' * 100001)
        result = gather(self.payload, self.goal, large)
        with self.assertRaisesRegex(ValueError, 'document text'):
            self.save(gathered=result)

    def test_invalid_save_preserves_last_valid_checkpoint(self):
        digest = self.save()
        before = self.path.read_bytes()
        with self.assertRaises(ValueError):
            self.save(gathered=replace(self.gathered, evidence_state='APPROVED'))
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(self.load(digest).gathered, self.gathered)

    def test_failed_atomic_replace_preserves_checkpoint(self):
        digest = self.save()
        before = self.path.read_bytes()
        with patch('scout.os.replace', side_effect=OSError('disk failure')):
            with self.assertRaises(OSError):
                self.save()
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(list(self.path.parent.glob('.scout-*')), [])
        self.load(digest)

    def test_github_blob_receipt_is_rechecked(self):
        url = 'https://github.com/example/project/blob/' + 'a' * 40 + '/README.md'
        payload = {'results': [{'title': 'Workflow', 'url': url, 'excerpt': 'snippet'}]}
        text = 'The immutable source body.'
        result = gather(payload, self.goal, lambda s: HostRead(
            s.url, s.url, text, 'github_connector', 'github-blob:' + github_blob_sha(text),
            '2026-11-22T21:45:00-07:00'))
        digest = self.save(payload=payload, gathered=result, approved_urls=[url])
        self.load(digest, approved_urls=[url])
        bad = replace(result.receipts[0], provider_ref='github-blob:' + 'b' * 40)
        with self.assertRaisesRegex(ValueError, 'GitHub receipt'):
            self.save(payload=payload, approved_urls=[url],
                      gathered=replace(result, receipts=(bad,)))

    def test_rejected_claim_remains_hold_after_restore(self):
        claim = {**self.claims[0], 'completed_action': True}
        digest = self.save(claims=[claim])
        restored = self.load(digest)
        handoff = build_handoff(restored.payload, restored.goal,
                                restored.claims, restored.gathered.documents)
        self.assertEqual(handoff['verdict'], 'HOLD')
        self.assertFalse(handoff['independent_semantic_review_completed'])

    def test_duplicate_json_fields_rejected(self):
        self.save()
        raw = self.path.read_bytes()
        needle = b'"schema": "wit.research-checkpoint.v1"'
        raw = raw.replace(needle, needle + b',' + needle)
        self.path.write_bytes(raw)
        with self.assertRaisesRegex(ValueError, 'duplicate JSON'):
            self.load(hashlib.sha256(raw).hexdigest())

    def test_no_self_anchored_digest_default(self):
        self.save()
        with self.assertRaises(TypeError):
            load_research_checkpoint(self.path, expected_code_revision=self.revision,
                                     approved_urls=self.urls)

    def test_checkpoint_byte_limit_enforced_before_json_parse(self):
        raw = b' ' * (MAX_CHECKPOINT_BYTES + 1)
        self.path.write_bytes(raw)
        with self.assertRaisesRegex(ValueError, 'byte budget'):
            self.load(hashlib.sha256(raw).hexdigest())

    def test_legacy_v1_checkpoint_unchanged(self):
        items = [Evidence('A', self.urls[0], 'snippet')]
        save_checkpoint(self.path, items)
        self.assertEqual(load_checkpoint(self.path), items)


if __name__ == '__main__':
    unittest.main()
