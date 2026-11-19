import tempfile
import unittest
from pathlib import Path
from store import Store

class StoreTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.path=Path(self.temp.name)/"records.sqlite"
        self.item={"url":"https://github.com/example/repo/issues/1","title":"Context loss","relevance":35,"help_request":25,"fit":25,"community":0,"verified_fit":True,"rules_checked":False,"status_checked":False,"freshness_checked":False,"help_intent_checked":True,"evidence_urls":["https://github.com/iJaspers/manager-os"]}
    def tearDown(self): self.temp.cleanup()
    def test_restart_persistence(self):
        s=Store(self.path); a=s.ingest([self.item])[0]; s.close()
        s=Store(self.path); self.assertEqual(s.list_records()[0]["id"],a["id"]);s.close()
    def test_replay_idempotent(self):
        s=Store(self.path);s.ingest([self.item]);r=s.ingest([self.item])[0]
        self.assertTrue(r["duplicate_observation"]);self.assertEqual(len(s.list_records()),1);self.assertEqual(s.event_count(),1);s.close()
    def test_feedback_survives_restart_and_replay(self):
        s=Store(self.path);i=s.ingest([self.item])[0]["id"];s.feedback(i,"BAD","not buyer intent");s.close()
        s=Store(self.path);s.ingest([self.item]);self.assertEqual(s.list_records()[0]["feedback"]["verdict"],"BAD");self.assertEqual(s.event_count(),2);s.close()
    def test_unsafe_posting_never_set(self):
        s=Store(self.path);s.ingest([self.item]);self.assertFalse(s.list_records()[0]["human_approved"]);self.assertIsNone(s.list_records()[0]["posted_url"]);s.close()
    def test_feedback_invalid(self):
        s=Store(self.path);i=s.ingest([self.item])[0]["id"]
        with self.assertRaises(ValueError):s.feedback(i,"POSTED")
        s.close()
    def test_feedback_unknown(self):
        s=Store(self.path)
        with self.assertRaises(KeyError):s.feedback("unknown","GOOD")
        s.close()
    def test_duplicate_in_batch(self):
        s=Store(self.path);out=s.ingest([self.item,self.item]);self.assertTrue(out[1]["duplicate_observation"]);s.close()
    def test_bad_input(self):
        s=Store(self.path)
        with self.assertRaises(ValueError):s.ingest({})
        s.close()

if __name__=="__main__":unittest.main()
