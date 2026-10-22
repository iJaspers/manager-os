#!/usr/bin/env python3
"""Wit Documented Compensation Comparison 0.1.1.

Offline, input-driven comparison of guaranteed documented wages minus documented
commute costs, before all taxes. Never assumes benefits, overtime eligibility,
commute rate, current job openings, or pay entitlement. Uncertain offers cannot
be ranked. No applications or employer contact.
CLI: python tool.py --input offers.json
     python tool.py --self-test
Input: {"offers":[{"name":"A","source_ref":"signed offer or payroll record",
 "currency":"CAD","hourly_rate":"30","paid_regular_hours_per_week":"40",
 "paid_weeks_per_year":"52","guaranteed_ot_hours_per_week":"0",
 "documented_ot_multiplier":"1.5","documented_guaranteed_cash_per_year":"0",
 "round_trip_commute_km_per_day":"20","commute_days_per_week":"5",
 "commute_weeks_per_year":"48","documented_cost_per_km":"0.25",
 "annual_parking_cost":"0","annual_union_dues":"0",
 "round_trip_commute_hours_per_day":"1"}]}
"""
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 iJaspers. See LICENSE.
import argparse, json
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
TOOL_ID='wit.documented-compensation-comparison@0.1.1'
FIELDS=['hourly_rate','paid_regular_hours_per_week','paid_weeks_per_year','guaranteed_ot_hours_per_week','documented_ot_multiplier','documented_guaranteed_cash_per_year','round_trip_commute_km_per_day','commute_days_per_week','commute_weeks_per_year','documented_cost_per_km','annual_parking_cost','annual_union_dues','round_trip_commute_hours_per_day']
def _num(v):
    if isinstance(v,bool) or v is None or len(str(v))>64:return None
    try:
        n=Decimal(str(v))
        if not n.is_finite() or n < 0 or n > Decimal('1000000000'):return None
        return n
    except (InvalidOperation,ValueError,TypeError):return None
def _money(v):return str(v.quantize(Decimal('.01'),rounding=ROUND_HALF_UP))
def evaluate(doc):
    if not isinstance(doc,dict) or not isinstance(doc.get('offers'),list) or not doc['offers']:
        return {'status':'INVALID_INPUT','error':'Nonempty offers list required.','offers':[]}
    results=[]
    for offer in doc['offers']:
        if not isinstance(offer,dict):results.append({'status':'HOLD','issues':['Offer is not an object.']});continue
        name=offer.get('name'); issues=[]
        if not isinstance(name,str) or not name.strip():issues.append('Offer name missing')
        if offer.get('currency')!='CAD':issues.append('Currency must be CAD; no guessed FX conversions')
        if not isinstance(offer.get('source_ref'),str) or not offer['source_ref'].strip():issues.append('Employment compensation source evidence missing')
        vals={k:_num(offer.get(k)) for k in FIELDS}
        issues += ['Unknown/invalid: '+k for k,v in vals.items() if v is None]
        if vals['documented_ot_multiplier'] is not None and vals['documented_ot_multiplier']<1 and (vals['guaranteed_ot_hours_per_week'] or 0)>0:
            issues.append('OT multiplier below 1: verify employer evidence')
        if (vals['paid_weeks_per_year'] is not None and vals['paid_weeks_per_year']>52) or (vals['commute_weeks_per_year'] is not None and vals['commute_weeks_per_year']>52):issues.append('Week counts cannot exceed 52')
        if vals['round_trip_commute_hours_per_day'] is not None and vals['round_trip_commute_hours_per_day']>24: issues.append('Round-trip commute hours cannot exceed 24/day')
        if vals['commute_days_per_week'] is not None and vals['commute_days_per_week']>7: issues.append('Commute days cannot exceed 7/week')
        if all(vals[k] is not None for k in ['paid_regular_hours_per_week','guaranteed_ot_hours_per_week']) and vals['paid_regular_hours_per_week']+vals['guaranteed_ot_hours_per_week']>168:issues.append('Hours/week exceeds 168')
        if vals['guaranteed_ot_hours_per_week'] is not None and vals['guaranteed_ot_hours_per_week']>0 and offer.get('ot_guarantee_evidence') not in ('SIGNED_CONTRACT','PAYROLL_AGREEMENT'):
            issues.append('Guaranteed overtime requires exact documentary support')
        d={'name':name,'status':'HOLD_UNRANKED' if issues else 'INPUT_COMPLETE_SCENARIO','issues':issues,'annual_cash_before_tax':None,'annual_commute_dues_costs':None,'annual_cash_less_documented_costs_before_tax':None,'annual_commute_hours':None}
        if not issues:
            v=vals;r=v['hourly_rate']; regular=r*v['paid_regular_hours_per_week']*v['paid_weeks_per_year']
            ot=r*v['guaranteed_ot_hours_per_week']*v['documented_ot_multiplier']*v['paid_weeks_per_year']
            cash=regular+ot+v['documented_guaranteed_cash_per_year']
            costs=(v['round_trip_commute_km_per_day']*v['commute_days_per_week']*v['commute_weeks_per_year']*v['documented_cost_per_km']+v['annual_parking_cost']+v['annual_union_dues'])
            d.update(annual_cash_before_tax=_money(cash),annual_commute_dues_costs=_money(costs),annual_cash_less_documented_costs_before_tax=_money(cash-costs),annual_commute_hours=str((v['round_trip_commute_hours_per_day']*v['commute_days_per_week']*v['commute_weeks_per_year']).normalize()))
        results.append(d)
    names=[str(x.get('name')) for x in results]
    if len(set(names))!=len(names):
        for r in results:r['issues'].append('Duplicate offer name; unique offer identifiers required');r['status']='HOLD_UNRANKED'
    rankable=all(x['status']=='INPUT_COMPLETE_SCENARIO' for x in results) and len(results)>1
    return {'status':'COMPLETE_SCENARIOS_NOT_OFFER_VERIFICATION' if rankable else 'COMPARISON_HOLD_UNRANKED', 'offers':results,'ranked_offer_names':[x['name'] for x in sorted(results,key=lambda o:Decimal(o['annual_cash_less_documented_costs_before_tax']),reverse=True)] if rankable else [],'warning':'Scenario only. Not take-home pay; excludes taxes, noncash benefits, uncertain income, and employer/personal risk. Source evidence is caller-supplied, not independently verified.'}
def _tests():
    import copy
    o=dict(name='A',source_ref='documented',currency='CAD',hourly_rate='30',paid_regular_hours_per_week='40',paid_weeks_per_year='52',guaranteed_ot_hours_per_week='0',documented_ot_multiplier='1.5',documented_guaranteed_cash_per_year='0',round_trip_commute_km_per_day='20',commute_days_per_week='5',commute_weeks_per_year='48',documented_cost_per_km='0.25',annual_parking_cost='0',annual_union_dues='0',round_trip_commute_hours_per_day='1')
    assert evaluate({'offers':[o]})['offers'][0]['annual_cash_before_tax']=='62400.00'
    assert evaluate({'offers':[o]})['offers'][0]['annual_commute_dues_costs']=='1200.00'
    def c():return copy.deepcopy(o)
    x=c();x['hourly_rate']='-1';assert evaluate({'offers':[x]})['offers'][0]['status']=='HOLD_UNRANKED'
    x=c();del x['documented_cost_per_km'];assert evaluate({'offers':[x]})['offers'][0]['status']=='HOLD_UNRANKED'
    x=c();x['guaranteed_ot_hours_per_week']='2';assert evaluate({'offers':[x]})['offers'][0]['status']=='HOLD_UNRANKED'
    x=c();x['guaranteed_ot_hours_per_week']='2';x['ot_guarantee_evidence']='SIGNED_CONTRACT';assert evaluate({'offers':[x]})['offers'][0]['annual_cash_before_tax']=='67080.00'
    x=c();x['paid_weeks_per_year']='53';assert evaluate({'offers':[x]})['offers'][0]['status']=='HOLD_UNRANKED'
    x=c();x['commute_days_per_week']='8';assert evaluate({'offers':[x]})['offers'][0]['status']=='HOLD_UNRANKED'
    x=c();x['source_ref']='';assert evaluate({'offers':[x]})['offers'][0]['status']=='HOLD_UNRANKED'
    x=c();x['currency']='USD';assert evaluate({'offers':[x]})['offers'][0]['status']=='HOLD_UNRANKED'
    x=c();x['hourly_rate']='31';r=evaluate({'offers':[o,x]});assert not r['ranked_offer_names']
    x=c();x['name']='B';x['hourly_rate']='31';assert evaluate({'offers':[o,x]})['ranked_offer_names']==['B','A']
    assert evaluate({})['status']=='INVALID_INPUT'
    return 13
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path);p.add_argument('--self-test',action='store_true');a=p.parse_args()
    if a.self_test:print('PASS',TOOL_ID,_tests(),'functional checks')
    elif a.input:
        try:v=evaluate(json.loads(a.input.read_text(encoding='utf-8')))
        except (OSError,ValueError) as e:v={'status':'INVALID_INPUT','error':str(e)}
        print(json.dumps(v,indent=2))
    else:p.error('--input or --self-test required')
