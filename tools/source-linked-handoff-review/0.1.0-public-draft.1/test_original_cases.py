"""Nine recovered BOB-089 scenarios; fictional fixture and timezone validation updated."""
import unittest
import handoff as m89

class B089(unittest.TestCase):
    def data(self):return {'owner':'Fictional Workshop','source_task':'task:fictional-1','source_observed_at':'2026-11-03T12:00:00Z','proposal':'review only','evidence_refs':['e1'],'source_state':'REVIEW','claim_resolved':False,'performed_write':False,'automated_send':False}
    def test_positive(self):self.assertEqual(m89.evaluate(self.data())['status'],'REVIEWABLE_HANDOFF_PROPOSAL')
    def test_absent_evidence(self):
        x=self.data();x['evidence_refs']=[];self.assertIn('MISSING_VERIFIABLE_EVIDENCE_REF',m89.evaluate(x)['issues'])
    def test_duplicate_evidence(self):
        x=self.data();x['evidence_refs']=['e1','e1'];self.assertIn('DUPLICATE_EVIDENCE_REF',m89.evaluate(x)['issues'])
    def test_reopening_without_change(self):
        x=self.data();x['source_state']='DONE';self.assertIn('REOPENING_STOPPED_SOURCE_WITHOUT_NEW_EVIDENCE',m89.evaluate(x)['issues'])
    def test_claim_without_approval(self):
        x=self.data();x['claim_resolved']=True;self.assertIn('UNSUPPORTED_RESOLUTION_CLAIM',m89.evaluate(x)['issues'])
    def test_external_actions(self):
        x=self.data();x['automated_send']=True;x['performed_write']=True;z=m89.evaluate(x);self.assertIn('AUTOMATED_EXTERNAL_ACTION_NOT_ALLOWED',z['issues']);self.assertIn('SOURCE_OR_EXTERNAL_WRITE_NOT_ALLOWED',z['issues'])
    def test_bob_ownership(self):
        x=self.data();x['owner']='BOB';self.assertIn('BOB_CANNOT_BE_SOURCE_OWNER',m89.evaluate(x)['issues'])
    def test_bad_source_state_type(self):
        x=self.data();x['source_state']=[];z=m89.evaluate(x);self.assertEqual(z['status'],'HOLD')
    def test_bad_evidence_dict(self):
        x=self.data();x['evidence_refs']=[{}];z=m89.evaluate(x);self.assertEqual(z['status'],'HOLD')
