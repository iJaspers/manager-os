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

    def test_optional_requirements_cannot_promote_or_override_holds(self):
        row = dict(id='offline-use', status='SUPPORTED', evidence_index=0)
        normal = evaluate(self.item, set())
        with_fit = evaluate(dict(self.item, fit_requirements=[row]), set())
        self.assertEqual(with_fit.pop('fit_requirements'), [row])
        self.assertEqual(with_fit, normal)
        held = evaluate(dict(self.item, verified_fit=False, fit_requirements=[row]), set())
        self.assertEqual(held['decision'], 'BLOCKED')
        self.assertFalse(held['human_approved'])

    def test_unknown_and_unmet_hold_despite_score(self):
        rows = [dict(id='phone', status='UNKNOWN', evidence_index=None),
                dict(id='local-use', status='NOT_MET', evidence_index=0)]
        assessed = evaluate(dict(self.item, fit_requirements=rows), set())
        self.assertEqual(assessed['score']['total'], 100)
        self.assertEqual(assessed['decision'], 'BLOCKED')
        self.assertEqual(assessed['fit_requirements'], list(reversed(rows)))
        self.assertIn('required capability not met', assessed['gate_reasons'])
        self.assertIn('required capability unknown', assessed['gate_reasons'])
        self.assertIsNone(assessed['posted_url'])

    def test_requirements_require_bounded_unique_ids_and_evidence_indices(self):
        row = dict(id='offline-use', status='SUPPORTED', evidence_index=0)
        for invalid in ([], [row] * 13, [row, row], [dict(row, evidence_index=True)],
                        [dict(row, evidence_index=1)], [dict(row, evidence_index=-1)],
                        [dict(row, status='UNKNOWN')], [dict(row, status='APPROVED')],
                        [dict(row, id='<b>')], [dict(row, human_approved=True)]):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                evaluate(dict(self.item, fit_requirements=invalid), set())

if __name__=='__main__': unittest.main()
