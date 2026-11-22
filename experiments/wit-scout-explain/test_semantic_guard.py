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

    def test_same_predicate_no_negation_difference(self):
        self.assertEqual(self.run_gate('It is not a separate AI model').verdict,'NEEDS_SEMANTIC_REVIEW')

if __name__=='__main__':unittest.main()
