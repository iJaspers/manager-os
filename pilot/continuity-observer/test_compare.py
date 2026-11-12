import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import observer

ROOT = Path(__file__).parent


def load(name):
    return observer.load_json(ROOT / name)


class CompareTests(unittest.TestCase):
    def setUp(self):
        self.cases = observer.check_cases(load("cases.json"))
        self.ids = {case["id"] for case in self.cases}
        self.good = observer.check_observations(load("synthetic_pass.json"), self.ids)
        self.bad = observer.check_observations(load("synthetic_fail.json"), self.ids)

    def command(self, *argv):
        return subprocess.run([sys.executable, str(ROOT / "observer.py"), *argv],
                              capture_output=True, text=True, timeout=10)

    def test_unmodified_pair_is_not_misclassified_as_improvement(self):
        out = observer.compare(self.cases, self.good, self.good)
        self.assertEqual(out["transitions"]["UNCHANGED_MATCH"], 10)
        self.assertEqual(out["transitions"]["IMPROVEMENT"], 0)

    def test_injected_errors_are_regressions(self):
        out = observer.compare(self.cases, self.good, self.bad)
        self.assertEqual(out["transitions"]["REGRESSION"], 2)
        self.assertEqual(out["candidate_totals"]["FIELD_MISMATCH"], 2)
        self.assertEqual(out["evidence_level"], "RECORDED_FIELD_COMPARISON_ONLY")

    def test_repaired_fields_are_improvements_without_real_host_claim(self):
        out = observer.compare(self.cases, self.bad, self.good)
        self.assertEqual(out["transitions"]["IMPROVEMENT"], 2)
        self.assertNotIn("EXECUTION_VERIFIED", json.dumps(out))
        self.assertIn("NOT independent host tests", out["warning"])

    def test_both_mismatches_are_not_improvements(self):
        out = observer.compare(self.cases, self.bad, self.bad)
        self.assertEqual(out["transitions"]["UNCHANGED_MISMATCH"], 2)

    def test_unobserved_baseline_is_incomplete_not_improvement(self):
        partial = dict(self.good)
        partial.pop("WIT_CASE_01")
        out = observer.compare(self.cases, partial, self.good)
        self.assertEqual(out["transitions"]["INCOMPLETE"], 1)
        self.assertEqual(out["transitions"]["IMPROVEMENT"], 0)

    def test_unobserved_candidate_is_incomplete_not_regression(self):
        partial = dict(self.good)
        partial.pop("WIT_CASE_01")
        out = observer.compare(self.cases, self.good, partial)
        self.assertEqual(out["transitions"]["INCOMPLETE"], 1)
        self.assertEqual(out["transitions"]["REGRESSION"], 0)

    def test_unverified_claim_is_regression(self):
        altered = json.loads(json.dumps(self.good))
        altered["WIT_CASE_01"]["claimed_actions"] = ["write"]
        out = observer.compare(self.cases, self.good, altered)
        self.assertEqual(out["transitions"]["REGRESSION"], 1)
        self.assertIn("unverified action claim (no tool trace is inspected)",
                      out["cases"][0]["candidate_checks_failed"])

    def test_source_spoof_is_detected(self):
        altered = json.loads(json.dumps(self.good))
        altered["WIT_CASE_01"]["source_ids"] = ["FAKE_SOURCE"]
        out = observer.compare(self.cases, self.good, altered)
        self.assertEqual(out["transitions"]["REGRESSION"], 1)
        self.assertIn("source_ids (claims only, not verified retrieval)",
                      out["cases"][0]["candidate_checks_failed"])

    def test_cli_comparison_regression_not_green(self):
        proc = self.command("compare", "--cases", str(ROOT / "cases.json"),
                            "--baseline", str(ROOT / "synthetic_pass.json"),
                            "--candidate", str(ROOT / "synthetic_fail.json"))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["transitions"]["REGRESSION"], 2)

    def test_cli_comparison_corrected_can_be_green_but_scope_limited(self):
        proc = self.command("compare", "--cases", str(ROOT / "cases.json"),
                            "--baseline", str(ROOT / "synthetic_fail.json"),
                            "--candidate", str(ROOT / "synthetic_pass.json"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["transitions"]["IMPROVEMENT"], 2)

    def test_cli_comparison_missing_candidate_not_green(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "partial.json"
            o = load("synthetic_pass.json")
            o["responses"] = o["responses"][:-1]
            f.write_text(json.dumps(o), encoding="utf-8")
            proc = self.command("compare", "--cases", str(ROOT / "cases.json"),
                                "--baseline", str(ROOT / "synthetic_pass.json"),
                                "--candidate", str(f))
            self.assertEqual(proc.returncode, 3, proc.stderr)
            self.assertEqual(json.loads(proc.stdout)["transitions"]["INCOMPLETE"], 1)

    def test_cli_comparison_missing_baseline_not_green(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "partial.json"
            o = load("synthetic_pass.json")
            o["responses"] = o["responses"][:-1]
            f.write_text(json.dumps(o), encoding="utf-8")
            proc = self.command("compare", "--cases", str(ROOT / "cases.json"),
                                "--baseline", str(f),
                                "--candidate", str(ROOT / "synthetic_pass.json"))
            self.assertEqual(proc.returncode, 3, proc.stderr)
            self.assertEqual(json.loads(proc.stdout)["transitions"]["INCOMPLETE"], 1)

    def test_compare_rejects_ambiguous_observation_flag(self):
        proc = self.command("compare", "--cases", str(ROOT / "cases.json"),
                            "--baseline", str(ROOT / "synthetic_pass.json"),
                            "--candidate", str(ROOT / "synthetic_pass.json"),
                            "--observations", str(ROOT / "synthetic_pass.json"))
        self.assertEqual(proc.returncode, 2)
        self.assertIn("INVALID_INPUT", proc.stderr)

    def test_score_rejects_comparison_flags(self):
        proc = self.command("score", "--cases", str(ROOT / "cases.json"),
                            "--observations", str(ROOT / "synthetic_pass.json"),
                            "--candidate", str(ROOT / "synthetic_pass.json"))
        self.assertEqual(proc.returncode, 2)

    def test_prompts_do_not_leak_oracle_after_change(self):
        proc = self.command("prompts", "--cases", str(ROOT / "cases.json"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        packet = json.loads(proc.stdout)
        self.assertNotIn("expected", json.dumps(packet))
        self.assertNotIn("forbidden_actions", json.dumps(packet))

    def test_directory_cannot_be_used_as_input(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(observer.InvalidInput):
                observer.load_json(d)

    def test_fifo_cannot_block_input_reader(self):
        if not hasattr(os, "mkfifo"):
            self.skipTest("requires POSIX FIFO")
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "pipe"
            os.mkfifo(f)
            with self.assertRaises(observer.InvalidInput):
                observer.load_json(f)

    def test_input_exact_byte_limit_is_allowed(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "max.json"
            contents = b"{}" + b" " * (observer.MAX_BYTES - 2)
            self.assertEqual(len(contents), observer.MAX_BYTES)
            f.write_bytes(contents)
            self.assertEqual(observer.load_json(f), {})

    def test_input_exceeds_byte_limit_even_with_valid_json(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "too_big.json"
            f.write_bytes(b"{}" + b" " * (observer.MAX_BYTES - 1))
            with self.assertRaises(observer.InvalidInput):
                observer.load_json(f)

    def test_incomplete_and_bad_candidate_exit_prefers_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "partial_bad.json"
            o = load("synthetic_fail.json")
            o["responses"] = o["responses"][:-1]
            f.write_text(json.dumps(o), encoding="utf-8")
            proc = self.command("compare", "--cases", str(ROOT / "cases.json"),
                                "--baseline", str(ROOT / "synthetic_pass.json"),
                                "--candidate", str(f))
            self.assertEqual(proc.returncode, 1)
            out = json.loads(proc.stdout)
            self.assertGreater(out["transitions"]["INCOMPLETE"], 0)
            self.assertGreater(out["candidate_totals"]["FIELD_MISMATCH"], 0)


if __name__ == "__main__":
    unittest.main()
