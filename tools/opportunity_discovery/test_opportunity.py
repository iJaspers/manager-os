import unittest
from opportunity import canonical, evaluate, run

class Tests(unittest.TestCase):
    def setUp(self):
        self.item=dict(url='https://github.com/example/repo/issues/3?utm_source=x',title='Help with AI context',relevance=35,help_request=25,fit=25,community=15,verified_fit=True,rules_checked=True,status_checked=True,freshness_checked=True,help_intent_checked=True,evidence_urls=['https://github.com/iJaspers/manager-os'])
    def test_valid(self):
        x=evaluate(self.item,set());self.assertEqual(x['gate'],'PASS');self.assertEqual(x['score']['total'],100);self.assertFalse(x['human_approved'])
    def test_duplicate(self):
        s=set();evaluate(self.item,s);self.assertEqual(evaluate(self.item,s)['gate'],'NEEDS_REVIEW')
    def test_rules(self):
        self.assertEqual(evaluate(dict(self.item,rules_checked=False),set())['decision'],'BLOCKED')
    def test_missing_evidence(self):
        self.assertEqual(evaluate(dict(self.item,evidence_urls=[]),set())['gate'],'NEEDS_REVIEW')
    def test_host_block(self):
        with self.assertRaises(ValueError):canonical('https://github.com.evil.com/a')
    def test_http_block(self):
        with self.assertRaises(ValueError):canonical('http://github.com/a')
    def test_hn(self):
        self.assertEqual(canonical('https://news.ycombinator.com/item?id=3&utm=x'),'https://news.ycombinator.com/item?id=3')
    def test_no_network(self):
        self.assertEqual(len(run([self.item])),1)
    def test_removed(self):
        self.assertEqual(evaluate(dict(self.item,removed=True),set())['gate'],'NEEDS_REVIEW')
    def test_score_clamp(self):
        self.assertEqual(evaluate(dict(self.item,relevance=500),set())['score']['relevance'],35)

if __name__=='__main__': unittest.main()
