# SPDX-License-Identifier: MIT
# Copyright (c) 2026 iJaspers. See LICENSE.
import json, tempfile, unittest
from pathlib import Path
from tool import calculate, load_input, InputError
BASE=json.loads(Path(__file__).with_name('example.json').read_text())
class Boundaries(unittest.TestCase):
    def load(self,raw):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'input.json';p.write_bytes(raw);return load_input(p)
    def test_exact_byte_limit(self):
        prefix=json.dumps(BASE,separators=(',',':'))[:-1]+',"padding":"';suffix='"}';raw=(prefix+'a'*(1048576-len(prefix.encode())-len(suffix))+suffix).encode();self.assertEqual(len(raw),1048576);self.assertEqual(calculate(self.load(raw))['known_basket_total_cad'],'9.67')
    def test_over_byte_limit(self):
        with self.assertRaisesRegex(InputError,'1 MiB'):self.load(b' '*(1048577))
    def test_multibyte_limit(self):
        with self.assertRaisesRegex(InputError,'1 MiB'):self.load(('界'*400000).encode())
    def test_depth_limit(self):
        with self.assertRaisesRegex(InputError,'32 levels'):self.load(b'['*33+b'0'+b']'*33)
    def test_duplicate_key(self):
        with self.assertRaisesRegex(InputError,'Duplicate'):self.load(b'{"offers":[],"offers":[]}')
    def test_invalid_utf8(self):
        with self.assertRaises(ValueError):self.load(b'\xff')
    def test_empty_input(self):
        with self.assertRaises(ValueError):self.load(b'')
    def test_repeated_results_unchanged(self):
        raw=json.dumps(BASE);expected=calculate(BASE)
        for _ in range(100):self.assertEqual(calculate(BASE),expected)
        self.assertEqual(json.dumps(BASE),raw)
    def test_invalid_to_valid_recovery(self):
        for _ in range(100):
            with self.assertRaises(InputError):calculate({'budget_cad':'20.00'})
            self.assertEqual(calculate(BASE)['known_basket_total_cad'],'9.67')
if __name__=='__main__': unittest.main()
