"""Tests the exact GitHub connector result shape without live network access."""
import unittest
from dataclasses import replace
from datetime import datetime, timezone

from github_connector_adapter import GitHubTarget, GitHubConnectorAdapter, github_blob_sha
from trusted_host_bridge import gather
from claim_review import verify_claims


class GitHubAdapterTests(unittest.TestCase):
    def setUp(self):
        self.target = GitHubTarget('iJaspers/manager-os', 'README.md', '57c8de2d5d7dc5b43e4108b36078c9b41e2be75a')
        self.content = 'It is not a separate AI model.\n'
        self.calls = []
        def api(**kwargs):
            self.calls.append(kwargs)
            return {'result': {'content': self.content, 'sha': github_blob_sha(self.content),
                               'display_url': self.target.url}}
        self.api = api
        self.clock = lambda: datetime(2026, 11, 22, 21, 0, tzinfo=timezone.utc)
        self.payload = {'results':[{'title': 'WIT README', 'url': self.target.url,
                                    'excerpt': 'WIT can automatically run everything'}]}

    def adapter(self, reader=None):
        return GitHubConnectorAdapter(reader or self.api, (self.target,), self.clock)

    def test_connector_called_with_immutable_commit(self):
        result = gather(self.payload, 'WIT README', self.adapter())
        self.assertEqual(self.calls[0], {'repository_full_name':'iJaspers/manager-os',
                                        'path':'README.md', 'ref':self.target.commit})
        self.assertEqual(result.documents[0].text, self.content)
        self.assertEqual(result.receipts[0].retrieval_method, 'github_connector')
        self.assertTrue(result.receipts[0].provider_ref.startswith('github-blob:'))

    def test_actual_quote_then_review_only(self):
        result = gather(self.payload,'WIT',self.adapter())
        doc=result.documents[0]
        claim={'id':'wit-not-model','statement':'WIT is not a separate AI model',
               'completed_action':False,'evidence':[{'source_url': self.target.url,
                    'quote':'It is not a separate AI model.', 'sha256':doc.sha256}]}
        self.assertEqual(verify_claims([claim],result.documents).verdict,'REVIEW_REQUIRED')

    def test_unlisted_source_blocked_before_call(self):
        self.payload['results'][0]['url'] = 'https://github.com/iJaspers/manager-os/blob/main/README.md'
        result = gather(self.payload, 'WIT', self.adapter())
        self.assertFalse(self.calls)
        self.assertEqual(len(result.documents), 0)
        self.assertEqual(result.failures[0]['reason'],'PermissionError')

    def test_missing_blob_hash_fails(self):
        def invalid(**kw): return {'result': {'content': self.content, 'sha':'0'*40}}
        self.assertEqual(len(gather(self.payload,'WIT',self.adapter(invalid)).documents),0)

    def test_mismatched_display_ref_fails(self):
        def invalid(**kw): return {'result': {'content': self.content,
            'sha': github_blob_sha(self.content), 'display_url':'https://github.com/iJaspers/manager-os/blob/main/README.md'}}
        self.assertEqual(len(gather(self.payload,'WIT',self.adapter(invalid)).documents),0)

    def test_oversized_blob_fails(self):
        def invalid(**kw): return {'result': {'content':'x'*200001,
             'sha':github_blob_sha('x'*200001), 'display_url':self.target.url}}
        self.assertEqual(len(gather(self.payload,'WIT',self.adapter(invalid)).documents),0)

    def test_reject_unpinned_ref(self):
        with self.assertRaises(ValueError): GitHubTarget('iJaspers/manager-os','README.md','main')

    def test_reject_path_traversal(self):
        with self.assertRaises(ValueError): GitHubTarget('iJaspers/manager-os','a/../README.md',self.target.commit)

    def test_invalid_clock_fails(self):
        bad = GitHubConnectorAdapter(self.api,(self.target,),clock=lambda:datetime(2026,11,22))
        self.assertEqual(len(gather(self.payload,'WIT',bad).documents),0)

    def test_bad_connector_response_fails(self):
        self.assertEqual(len(gather(self.payload,'WIT',self.adapter(lambda **kw: 'ok')).documents),0)


if __name__=='__main__':unittest.main()
