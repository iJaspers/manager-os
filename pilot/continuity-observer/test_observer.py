import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import observer

ROOT = Path(__file__).parent


def cases():
    return observer.load_json(ROOT / 'cases.json')


def observations():
    return observer.load_json(ROOT / 'synthetic_pass.json')


class ObserverTests(unittest.TestCase):
    def setUp(self):
        self.cases = observer.check_cases(cases())
        self.ids = {c['id'] for c in self.cases}
        self.obs = observer.check_observations(observations(), self.ids)

    def test_synthetic_demo_fields_only(self):
        out = observer.score(self.cases, self.obs)
        self.assertEqual(out['totals'], {'FIELD_MATCH': 10, 'FIELD_MISMATCH': 0, 'NOT_RUN': 0})
        self.assertEqual(out['evidence_level'], 'RESPONSE_FIELD_CHECK_ONLY')

    def test_actual_per_host_execution_not_claimed(self):
        report = observer.score(self.cases, self.obs)
        self.assertNotIn('EXECUTION_VERIFIED', json.dumps(report))
        self.assertIn('cannot verify actual tool execution', report['warning'])

    def test_prompt_export_excludes_oracle(self):
        packet = observer.prompts(self.cases)
        self.assertEqual(len(packet['prompts']), 10)
        self.assertNotIn('expected', json.dumps(packet))
        self.assertNotIn('forbidden_actions', json.dumps(packet))
        self.assertNotIn('synthetic_pass', json.dumps(packet))

    def test_decision_regression_detected(self):
        changed = json.loads(json.dumps(self.obs))
        changed['WIT_CASE_01']['decision_id'] = 'WRONG_ONE'
        output = observer.score(self.cases, changed)
        self.assertEqual(output['totals']['FIELD_MISMATCH'], 1)
        self.assertIn('decision_id', output['cases'][0]['checks_failed'])

    def test_source_ref_regression_detected(self):
        changed = json.loads(json.dumps(self.obs))
        changed['WIT_CASE_02']['source_ids'] = ['STALE_QUEUE']
        out = observer.score(self.cases, changed)
        self.assertEqual(out['totals']['FIELD_MISMATCH'], 1)

    def test_claimed_forbidden_action_detected(self):
        changed = json.loads(json.dumps(self.obs))
        changed['WIT_CASE_03']['claimed_actions'] = ['publish']
        out = observer.score(self.cases, changed)
        self.assertIn('forbidden claimed action', out['cases'][2]['checks_failed'])
        self.assertIn('unverified action claim (no tool trace is inspected)', out['cases'][2]['checks_failed'])

    def test_even_allowed_action_claim_not_verified(self):
        changed = json.loads(json.dumps(self.obs))
        changed['WIT_CASE_03']['claimed_actions'] = ['write']
        out = observer.score(self.cases, changed)
        self.assertEqual(out['totals']['FIELD_MISMATCH'], 1)

    def test_missing_observation_is_not_run(self):
        changed = dict(self.obs)
        del changed['WIT_CASE_10']
        self.assertEqual(observer.score(self.cases, changed)['totals']['NOT_RUN'], 1)

    def test_extra_response_field_rejected(self):
        changed = json.loads(json.dumps(observations()))
        changed['responses'][0]['response']['execute'] = 'send-email'
        with self.assertRaises(observer.InvalidInput):
            observer.check_observations(changed, self.ids)

    def test_unexpected_observation_id_rejected(self):
        changed = json.loads(json.dumps(observations()))
        changed['responses'][0]['case_id'] = 'WIT_CASE_99'
        with self.assertRaises(observer.InvalidInput):
            observer.check_observations(changed, self.ids)

    def test_duplicate_observation_id_rejected(self):
        changed = json.loads(json.dumps(observations()))
        changed['responses'][1]['case_id'] = 'WIT_CASE_01'
        with self.assertRaises(observer.InvalidInput):
            observer.check_observations(changed, self.ids)

    def test_duplicate_case_rejected(self):
        changed = cases()
        changed['cases'][1]['id'] = 'WIT_CASE_01'
        with self.assertRaises(observer.InvalidInput):
            observer.check_cases(changed)

    def test_unknown_context_source_rejected(self):
        changed = cases()
        changed['cases'][0]['expected']['source_ids'] = ['NOT_IN_CONTEXT']
        with self.assertRaises(observer.InvalidInput):
            observer.check_cases(changed)

    def test_duplicate_context_source_rejected(self):
        changed = cases()
        changed['cases'][0]['context'][1]['id'] = 'CURRENT_PLAN'
        with self.assertRaises(observer.InvalidInput):
            observer.check_cases(changed)

    def test_unknown_action_name_rejected(self):
        changed = observations()
        changed['responses'][0]['response']['claimed_actions'] = ['force_submit']
        with self.assertRaises(observer.InvalidInput):
            observer.check_observations(changed, self.ids)

    def test_oversized_input_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'huge.json'
            p.write_bytes(b'x' * (observer.MAX_BYTES + 1))
            with self.assertRaises(observer.InvalidInput):
                observer.load_json(p)

    def test_duplicate_json_key_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'bad.json'
            p.write_text('{"version": 1, "version": 2}', encoding='utf-8')
            with self.assertRaises(observer.InvalidInput):
                observer.load_json(p)

    def test_invalid_encoding_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'bad.json'
            p.write_bytes(b'\xff\xff')
            with self.assertRaises(observer.InvalidInput):
                observer.load_json(p)

    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'alias.json'
            p.symlink_to(ROOT / 'cases.json')
            with self.assertRaises(observer.InvalidInput):
                observer.load_json(p)

    def test_nan_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'bad.json'
            p.write_text('{"value": NaN}', encoding='utf-8')
            with self.assertRaises(observer.InvalidInput):
                observer.load_json(p)

    def test_strict_status_rejected(self):
        changed = observations()
        changed['responses'][0]['response']['status'] = 'POSTED'
        with self.assertRaises(observer.InvalidInput):
            observer.check_observations(changed, self.ids)

    def test_cli_pass_output(self):
        run = subprocess.run([sys.executable, str(ROOT / 'observer.py'), 'score', '--cases', str(ROOT / 'cases.json'), '--observations', str(ROOT / 'synthetic_pass.json')], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0)
        self.assertEqual(json.loads(run.stdout)['totals']['FIELD_MATCH'], 10)

    def test_cli_expected_failure_exit(self):
        run = subprocess.run([sys.executable, str(ROOT / 'observer.py'), 'score', '--cases', str(ROOT / 'cases.json'), '--observations', str(ROOT / 'synthetic_fail.json')], capture_output=True, text=True)
        self.assertEqual(run.returncode, 1)
        self.assertEqual(json.loads(run.stdout)['totals']['FIELD_MISMATCH'], 2)

    def test_cli_incomplete_exit(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'partial.json'
            x = observations()
            x['responses'] = x['responses'][:1]
            p.write_text(json.dumps(x), encoding='utf-8')
            run = subprocess.run([sys.executable, str(ROOT / 'observer.py'), 'score', '--cases', str(ROOT / 'cases.json'), '--observations', str(p)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 3)
            self.assertEqual(json.loads(run.stdout)['totals']['NOT_RUN'], 9)

    def test_cli_unexpected_arguments_rejected(self):
        run = subprocess.run([sys.executable, str(ROOT / 'observer.py'), 'prompts', '--cases', str(ROOT / 'cases.json'), '--observations', str(ROOT / 'synthetic_pass.json')], capture_output=True, text=True)
        self.assertEqual(run.returncode, 2)
        self.assertIn('INVALID_INPUT', run.stderr)


if __name__ == '__main__':
    unittest.main()
