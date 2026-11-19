import unittest
from memory_guard import select, once_only

BASE = {"id":"a","key":"door","status":"active","verified":True}
class GuardTests(unittest.TestCase):
    def test_current(self): self.assertEqual(select([BASE],"door")["decision"],"use")
    def test_superseded(self): self.assertEqual(select([{**BASE,"status":"superseded"}],"door")["decision"],"hold")
    def test_conflict(self): self.assertEqual(select([BASE,{**BASE,"id":"b"}],"door")["reason"],"conflicting_active_records")
    def test_sensitive(self): self.assertEqual(select([{**BASE,"sensitive":True}],"door")["decision"],"hold")
    def test_unverified(self): self.assertEqual(select([{**BASE,"verified":False}],"door")["decision"],"hold")
    def test_commit_drift(self): self.assertEqual(select([{**BASE,"source_commit":"old"}],"door", "new")["reason"],"source_revision_unverified")
    def test_commit_match(self): self.assertEqual(select([{**BASE,"source_commit":"same"}],"door", "same")["decision"],"use")
    def test_no_replay(self): self.assertEqual(once_only({"completed":["x"]},"x")["decision"],"skip")
    def test_no_atomic_claim(self): self.assertEqual(once_only({"completed":[]},"x")["decision"],"review")
    def test_invalid_checkpoint(self): self.assertEqual(once_only({},"x")["decision"],"hold")
if __name__ == "__main__": unittest.main()
