import unittest
from scout import Evidence
from evidence_gate import verify_host_fetch,source_excerpt
class EvidenceGateTests(unittest.TestCase):
    def setUp(self):
        self.e=Evidence('Search tool','https://github.com/example/repo','Search snippets are untrusted')
    def test_no_untrusted_promotion(self):
        with self.assertRaises(PermissionError):
            verify_host_fetch(self.e,final_url=self.e.url,text='full page',retrieval_method='github_connector')
    def test_verified_handoff_and_exact_quote(self):
        doc=verify_host_fetch(self.e,final_url=self.e.url,text='Project supports local search and citations.',retrieval_method='github_connector',host_verified=True)
        self.assertIn('local search',source_excerpt(doc,'local search'))
        self.assertIsNone(source_excerpt(doc,'invented capability'))
        self.assertEqual(len(doc.sha256),64)
    def test_reject_bad_redirect(self):
        with self.assertRaises(ValueError):
            verify_host_fetch(self.e,final_url='http://127.0.0.1/admin',text='secret',retrieval_method='github_connector',host_verified=True)
    def test_reject_oversized_content(self):
        with self.assertRaises(ValueError):
            verify_host_fetch(self.e,final_url=self.e.url,text='a'*200001,retrieval_method='github_connector',host_verified=True)
    def test_reject_unapproved_method(self):
        with self.assertRaises(ValueError):
            verify_host_fetch(self.e,final_url=self.e.url,text='page',retrieval_method='random_scraper',host_verified=True)
if __name__=='__main__': unittest.main()
