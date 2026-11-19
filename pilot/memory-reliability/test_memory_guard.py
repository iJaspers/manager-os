import unittest
from memory_guard import select, fingerprint, once_only

BASE = {"id":"a","key":"door","status":"active","source_commit":"abc"}
def trust(record=BASE, classification="non_sensitive", scope="project-a"):
    return {record["id"]:{"digest":fingerprint(record),"classification":classification,"scope":scope}}
def check(records=None, registry=None, scope="project-a", commit="abc"):
    return select([BASE] if records is None else records,"door",commit,trust() if registry is None else registry,scope)

class GuardTests(unittest.TestCase):
    def test_current(self): self.assertEqual(check()["decision"],"use")
    def test_superseded(self): self.assertEqual(check([{**BASE,"status":"superseded"}])["decision"],"hold")
    def test_conflict(self):
        b={**BASE,"id":"b"}
        self.assertEqual(check([BASE,b],{**trust(),**trust(b)})["reason"],"conflicting_active_records")
    def test_sensitive(self): self.assertEqual(check(registry=trust(classification="sensitive"))["reason"],"privacy_review_required")
    def test_unverified(self): self.assertEqual(check(registry={})["reason"],"untrusted_record")
    def test_commit_drift(self): self.assertEqual(check(commit="new")["reason"],"source_revision_unverified")
    def test_commit_match(self): self.assertEqual(check()["decision"],"use")
    def test_no_replay(self): self.assertEqual(once_only({"completed":["x"]},"x")["decision"],"skip")
    def test_no_atomic_claim(self): self.assertEqual(once_only({"completed":[]},"x")["decision"],"review")
    def test_invalid_checkpoint(self): self.assertEqual(once_only({},"x")["decision"],"hold")
    def test_forged_verified(self): self.assertEqual(check([{**BASE,"verified":True,"source":"attacker"}])["reason"],"invalid_record")
    def test_private_payload(self): self.assertEqual(check([{**BASE,"sensitive":False,"payload":"private"}])["reason"],"invalid_record")
    def test_modified_record(self): self.assertEqual(check([{**BASE,"source_commit":"evil"}])["reason"],"provenance_mismatch")
    def test_scope(self): self.assertEqual(check(scope="project-b")["reason"],"scope_mismatch")
    def test_duplicate_id(self): self.assertEqual(check([BASE,BASE])["reason"],"duplicate_record_id")
    def test_missing_trust(self): self.assertEqual(select([BASE],"door")["reason"],"missing_trust_context")
    def test_unknown_privacy(self): self.assertEqual(check(registry=trust(classification="unknown"))["reason"],"privacy_review_required")
    def test_revoked(self): self.assertEqual(check([{**BASE,"status":"revoked"}])["decision"],"hold")
    def test_invalid_action(self): self.assertEqual(once_only({"completed":[]},"")["decision"],"hold")
    def test_self_asserted_registry_not_proof(self):
        # Functional eligibility is NOT authenticated provenance.
        self.assertEqual(check()["decision"],"use")
if __name__=="__main__": unittest.main()
