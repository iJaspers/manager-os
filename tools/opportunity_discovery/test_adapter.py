import unittest
from datetime import datetime, timezone
from github_adapter import adapt_issue
from opportunity import evaluate
class AdapterTests(unittest.TestCase):
 def setUp(self):
  self.issue={'html_url':'https://github.com/example/repo/issues/42','title':'Agent forgot context','body':'Context gone','created_at':'2026-11-18T10:00:00Z','state':'open','user':{'login':'example'}}
  self.now=datetime(2026,11,19,tzinfo=timezone.utc)
 def test_normalize(self):
  x=adapt_issue(self.issue,self.now);self.assertEqual(x['source_author'],'example');self.assertFalse(x['stale'])
 def test_closed(self):self.assertTrue(adapt_issue(dict(self.issue,state='closed'),self.now)['removed'])
 def test_pr_excluded(self):self.assertTrue(adapt_issue(dict(self.issue,pull_request={'url':'test'}),self.now)['removed'])
 def test_old(self):self.assertTrue(adapt_issue(dict(self.issue,created_at='2026-01-01T00:00:00Z'),self.now)['stale'])
 def test_not_auto_approved(self):
  x=evaluate(adapt_issue(self.issue,self.now),set());self.assertEqual(x['gate'],'NEEDS_REVIEW');self.assertFalse(x['human_approved'])
 def test_other_host_rejected(self):
  with self.assertRaises(ValueError):adapt_issue(dict(self.issue,html_url='https://github.com.evil.test/a/issues/1'),self.now)
if __name__=='__main__':unittest.main()
