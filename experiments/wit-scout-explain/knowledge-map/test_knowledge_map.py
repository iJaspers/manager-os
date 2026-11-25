import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


class RoutingTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)
        shutil.copyfile(HERE / "knowledge_map.py", self.root / "knowledge_map.py")
        self.map = self.root / "topics.json"
        shutil.copyfile(HERE / "topics.json", self.map)

    def cli(self, topic):
        p = subprocess.run([sys.executable, "-I", "-B", str(self.root / "knowledge_map.py"), topic],
                           capture_output=True, text=True, cwd="/tmp", timeout=5)
        self.assertEqual(p.stderr, "")
        return p.returncode, json.loads(p.stdout)

    def test_normalized_query_and_exact_source_runtime(self):
        code, result = self.cli("  SOURCE    Coverage ")
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "ROUTED")
        self.assertEqual(result["matches"], [{"id": "context review", "state": "experimental",
            "source": "experiments/wit-scout-explain/context-review/README.md"}])

    def test_shared_alias_never_picks_a_winner(self):
        code, result = self.cli("scout")
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "AMBIGUOUS")
        self.assertEqual([r["id"] for r in result["matches"]], ["context review", "scout evidence"])

    def test_partial_alias_does_not_infer(self):
        code, result = self.cli("source")
        self.assertEqual((code, result["status"], result["matches"]), (0, "UNKNOWN", []))

    def test_bad_unmatched_record_holds_all_results(self):
        data = json.loads(self.map.read_text())
        data["records"][0]["source"] = "../private/example"
        self.map.write_text(json.dumps(data))
        self.assertEqual(self.cli("source coverage"), (2, {"status": "HOLD", "matches": []}))

    def test_unknown_status_does_not_claim_release(self):
        data = json.loads(self.map.read_text())
        data["records"][1]["state"] = "approved"
        self.map.write_text(json.dumps(data))
        self.assertEqual(self.cli("source coverage")[0], 2)

    def test_unavailable_local_map_holds(self):
        self.map.unlink()
        self.assertEqual(self.cli("source coverage")[0], 2)

    def test_oversized_map_holds(self):
        self.map.write_bytes(b" " * 65537)
        self.assertEqual(self.cli("source coverage")[0], 2)

    def test_non_integer_schema_holds(self):
        data = json.loads(self.map.read_text())
        data["schema"] = True
        self.map.write_text(json.dumps(data))
        self.assertEqual(self.cli("source coverage")[0], 2)

    def test_duplicate_keys_at_top_and_nested_hold(self):
        original = self.map.read_text()
        for text in (original.replace('"schema": 1', '"schema": 2, "schema": 1'),
                     original.replace('"id": "scout evidence"',
                                      '"id": "wrong", "id": "scout evidence"')):
            with self.subTest(text=text):
                self.assertNotEqual(text, original)
                self.map.write_text(text)
                self.assertEqual(self.cli("source coverage"),
                                 (2, {"status": "HOLD", "matches": []}))

    def test_normalizes_unicode_and_rejects_invisible_format(self):
        data = json.loads(self.map.read_text())
        data["records"][0]["aliases"].append("caf\u00e9")
        self.map.write_text(json.dumps(data))
        self.assertEqual(self.cli("CAFE\u0301")[1]["status"], "ROUTED")
        self.assertEqual(self.cli("source\u200b coverage")[0], 2)
        data["records"][0]["id"] += "\u202e"
        self.map.write_text(json.dumps(data))
        self.assertEqual(self.cli("source coverage")[0], 2)


if __name__ == "__main__":
    unittest.main()
