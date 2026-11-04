import test from 'node:test';
import assert from 'node:assert/strict';
import {runReadOnly} from './host-read.mjs';
import {requestHash} from './connector-doctor.mjs';
const request=()=>({host:'node',session:'synthetic',account:'fictional',connector:'fixture',tool:'read_fixture',action:'read',target:'approved.txt',payload:''});
function fixture(){
 let count=0,clock='2026-11-03T12:00:00Z';
 const h={now:()=>clock,observe:async()=>({connections:[{host:'node',id:'fixture',session:'synthetic',account:'fictional',source:'host_tool_response',observed_at:clock,installed:true,authenticated:true,observed:true,tools:['read_fixture'],capabilities:['read'],tool_capabilities:{read_fixture:['read']}}]}),authorize:async()=>true,invoke:async x=>{count++;return {source:'host_tool_response',invocation_id:'fictional',request_sha256:requestHash(x),target:x.target,outcome:'succeeded',observed_at:clock,result_present:true};}};
 return {h,count:()=>count,setClock:x=>clock=x};
}
test('authorization cannot mutate both request copies to approve another target',async()=>{
 const r=request(),f=fixture();f.h.authorize=async x=>{r.target='changed.txt';try{x.target='changed.txt';}catch{}return true;};
 assert.equal((await runReadOnly(r,f.h)).status,'APPROVAL_MISMATCH');assert.equal(f.count(),0);
});
for(const [key,value] of [['action','write'],['target','other.txt'],['payload','other input'],['account','other'],['session','other'],['host','other'],['tool','other'],['connector','other']])test('changed '+key+' during authorization never invokes',async()=>{
 const r=request(),f=fixture();f.h.authorize=async()=>{r[key]=value;return true;};const out=await runReadOnly(r,f.h);assert.equal(out.status,'APPROVAL_MISMATCH');assert.equal(f.count(),0);
});
test('scope and observed capability arrays are immutable at host boundary',async()=>{
 const f=fixture();f.h.authorize=async x=>{assert.ok(Object.isFrozen(x));assert.ok(Object.isFrozen(x.connections[0].tools));assert.throws(()=>x.connections[0].tools.push('write'));return true;};assert.equal((await runReadOnly(request(),f.h)).status,'VERIFIED');
});
test('request changed during first observation is stopped before permission',async()=>{
 const r=request(),f=fixture(),observe=f.h.observe;let authorized=0;f.h.observe=async x=>{assert.ok(Object.isFrozen(x));r.target='other.txt';return observe();};f.h.authorize=async()=>{authorized++;return true;};assert.equal((await runReadOnly(r,f.h)).status,'APPROVAL_MISMATCH');assert.equal(authorized,0);assert.equal(f.count(),0);
});
test('expired local permission window blocks with fresh capability observations',async()=>{const f=fixture();f.h.authorize=async()=>{f.setClock('2026-11-03T12:05:01Z');return true;};assert.equal((await runReadOnly(request(),f.h)).status,'APPROVAL_EXPIRED');assert.equal(f.count(),0);});
test('clock rollback cannot extend permission',async()=>{const f=fixture();f.h.authorize=async()=>{f.setClock('2026-11-03T11:59:59Z');return true;};assert.equal((await runReadOnly(request(),f.h)).status,'APPROVAL_EXPIRED');assert.equal(f.count(),0);});
test('replacing invoke callback during authorization does not redirect execution',async()=>{const f=fixture();let redirected=0;f.h.authorize=async()=>{f.h.invoke=async()=>{redirected++;throw Error('redirected');};return true;};assert.equal((await runReadOnly(request(),f.h)).status,'VERIFIED');assert.equal(f.count(),1);assert.equal(redirected,0);});
test('mutation during execution cannot turn into a verified success',async()=>{const r=request(),f=fixture(),invoke=f.h.invoke;f.h.invoke=async x=>{r.target='changed.txt';return invoke(x);};const out=await runReadOnly(r,f.h);assert.equal(out.status,'UNVERIFIED');assert.equal(out.attempted,true);assert.equal(f.count(),1);});
test('extra action fields are rejected before host discovery',async()=>{const f=fixture();let observed=0;f.h.observe=async()=>{observed++;return {};};assert.equal((await runReadOnly({...request(),path:'unapproved.txt'},f.h)).status,'INVALID_INPUT');assert.equal(observed,0);});
test('accessor intent is rejected without executing getter',async()=>{const r=request(),f=fixture();let getters=0;Object.defineProperty(r,'target',{get(){getters++;return 'other';},enumerable:true});assert.equal((await runReadOnly(r,f.h)).status,'INVALID_INPUT');assert.equal(getters,0);});
test('oversized input is rejected before host observation',async()=>{const f=fixture();let observed=0;f.h.observe=async()=>{observed++;return {};};assert.equal((await runReadOnly({...request(),payload:'x'.repeat(32769)},f.h)).status,'INVALID_INPUT');assert.equal(observed,0);});
