"""CLI acceptance checks on fictional inputs and disposable output files."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from _base import save_research_checkpoint
from demo_session import make_demo_session
from review import write_new

HERE = Path(__file__).resolve().parent


def run_cli(*args):
    return subprocess.run([sys.executable, "-B", str(HERE / "review.py"), *map(str, args)],
                          capture_output=True, text=True, timeout=15)


class ReviewCliTests(unittest.TestCase):
    def test_demo_is_labelled_fictional_and_preserves_failed_source(self):
        result = run_cli("--demo", "--include-source-details")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["origin"], "SYNTHETIC_DEMO")
        self.assertEqual(report["verdict"], "HOLD")
        self.assertIn("FETCH_FAILED", [row["fetch_state"] for row in report["context"]["sources"]])

    def test_checkpoint_requires_separate_anchors(self):
        result = run_cli("--checkpoint", "not-read.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires external digest", result.stderr)

    def test_demo_does_not_accept_checkpoint_anchors(self):
        result = run_cli("--demo", "--expected-sha256", "a" * 64)
        self.assertNotEqual(result.returncode, 0)

    def test_html_write_is_complete_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "review.html"
            first = run_cli("--demo", "--html", path)
            self.assertEqual(first.returncode, 0, first.stderr)
            original = path.read_bytes()
            self.assertTrue(original.startswith(b"<!doctype html>"))
            self.assertTrue(original.endswith(b"</html>"))
            self.assertNotIn(b"https://example.org", original)
            second = run_cli("--demo", "--include-source-details", "--html", path)
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual(path.read_bytes(), original)

    def test_output_symlink_is_refused_without_changing_target(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "keep.txt"
            target.write_text("unchanged")
            link = Path(directory) / "link.html"
            link.symlink_to(target)
            with self.assertRaises(FileExistsError):
                write_new(link, "replacement")
            self.assertEqual(target.read_text(), "unchanged")

    def test_real_checkpoint_path_uses_existing_recovery_contract(self):
        session = make_demo_session()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "checkpoint.json"
            digest = save_research_checkpoint(path, payload=session.payload, goal=session.goal,
                claims=session.claims, gathered=session.gathered,
                code_revision=session.code_revision, approved_urls=session.approved_urls)
            args = ["--checkpoint", path, "--expected-sha256", digest,
                    "--code-revision", session.code_revision]
            for url in session.approved_urls:
                args += ["--source", url]
            result = run_cli(*args)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["verdict"], "HOLD")
            self.assertEqual(report["memory_review"]["owner_confirmation"], "NOT_VERIFIED")
            self.assertEqual(report["context"]["sources"], [])
            path.write_bytes(path.read_bytes() + b" ")
            rejected = run_cli(*args)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("bytes changed", rejected.stderr)


if __name__ == "__main__":
    unittest.main()
