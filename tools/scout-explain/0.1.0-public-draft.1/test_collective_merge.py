"""Regressions at the join of the two independently developed Scout branches.

All source content and host callbacks in these cases are explicit test fixtures.
"""
import copy
from pathlib import Path
import tempfile
import unittest

from research_checkpoint import load_research_checkpoint, save_research_checkpoint
from research_handoff import build_handoff
from trusted_host_bridge import HostRead, gather


class CollectiveMergeTests(unittest.TestCase):
    def restored(self):
        url = 'https://example.org/synthetic-recovery-review'
        quote = 'Generated outputs still require review.'
        payload = {'results': [{'title': 'Synthetic recovery example', 'url': url,
                                'excerpt': 'Synthetic discovery snippet'}]}
        def read(source):
            return HostRead(source.url, source.url, '# Fixture\n' + quote + '\n',
                            'trusted_search_fetch', 'synthetic-test-only',
                            '2026-11-23T12:00:00-07:00')
        gathered = gather(payload, 'generated outputs review', read)
        claims = [{'id': 'review-limit', 'statement': quote, 'completed_action': False,
                   'evidence': [{'source_url': url, 'quote': quote,
                                 'sha256': gathered.documents[0].sha256}]}]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'checkpoint.json'
            digest = save_research_checkpoint(path, payload=payload,
                goal='generated outputs review', claims=claims, gathered=gathered,
                code_revision='collective-private-merge-fixture', approved_urls=[url])
            restored = load_research_checkpoint(path, expected_sha256=digest,
                expected_code_revision='collective-private-merge-fixture',
                approved_urls=[url])
        return restored, quote

    def test_recovery_does_not_enable_private_quick_view_by_itself(self):
        state, _ = self.restored()
        handoff = build_handoff(state.payload, state.goal, state.claims,
                                state.gathered.documents)
        self.assertEqual(handoff['verdict'], 'REVIEW_REQUIRED')
        self.assertNotIn('evidence', handoff['quick_view']['claims'][0])
        self.assertFalse(handoff['independent_semantic_review_completed'])

    def test_explicit_same_audience_view_keeps_recovered_quote_and_navigation(self):
        state, quote = self.restored()
        handoff = build_handoff(state.payload, state.goal, state.claims,
            state.gathered.documents, same_audience_private_evidence=True)
        item = handoff['quick_view']['claims'][0]['evidence'][0]
        self.assertEqual(item['quote'], quote)
        self.assertEqual(item['evidence_state'], 'MATCHED_HOST_TEXT')
        self.assertEqual(item['navigation'], handoff['claim_details'][0]['evidence'][0]['navigation'])
        self.assertEqual(handoff['quick_view']['verdict'], 'REVIEW_REQUIRED')

    def test_changed_completion_claim_stays_held_after_recovery_in_both_views(self):
        state, _ = self.restored()
        before = build_handoff(state.payload, state.goal, state.claims,
                               state.gathered.documents)
        changed = copy.deepcopy(list(state.claims))
        changed[0]['completed_action'] = True
        changed[0]['statement'] = 'The generated output has been approved and delivered.'
        handoff = build_handoff(state.payload, state.goal, changed,
            state.gathered.documents, previous_binding=before['review_binding']['sha256'],
            same_audience_private_evidence=True)
        self.assertEqual(handoff['review_binding']['state'], 'INPUTS_CHANGED')
        self.assertEqual(handoff['verdict'], 'HOLD')
        self.assertEqual(handoff['quick_view']['verdict'], 'HOLD')
        self.assertFalse(handoff['independent_semantic_review_completed'])


if __name__ == '__main__':
    unittest.main()
