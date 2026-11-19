import unittest
from memory_guard import fingerprint
from trusted_ingestion import evaluate
R={"id":"decision-1","key":"next_step","status":"active","source_commit":"abc"}
def authority():
    return {"authenticated":True,"scope":"wit","records":{"decision-1":{
        "digest":fingerprint(R),"classification":"non_sensitive","source_commit":"abc"}}}
def run(r=R,a=None,scope="wit",commit="abc"):
    return evaluate(r,authority() if a is None else a,expected_scope=scope,current_commit=commit)
class IngestionTests(unittest.TestCase):
    def test_approved(self): self.assertEqual(run()["decision"],"use")
    def test_untrusted_manifest(self):
        a=authority();a["authenticated"]=False
        self.assertEqual(run(a=a)["reason"],"unauthenticated_authority")
    def test_forged_flag(self):
        self.assertEqual(run({**R,"verified":True})["decision"],"hold")
    def test_payload(self):
        self.assertEqual(run({**R,"payload":"secret"})["decision"],"hold")
    def test_digest_drift(self):
        self.assertEqual(run({**R,"status":"revoked"})["decision"],"hold")
    def test_wrong_project(self):
        self.assertEqual(run(scope="other")["reason"],"authority_scope_mismatch")
    def test_stale(self):
        self.assertEqual(run(commit="def")["reason"],"stale_authority")
    def test_sensitive(self):
        a=authority();a["records"]["decision-1"]["classification"]="sensitive"
        self.assertEqual(run(a=a)["reason"],"privacy_review_required")
    def test_unapproved(self):
        a=authority();a["records"]={}
        self.assertEqual(run(a=a)["reason"],"record_not_approved")
    def test_unknown_auth_schema(self):
        a=authority();a["override"]=True
        self.assertEqual(run(a=a)["reason"],"invalid_authority")
if __name__=="__main__": unittest.main()
