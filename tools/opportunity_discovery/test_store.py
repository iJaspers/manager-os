import json
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
    def test_changed_status_invalidates_old_review_and_preserves_history(self):
        original = dict(self.item, status_checked=True, rules_checked=True, freshness_checked=True)
        store = Store(self.path)
        first, = store.ingest([original])
        self.assertEqual(first["gate"], "PASS")
        store.feedback(first["id"], "GOOD")
        closed, = store.ingest([dict(original, removed=True)])
        self.assertEqual(closed["decision"], "BLOCKED")
        self.assertIn("removed", closed["gate_reasons"])
        self.assertNotIn("feedback", closed)
        previous = json.loads(store.db.execute(
            "SELECT detail FROM events WHERE kind='OBSERVATION_CHANGED'"
        ).fetchone()[0])["prior"]
        self.assertEqual(previous["feedback"]["verdict"], "GOOD")
        store.close()
        store = Store(self.path)
        duplicate, = store.ingest([dict(original, removed=True)])
        self.assertTrue(duplicate["duplicate_observation"])
        self.assertEqual(store.event_count(), 3)
        replay, = store.ingest([original])
        self.assertEqual(replay["gate"], "NEEDS_REVIEW")
        self.assertFalse(replay["human_approved"])
        store.close()

    def test_text_revision_changes_identity_but_clock_drift_does_not(self):
        store = Store(self.path)
        first, = store.ingest([dict(self.item, source_text="first", freshness_days=8)])
        duplicate, = store.ingest([dict(self.item, source_text="first", freshness_days=9)])
        changed, = store.ingest([dict(self.item, source_text="second", freshness_days=9)])
        self.assertTrue(duplicate["duplicate_observation"])
        self.assertNotEqual(first["observation_sha256"], changed["observation_sha256"])
        self.assertEqual(store.event_count(), 2)
        store.close()

    def test_unbound_legacy_record_requires_one_review(self):
        store = Store(self.path)
        previous, = store.ingest([self.item])
        previous.pop("observation_sha256")
        with store.db:
            store.db.execute("UPDATE opportunities SET payload=?", (json.dumps(previous),))
        bound, = store.ingest([self.item])
        self.assertIn("changed observation requires review", bound["gate_reasons"])
        replay, = store.ingest([self.item])
        self.assertTrue(replay["duplicate_observation"])
        self.assertEqual(store.event_count(), 2)
        store.close()

    def test_requirement_change_holds_and_retains_prior_review(self):
        row = dict(id="local-use", status="SUPPORTED", evidence_index=0)
        original = dict(self.item, fit_requirements=[row])
        store = Store(self.path)
        first, = store.ingest([original])
        store.feedback(first["id"], "GOOD")
        revised = dict(original, fit_requirements=[dict(row, status="UNKNOWN", evidence_index=None)])
        updated, = store.ingest([revised])
        self.assertEqual(updated["decision"], "BLOCKED")
        self.assertIn("changed observation requires review", updated["gate_reasons"])
        self.assertNotIn("feedback", updated)
        history = json.loads(store.db.execute(
            "SELECT detail FROM events WHERE kind='OBSERVATION_CHANGED'"
        ).fetchone()[0])
        self.assertEqual(history["prior"]["feedback"]["verdict"], "GOOD")
        store.close()
        store = Store(self.path)
        self.assertTrue(store.ingest([revised])[0]["duplicate_observation"])
        self.assertEqual(store.event_count(), 3)
        store.close()

    def test_bad_input(self):
        s=Store(self.path)
        with self.assertRaises(ValueError):s.ingest({})
        s.close()

if __name__=="__main__":unittest.main()
