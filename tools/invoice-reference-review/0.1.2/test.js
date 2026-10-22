// SPDX-License-Identifier: MIT
// Copyright (c) 2026 iJaspers. See LICENSE.
'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(__dirname+'/tool.html','utf8');
const engine=html.split('// ENGINE_START')[1].split('// ENGINE_END')[0];
const ctx={};vm.createContext(ctx);vm.runInContext(engine,ctx);let passed=0;
function test(name,fn){fn();passed++;console.log('PASS '+name)}

const run=(i,p)=>ctx.reconcileInvoices(i,p), inv='invoice_id,amount\nA,100.00', pay=x=>'invoice_id,amount,payment_id\n'+x;
test('exact candidate',()=>assert.equal(run(inv,pay('A,100.00,P1')).rows[0].status,'EXACT_CANDIDATE'));
test('partial candidate',()=>assert.equal(run(inv,pay('A,40.00,P1')).rows[0].status,'PARTIAL_CANDIDATE'));
test('overpayment exception',()=>assert.equal(run(inv,pay('A,101.00,P1')).rows[0].status,'OVERPAYMENT_EXCEPTION'));
test('missing payment',()=>assert.equal(run(inv,'invoice_id,amount,payment_id').rows[0].status,'NO_PAYMENT_EVIDENCE'));
test('orphan payment',()=>assert.equal(run(inv,pay('Z,10.00,P1')).rows[1].status,'ORPHAN_PAYMENT'));
test('missing reference',()=>assert.equal(run(inv,'invoice_id,amount\nA,100.00').rows[0].status,'REFERENCE_MISSING_REVIEW'));
test('duplicate invoice',()=>assert.equal(run(inv+'\nA,50.00',pay('A,100.00,P1')).rows[0].status,'HOLD_INVALID_INVOICE'));
test('invalid amount',()=>assert.equal(run('invoice_id,amount\nA,-1.00',pay('A,100.00,P1')).rows[0].status,'HOLD_INVALID_INVOICE'));
test('invalid date',()=>assert.equal(run('invoice_id,amount,date\nA,100.00,2030-02-30',pay('A,100.00,P1')).rows[0].status,'HOLD_INVALID_INVOICE'));
test('duplicate payment holds both invoices',()=>{let r=run(inv+'\nB,10.00',pay('A,100.00,DUP\nB,10.00,DUP'));assert.equal(r.rows.length,2);assert.ok(r.rows.every(x=>x.status==='HOLD_INVALID_PAYMENT'))});
test('duplicate header rejected',()=>assert.throws(()=>run('invoice_id,amount,amount\nA,100,200',pay('A,100.00,P1')),/Duplicate/));
test('unclosed quote rejected',()=>assert.throws(()=>ctx.csvRows('a,b\n"bad'),/Unclosed/));
test('spreadsheet formulas neutralized',()=>{for(let v of ['=1+1','+SUM(A1)','-1','@SUM(A1)','  =1','\t1'])assert.ok(ctx.csvCell(v).startsWith('"\''));assert.equal(ctx.csvCell('normal'),'"normal"');assert.equal(ctx.csvCell('a"b'),'"a""b"')});
test('aggregate overflow held',()=>assert.equal(run(inv,pay('A,90071992547409.90,P1\nA,90071992547409.90,P2')).rows[0].status,'HOLD_INVALID_PAYMENT'));
test('case-insensitive quoted ID',()=>assert.equal(run('invoice_id,amount\n"a,b",100.00',pay('"A,B",100.00,P1')).rows[0].status,'EXACT_CANDIDATE'));
console.log(JSON.stringify({passed,failed:0}));
