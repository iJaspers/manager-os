# SPDX-License-Identifier: MIT
# Copyright (c) 2026 iJaspers. See LICENSE.
#!/usr/bin/env python3
import importlib.util,json,pathlib,sys,tempfile,unittest
path=pathlib.Path(__file__).with_name('tool.py');spec=importlib.util.spec_from_file_location('candidate',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
example=json.loads((path.parent/'example.json').read_text())['offers'][0]
class Boundaries(unittest.TestCase):
    def load(self,raw):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'input.json';p.write_bytes(raw);return m.load_input(p)
    def test_10000_offers_accepted(self):
        r=m.evaluate({'offers':[{**example,'name':str(i)} for i in range(10000)]});self.assertEqual(len(r['ranked_offer_names']),10000)
    def test_10001_offers_rejected(self):self.assertEqual(m.evaluate({'offers':[example]*10001})['status'],'INVALID_INPUT')
    def test_exact_8MiB_accepted(self):
        prefix=json.dumps({'offers':[example]},separators=(',',':'))[:-1]+',"padding":"';suffix='"}';n=8*1024*1024-len(prefix.encode())-len(suffix);raw=(prefix+'a'*n+suffix).encode();self.assertEqual(len(raw),8*1024*1024);self.assertEqual(m.evaluate(self.load(raw))['offers'][0]['status'],'INPUT_COMPLETE_SCENARIO')
    def test_over_8MiB_rejected(self):
        with self.assertRaisesRegex(ValueError,'8 MiB'):self.load(b' '*(8*1024*1024+1))
    def test_duplicate_root_keys_rejected(self):
        with self.assertRaisesRegex(ValueError,'Duplicate'):self.load(b'{"offers":[],"offers":[{}]}')
    def test_duplicate_nested_keys_rejected(self):
        with self.assertRaisesRegex(ValueError,'Duplicate'):self.load(b'{"offers":[{"name":"A","name":"B"}]}')
    def test_depth_64_accepted_by_parser(self):self.load(b'['*64+b'0'+b']'*64)
    def test_depth_65_rejected(self):
        with self.assertRaisesRegex(ValueError,'64 levels'):self.load(b'['*65+b'0'+b']'*65)
    def test_braces_and_escapes_in_strings(self):self.assertEqual(self.load(b'{"padding":"[\\\"{\\\\}"}'),{'padding':'["{\\}'})
    def test_invalid_UTF8_rejected(self):
        with self.assertRaises(ValueError):self.load(b'\xff')
    def test_1024_name_accepted(self):self.assertEqual(m.evaluate({'offers':[{**example,'name':'A'*1024}]})['offers'][0]['status'],'INPUT_COMPLETE_SCENARIO')
    def test_1025_name_held_without_echo(self):
        r=m.evaluate({'offers':[{**example,'name':'A'*1025}]})['offers'][0];self.assertEqual(r['status'],'HOLD_UNRANKED');self.assertLess(len(r['name']),100)
    def test_1025_source_held(self):self.assertEqual(m.evaluate({'offers':[{**example,'source_ref':'A'*1025}]})['offers'][0]['status'],'HOLD_UNRANKED')
if __name__ == "__main__": unittest.main()
