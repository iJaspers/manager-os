# SPDX-License-Identifier: MIT
# Copyright (c) 2026 iJaspers. See LICENSE.
import json
import unittest
from pathlib import Path
from tool import calculate, InputError

SAMPLE = json.loads((Path(__file__).with_name('example.json')).read_text())

class BasketTests(unittest.TestCase):
    def test_example_total_and_pantry(self):
        result = calculate(SAMPLE)
        self.assertEqual(result['status'], 'WITHIN_BUDGET')
        self.assertEqual(result['known_basket_total_cad'], '9.67')
        self.assertEqual(result['lines'][0]['pantry_used'], 100)
        self.assertEqual(result['lines'][1]['pantry_used'], 200)
    def test_missing_price_is_not_fake_zero(self):
        d = json.loads(json.dumps(SAMPLE))
        d['offers'] = [x for x in d['offers'] if x['item'] != 'beans']
        result = calculate(d)
        self.assertEqual(result['status'], 'UNKNOWN_MISSING_PRICE')
        self.assertFalse(result['total_is_complete'])
    def test_over_budget(self):
        d = json.loads(json.dumps(SAMPLE)); d['budget_cad'] = '6.00'
        self.assertEqual(calculate(d)['status'], 'OVER_BUDGET')
    def test_invalid_money(self):
        d = json.loads(json.dumps(SAMPLE)); d['budget_cad'] = 'NaN'
        with self.assertRaises(InputError): calculate(d)
    def test_negative_ingredient(self):
        d = json.loads(json.dumps(SAMPLE)); d['recipes'][0]['ingredients'][0]['qty'] = -1
        with self.assertRaises(InputError): calculate(d)
    def test_duplicate_pantry_rejected(self):
        d = json.loads(json.dumps(SAMPLE)); d['pantry'].append(d['pantry'][0])
        with self.assertRaises(InputError): calculate(d)
    def test_bad_identifier_rejected(self):
        d = json.loads(json.dumps(SAMPLE)); d['recipes'][0]['id'] = '../../secrets'
        with self.assertRaises(InputError): calculate(d)
    def test_unknown_recipe_rejected(self):
        d = json.loads(json.dumps(SAMPLE)); d['plan'][0]['recipe'] = 'nonexistent'
        with self.assertRaises(InputError): calculate(d)
    def test_pantry_covers_everything(self):
        d = json.loads(json.dumps(SAMPLE))
        d['pantry']=[{'item':'rice','unit':'g','qty':10000},{'item':'beans','unit':'g','qty':10000},{'item':'tortilla','unit':'each','qty':10000}]
        d['offers']=[]
        self.assertEqual(calculate(d)['known_basket_total_cad'], '0.00')
        self.assertEqual(calculate(d)['status'], 'WITHIN_BUDGET')
    def test_unit_mismatch_never_subtracts_stock(self):
        d = json.loads(json.dumps(SAMPLE))
        d['pantry'][0]['unit'] = 'ml'
        line = next(x for x in calculate(d)['lines'] if x['item']=='rice')
        self.assertEqual(line['pantry_used'],0)
    def test_cheapest_total_not_cheapest_unit(self):
        d = json.loads(json.dumps(SAMPLE))
        d['offers'].append({'item':'rice','unit':'g','pack_qty':10000,'price_cad':'4.00','store':'store_c'})
        line = next(x for x in calculate(d)['lines'] if x['item']=='rice')
        self.assertEqual(line['cost_cad'], '2.40')
    def test_missing_lists_held(self):
        with self.assertRaises(InputError): calculate({'budget_cad':'20.00'})
    def test_empty_plan_held(self):
        d = json.loads(json.dumps(SAMPLE)); d['plan'] = []
        with self.assertRaises(InputError): calculate(d)
    def test_null_offer_row_held(self):
        d = json.loads(json.dumps(SAMPLE)); d['offers'] = [None]
        with self.assertRaises(InputError): calculate(d)
    def test_empty_ingredients_held(self):
        d = json.loads(json.dumps(SAMPLE)); d['recipes'][0]['ingredients'] = []
        with self.assertRaises(InputError): calculate(d)
    def test_offer_count_held(self):
        d = json.loads(json.dumps(SAMPLE)); d['offers'] = d['offers'] * 251
        with self.assertRaises(InputError): calculate(d)
    def test_large_cents_formatted_exactly(self):
        from tool import money
        self.assertEqual(money(9999999999999999991), '99999999999999999.91')
if __name__ == '__main__': unittest.main()
