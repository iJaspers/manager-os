import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from handoff import evaluate
ROOT=Path(__file__).parent

class PublicBoundary(unittest.TestCase):
    def data(self):return json.loads((ROOT/'example.json').read_text())
    def test_non_object(self):self.assertEqual(evaluate([])['status'],'HOLD')
    def test_invalid_time(self):
        d=self.data();d['source_observed_at']='yesterday';self.assertIn('INVALID_OBSERVATION_TIME',evaluate(d)['issues'])
    def test_timezone_required(self):
        d=self.data();d['source_observed_at']='2026-11-03';self.assertEqual(evaluate(d)['status'],'HOLD')
    def test_unknown_fields(self):
        d=self.data();d['extra']='private';self.assertEqual(evaluate(d)['status'],'HOLD');self.assertNotIn('private',json.dumps(evaluate(d)))
    def test_boolean_strings_not_approval(self):
        d=self.data();d['claim_resolved']=True;d['owner_approval_evidence']='yes';self.assertEqual(evaluate(d)['status'],'HOLD')
    def test_changed_evidence_does_not_accept_or_reopen(self):
        d=self.data();d['source_state']='DONE';d['new_evidence_changes_answer']=True;self.assertEqual(evaluate(d)['status'],'REVIEWABLE_HANDOFF_PROPOSAL')
    def test_insecure_link(self):
        d=self.data();d['source_task']='http://example.invalid';self.assertIn('INSECURE_SOURCE_LINK',evaluate(d)['issues'])
    def test_oversize_field(self):
        d=self.data();d['proposal']='x'*4097;self.assertEqual(evaluate(d)['status'],'HOLD')
    def test_oversize_evidence_list(self):
        d=self.data();d['evidence_refs']=['fixture:'+str(i) for i in range(51)];self.assertEqual(evaluate(d)['status'],'HOLD')
    def run_cli(self,content=None,link=False,missing=False):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'input.json'
            if not missing:path.write_bytes(content or json.dumps(self.data()).encode())
            if link:
                alias=Path(directory)/'alias.json';alias.symlink_to(path);path=alias
            return subprocess.run([sys.executable,str(ROOT/'handoff.py'),str(path)],capture_output=True,text=True,timeout=5)
    def test_cli_positive(self):
        p=self.run_cli();self.assertEqual(p.returncode,0);self.assertEqual(json.loads(p.stdout)['status'],'REVIEWABLE_HANDOFF_PROPOSAL')
    def test_cli_held_is_nonzero(self):
        p=self.run_cli(b'{}');self.assertEqual(p.returncode,2);self.assertEqual(json.loads(p.stdout)['status'],'HOLD')
    def test_cli_duplicate_keys(self):
        p=self.run_cli(b'{"owner":"a","owner":"b"}');self.assertEqual(p.returncode,2);self.assertIn('INVALID_INPUT',json.loads(p.stdout)['issues'])
    def test_cli_oversize(self):self.assertEqual(self.run_cli(b'x'*65537).returncode,2)
    def test_cli_invalid_utf8(self):self.assertEqual(self.run_cli(bytes([255])).returncode,2)
    def test_cli_symlink(self):self.assertEqual(self.run_cli(link=True).returncode,2)
    def test_cli_missing_does_not_reflect_path(self):
        p=self.run_cli(missing=True);self.assertEqual(p.returncode,2);self.assertNotIn('input.json',p.stdout+p.stderr)

if __name__=='__main__':unittest.main()
