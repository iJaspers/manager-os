# SPDX-License-Identifier: MIT
# Copyright (c) 2026 iJaspers. See LICENSE.
import unittest, json, copy
from pathlib import Path
from tool import evaluate
class PublicTests(unittest.TestCase):
    def setUp(self): self.doc=json.loads((Path(__file__).parent/'example.json').read_text())
    def test_synthetic_pair(self):
        r=evaluate(self.doc); self.assertEqual(r['ranked_offer_names'],['Synthetic B','Synthetic A']);self.assertEqual(r['offers'][0]['annual_cash_before_tax'],'62400.00')
    def test_extreme_input_held(self):
        self.doc['offers'][0]['hourly_rate']='1e999';self.assertEqual(evaluate(self.doc)['ranked_offer_names'],[])
    def test_boolean_held(self):
        self.doc['offers'][0]['hourly_rate']=True;self.assertEqual(evaluate(self.doc)['ranked_offer_names'],[])
    def test_impossible_commute_held(self):
        self.doc['offers'][0]['round_trip_commute_hours_per_day']='24.1';self.assertEqual(evaluate(self.doc)['ranked_offer_names'],[])
    def test_duplicate_name_held(self):
        self.doc['offers'][1]['name']='Synthetic A';self.assertEqual(evaluate(self.doc)['ranked_offer_names'],[])
    def test_single_unranked(self):
        self.doc['offers']=self.doc['offers'][:1];self.assertEqual(evaluate(self.doc)['status'],'COMPARISON_HOLD_UNRANKED')
    def test_immutable(self):
        before=copy.deepcopy(self.doc);evaluate(self.doc);self.assertEqual(self.doc,before)
    def test_unknown_not_zero(self):
        del self.doc['offers'][0]['annual_parking_cost'];self.assertEqual(evaluate(self.doc)['ranked_offer_names'],[])
if __name__=='__main__':unittest.main()
