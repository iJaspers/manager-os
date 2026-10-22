// SPDX-License-Identifier: MIT
// Copyright (c) 2026 iJaspers. See LICENSE.
'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(__dirname+'/tool.html','utf8');const engine=html.split('// ENGINE_START')[1].split('// ENGINE_END')[0];const handler='const fmt='+html.split('// UI_START')[1].split('const fmt=')[1].split('// UI_END')[0];
const good={type:'hourly',pay:'20',weeks:'50',hours:'40',days:'5',commuteKm:'10',kmCost:'0.5',allowance:'0',oneWayMin:'15'};
let a={...good},b={...good,pay:'21'};const nodes={calculate:{},result:{textContent:''}};
const ctx={document:{getElementById:id=>nodes[id]},getRole:id=>id==='current'?a:b};vm.createContext(ctx);vm.runInContext(engine+'\n'+handler,ctx);
nodes.calculate.onclick();const original=nodes.result.textContent;
for(let i=0;i<25;i++){nodes.calculate.onclick();assert.equal(nodes.result.textContent,original)}
b={...good,pay:''};nodes.calculate.onclick();assert.match(nodes.result.textContent,/UNKNOWN/);assert.ok(!nodes.result.textContent.includes('Annual gross current:'));
b={...good,pay:'21'};nodes.calculate.onclick();assert.equal(nodes.result.textContent,original);
a={...good,type:'salary',pay:'1',weeks:'1',days:'1',commuteKm:'1e308',kmCost:'1',allowance:'0',oneWayMin:'0'};b={...a,pay:'1e308',commuteKm:'0'};nodes.calculate.onclick();assert.match(nodes.result.textContent,/UNKNOWN/);assert.match(nodes.result.textContent,/Numeric comparison range exceeded/);assert.ok(!nodes.result.textContent.includes('Infinity'));
console.log(JSON.stringify({passed:4,failed:0,checks:['25 identical UI-handler retries stable','invalid input replaces stale calculated text','valid retry restores prior result','overflow renders explicit range error and no Infinity'],scope:'actual handler with DOM stub, no browser capacity claim'}));
