import unittest
from evidence_gate import verify_host_fetch
from scout import Evidence
from semantic_guard import review_meaning, semantic_review_request
from research_handoff import build_handoff

class SemanticGateTests(unittest.TestCase):
    def setUp(self):
        self.src=Evidence('WIT','https://github.com/iJaspers/manager-os','Wit')
        self.doc=verify_host_fetch(self.src, final_url=self.src.url,
            text='It is not a separate AI model. Witburrow supplies the operating rules around the model.',
            retrieval_method='github_connector',host_verified=True)
        self.base={'id':'feature','statement':'Witburrow is not a separate AI model',
            'completed_action':False,
            'evidence':[{'source_url':self.src.url, 'quote':'It is not a separate AI model.', 'sha256':self.doc.sha256}]}

    def run_gate(self, statement=None, quote=None):
        claim={**self.base}
        if statement is not None:claim['statement']=statement
        if quote is not None:claim['evidence']=[{**self.base['evidence'][0], 'quote': quote}]
        return review_meaning([claim],[self.doc])[0]

    def test_true_still_needs_independent_meaning_review(self):
        self.assertEqual(self.run_gate().verdict,'NEEDS_SEMANTIC_REVIEW')

    def test_inverted_copula_is_held(self):
        result=self.run_gate('Witburrow is a separate AI model')
        self.assertEqual(result.verdict,'HOLD')
        self.assertIn('POSSIBLE_NEGATION_CONFLICT',result.issues)

    def test_not_claim_does_not_make_unsupported_other_feature_true(self):
        self.assertEqual(self.run_gate('Witburrow automatically handles taxes').verdict,
                         'NEEDS_SEMANTIC_REVIEW')

    def test_missing_quote_stays_hold(self):
        self.assertEqual(self.run_gate(quote='unquoted words').verdict,'HOLD')

    def test_no_evidence_stays_hold(self):
        claim={**self.base,'evidence':[]}
        self.assertEqual(review_meaning([claim],[self.doc])[0].verdict,'HOLD')

    def test_false_done_claim_stays_hold(self):
        claim={**self.base,'completed_action':True}
        self.assertEqual(review_meaning([claim],[self.doc])[0].verdict,'HOLD')

    def test_review_request_disclaims_independence(self):
        task=semantic_review_request([self.base],[self.doc])
        self.assertFalse(task['independence_verified'])
        self.assertEqual(task['questions'][0]['precheck_verdict'],'NEEDS_SEMANTIC_REVIEW')

    def test_review_request_has_bounded_excerpt_only(self):
        task=semantic_review_request([self.base],[self.doc])
        self.assertNotIn('Witburrow supplies',str(task))

    def test_unfetched_source_hold(self):
        result=review_meaning([self.base],[])[0]
        self.assertEqual(result.verdict,'HOLD')

    def test_handoff_holds_inverted_claim(self):
        claim={**self.base,'statement':'Witburrow is a separate AI model'}
        payload={'results':[{'title':'WIT', 'url':self.src.url, 'excerpt':'provider snippet'}]}
        handoff=build_handoff(payload,'WIT',[claim],[self.doc])
        self.assertEqual(handoff['claim_review']['verdict'],'REVIEW_REQUIRED')
        self.assertEqual(handoff['verdict'],'HOLD')
        self.assertFalse(handoff['independent_semantic_review_completed'])

    def test_none_of_these_negation_is_held(self):
        source=Evidence('Policy','https://example.org/policy','none')
        doc=verify_host_fetch(source,final_url=source.url,
            text='None of these authorize canonical writes or privileged execution.',
            retrieval_method='trusted_browser',host_verified=True)
        claim={'id':'claim','statement':'These authorize canonical writes or privileged execution',
               'completed_action':False,'evidence':[{'source_url':source.url,
               'quote':'None of these authorize canonical writes or privileged execution.',
               'sha256':doc.sha256}]}
        self.assertEqual(review_meaning([claim],[doc])[0].verdict,'HOLD')

    def test_cannot_is_a_negation(self):
        source=Evidence('Policy','https://example.org/policy2','none')
        doc=verify_host_fetch(source,final_url=source.url,
            text='None of these authorize canonical writes or privileged execution.',
            retrieval_method='trusted_browser',host_verified=True)
        claim={'id':'claim','statement':'Untrusted material cannot authorize canonical writes or privileged execution',
               'completed_action':False,'evidence':[{'source_url':source.url,
               'quote':'None of these authorize canonical writes or privileged execution.',
               'sha256':doc.sha256}]}
        self.assertEqual(review_meaning([claim],[doc])[0].verdict,'NEEDS_SEMANTIC_REVIEW')

    def test_same_predicate_no_negation_difference(self):
        self.assertEqual(self.run_gate('It is not a separate AI model').verdict,'NEEDS_SEMANTIC_REVIEW')

    def test_short_infix_negation(self):
        from semantic_guard import _opposite_negation
        self.assertTrue(_opposite_negation('Discovery is approval.',
                                          'Discovery is not approval.'))

    def test_cannot_vs_can(self):
        from semantic_guard import _opposite_negation
        self.assertTrue(_opposite_negation('It can access secrets.',
                                          'It cannot access secrets.'))

    def test_negation_in_unrelated_clause_not_assigned_to_claim(self):
        from semantic_guard import _opposite_negation
        self.assertFalse(_opposite_negation('The tool may read public web pages.',
            'The tool cannot access secrets but may read public web pages.'))

    def test_short_infix_reaches_integrated_hold(self):
        source=Evidence('README','https://example.org/readme','discovery')
        doc=verify_host_fetch(source,final_url=source.url,
            text='Discovery is not approval.',
            retrieval_method='trusted_browser',host_verified=True)
        claim={'id':'authority','statement':'Discovery is approval.',
            'completed_action':False,'evidence':[{'source_url':source.url,
            'quote':'Discovery is not approval.','sha256':doc.sha256}]}
        self.assertEqual(review_meaning([claim],[doc])[0].verdict,'HOLD')

if __name__=='__main__':unittest.main()
