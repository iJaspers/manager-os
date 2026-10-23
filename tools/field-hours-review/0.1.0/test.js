// SPDX-License-Identifier: MIT
// Copyright (c) 2026 iJaspers. See LICENSE.
'use strict';
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const path = require('path');
const html = fs.readFileSync(path.join(__dirname,'tool.html'),'utf8');
let passed=0;
function check(name, fn){try{fn();passed++;console.log('PASS '+name)}catch(e){console.error('FAIL '+name,e);process.exitCode=1}}
function evaluate(start,end,lunch,nextDay){
  const listeners={};
  const el={start:{value:start},end:{value:end},lunch:{value:lunch},nextDay:{checked:nextDay},calc:{addEventListener:(type,cb)=>{listeners[type]=cb}},result:{textContent:''}};
  const doc={getElementById:id=>{assert(el[id],'Unknown ID '+id);return el[id]}};
  const match=html.match(/<script>([\s\S]*?)<\/script>/);
  assert(match,'Standalone script required');
  vm.runInNewContext(match[1],{document:doc},{timeout:1000});
  listeners.click();
  return el.result.textContent;
}
check('same-day 8h net positive',()=>{assert.match(evaluate('08:30','17:00','30',false),/Net: 480 minutes \(8\.00 decimal hours\)/)});
check('explicit overnight 7.5h net positive',()=>{const s=evaluate('22:00','06:00','30',true);assert.match(s,/Net: 450 minutes \(7\.50 decimal hours\)/);assert.match(s,/Finish: next day/)});
check('midnight finish from 20:00',()=>{assert.match(evaluate('20:00','00:00','0',true),/Net: 240 minutes \(4\.00 decimal hours\)/)});
check('no implicit overnight',()=>{assert.match(evaluate('22:00','06:00','30',false),/^HOLD:/)});
check('wrong next-day on normal day blocked',()=>{assert.match(evaluate('08:30','17:00','30',true),/^HOLD:/)});
check('equal times same day held',()=>{assert.match(evaluate('08:30','08:30','30',false),/^HOLD:/)});
check('equal times next day held',()=>{assert.match(evaluate('08:30','08:30','30',true),/^HOLD:/)});
check('18h+ shift held',()=>{assert.match(evaluate('20:00','18:00','30',true),/HOLD: Shift exceeds 18 hours/)});
check('blank lunch held, not assumed paid',()=>{assert.match(evaluate('08:30','17:00','',false),/^HOLD:/)});
check('noninteger lunch held',()=>{assert.match(evaluate('08:30','17:00','30.5',false),/^HOLD:/)});
check('lunch exceeds shift held',()=>{assert.match(evaluate('08:30','09:00','30',false),/^HOLD:/)});
check('malformed time held',()=>{assert.match(evaluate('25:00','17:00','30',false),/^HOLD:/)});
check('offline CSP blocks network and forms',()=>{assert.match(html,/connect-src 'none'/);assert.match(html,/form-action 'none'/);assert.doesNotMatch(html,/(?:fetch\(|XMLHttpRequest|sendBeacon\(|localStorage|sessionStorage)/)});
console.log(`${passed}/13 standalone checks passed`);
if(passed!==13)process.exitCode=1;