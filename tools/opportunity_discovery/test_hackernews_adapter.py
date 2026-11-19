import unittest
from datetime import datetime, timezone
from hackernews_adapter import adapt_item
from opportunity import evaluate

class HackerNewsAdapterTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,11,19,tzinfo=timezone.utc)
        self.item={'id':123,'time':int(datetime(2026,11,18,tzinfo=timezone.utc).timestamp()),'title':'Ask HN: agent memory','by':'example','text':'How do you preserve context?'}
    def test_url(self):
        self.assertEqual(adapt_item(self.item,self.now)['url'],'https://news.ycombinator.com/item?id=123')
    def test_recent(self):self.assertFalse(adapt_item(self.item,self.now)['stale'])
    def test_dead(self):self.assertTrue(adapt_item(dict(self.item,dead=True),self.now)['removed'])
    def test_stale(self):self.assertTrue(adapt_item(dict(self.item,time=1),self.now)['stale'])
    def test_invalid_id(self):
        with self.assertRaises(ValueError):adapt_item(dict(self.item,id=True),self.now)
    def test_no_self_approval(self):
        r=evaluate(adapt_item(self.item,self.now),set())
        self.assertEqual(r['decision'],'BLOCKED')
        self.assertFalse(r['human_approved'])
if __name__=='__main__':unittest.main()
