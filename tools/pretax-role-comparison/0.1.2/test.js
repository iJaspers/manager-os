// SPDX-License-Identifier: MIT
// Copyright (c) 2026 iJaspers. See LICENSE.
'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(__dirname+'/tool.html','utf8');
const engine=html.split('// ENGINE_START')[1].split('// ENGINE_END')[0];
const ctx={};vm.createContext(ctx);vm.runInContext(engine,ctx);let passed=0;
function test(name,fn){fn();passed++;console.log('PASS '+name)}

const good={type:'hourly',pay:'20',weeks:'50',hours:'40',days:'5',commuteKm:'10',kmCost:'0.5',allowance:'0',oneWayMin:'15'};
const change=x=>({...good,...x});
test('hourly arithmetic',()=>{const r=ctx.compCase(good);assert.equal(r.annualBase,40000);assert.equal(r.commuteCash,1250);assert.equal(r.annualNetOfCommutePretax,38750);assert.equal(r.commuteHours,125)});
test('salary arithmetic',()=>assert.equal(ctx.compCase(change({type:'salary',pay:'50000',hours:''})).annualNetOfCommutePretax,48750));
test('difference',()=>assert.equal(ctx.compareRoles(good,change({type:'salary',pay:'50000'})).annualDifference,10000));
test('blank unknown',()=>assert.equal(ctx.compCase(change({allowance:''})).status,'UNKNOWN'));
test('negative rejected',()=>assert.equal(ctx.compCase(change({pay:'-1'})).status,'UNKNOWN'));
test('boolean and object rejected',()=>{assert.equal(ctx.numberOrNull(true),null);assert.equal(ctx.numberOrNull({}),null)});
test('invalid weeks',()=>assert.equal(ctx.compCase(change({weeks:'53'})).status,'UNKNOWN'));
test('overflow rejected',()=>assert.equal(ctx.compCase(change({pay:'1e308'})).status,'UNKNOWN'));
test('unknown comparison unranked',()=>assert.equal(ctx.compareRoles(good,change({kmCost:''})).status,'UNKNOWN'));
test('input not mutated',()=>{const before=JSON.stringify(good);ctx.compareRoles(good,good);assert.equal(JSON.stringify(good),before)});
test('difference overflow held despite finite scenarios',()=>{const a={type:'salary',pay:'1',weeks:'1',hours:'0',days:'1',commuteKm:'1e308',kmCost:'1',allowance:'0',oneWayMin:'0'},b={...a,pay:'1e308',commuteKm:'0'};assert.equal(ctx.compareRoles(a,b).status,'UNKNOWN')});
test('valid comparison recovers after overflow',()=>{const a={type:'hourly',pay:'20',weeks:'50',hours:'40',days:'5',commuteKm:'10',kmCost:'0.5',allowance:'0',oneWayMin:'15'};assert.equal(ctx.compareRoles(a,{...a,pay:'21'}).annualDifference,2000)});
console.log(JSON.stringify({passed,failed:0}));
