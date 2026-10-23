// SPDX-License-Identifier: MIT
// Copyright (c) 2026 iJaspers. See LICENSE.
'use strict';
const fs = require('fs'), assert = require('assert'), vm=require('vm');
const path = process.argv[2] || __dirname+'/tool.html';
const html = fs.readFileSync(path, 'utf8');
const match=html.match(/<script>([\s\S]*?)<\/script>/);
assert(match,'single inline script');
const code=match[1];
new vm.Script(code);
function simulate(opening,entries){
 const nodes={starting:{value:opening},entries:{value:entries},result:{textContent:''},calc:{addEventListener:(action,handler)=>{if(action==='click')cb=handler;}}};
 let cb=()=>{throw Error('No handler attached')};
 const context={document:{getElementById:id=>nodes[id]},Error,BigInt,Set,Date,Number,RegExp};
 vm.runInNewContext(code,context,{timeout:2000});
 cb();
 return nodes.result.textContent;
}
let n=0;
function check(title,opening,entries,has,absent=[]){const actual=simulate(opening,entries);for(const s of has) assert(actual.includes(s),`${title}: expected ${s} in ${actual}`);for(const s of absent)assert(!actual.includes(s),`${title}: unexpected ${s}`);console.log('PASS',++n,title);return actual;}
check('new labels identify same-day possible gap','$50.00'.slice(1),'2026-10-20, -70, Rent\n2026-10-20, 70, Paycheque',['NO PROJECTED DAY-END GAP','SAME-DAY DEBIT-FIRST BUFFER: $20.00','Rent: -$70.00','Paycheque: $70.00','First possible debit-first gap (2026-10-20): Rent -$70.00']);
check('legacy two-column lines retained','500','2026-10-21, -125.00\n2026-10-23, 250.00',['Entry 1: -$125.00','Entry 2: $250.00','Final projected balance: $625.00']);
check('labels do not affect math','50.00','2026-10-20, -70.01, Bill A\n2026-10-20, 70.00, Deposit B',['NO PROJECTED DAY-END GAP','SAME-DAY DEBIT-FIRST BUFFER: $20.01','Final projected balance: $49.99']);
check('negative starting balance explained','-5.00','2026-10-20, 10.00, Payment',['DAY-END GAP: $5.00','First gap: before the first listed date','Final projected balance: $5.00']);
check('empty label held','50','2026-10-20, -30,   ',['HOLD: Line 1 label']);
check('HTML markup label rejected and not echoed','50','2026-10-20, -30, <img src=x onerror=alert(1)>',['HOLD: Line 1 label'],['<img']);
check('email-like label rejected','50','2026-10-20, -30, me@example.com',['HOLD: Line 1 label'],['me@example.com']);
check('account-like label rejected','50','2026-10-20, -30, Account 1234567890',['HOLD: Line 1 label'],['1234567890']);
check('extra comma rejected','50','2026-10-20, -30, Gas, Extra',['HOLD: Line 1 needs date, amount, optional label']);
check('malformed money denied','50','2026-10-20, -30.123, Rent',['HOLD: Use plain dollars']);
check('invalid calendar date denied','50','2026-02-30, -30, Rent',['HOLD: Invalid date']);
check('no entries denied','50',' ',['HOLD: Enter at least one dated entry']);
check('too many entries denied','50',Array(21).fill('2026-10-20, -1, Rent').join('\n'),['HOLD: Maximum 20 lines']);
assert(html.includes("connect-src 'none'") && html.includes("form-action 'none'") && html.includes("default-src 'none'"),'CSP restrictions');console.log('PASS',++n,'offline-only CSP');
assert(!/\b(?:fetch\s*\(|XMLHttpRequest|WebSocket|sendBeacon|localStorage|sessionStorage|indexedDB)\b/.test(code),'no storage/egress APIs');console.log('PASS',++n,'no storage/network calls');
assert(!/\.(?:innerHTML|outerHTML)\b/.test(code),'no HTML injection output');console.log('PASS',++n,'text-only DOM result');
check('oversize input rejected before parsing','50','x'.repeat(8193),['HOLD: Maximum 8192 input characters']);
console.log(`TOTAL ${n}/${n} PASS`);
