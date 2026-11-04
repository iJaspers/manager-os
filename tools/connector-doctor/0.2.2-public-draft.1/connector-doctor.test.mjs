import test from 'node:test';
import assert from 'node:assert/strict';
import {evaluate,requestHash,sha256,verifyResult} from './connector-doctor.mjs';
export function fixture() { return {host:'chatgpt',session:'synthetic-session',account:'fictional-account',connector:'fixture',tool:'read_fixture',action:'read',target:'fixture.txt',payload:'',as_of:'2026-11-02T17:00:00Z',connections:[{host:'chatgpt',id:'fixture',session:'synthetic-session',account:'fictional-account',source:'host_tool_response',observed_at:'2026-11-02T17:00:00Z',available:true,installed:true,authenticated:true,observed:true,capabilities:['read','draft','write','send'],tools:['read_fixture','write_fixture'],tool_capabilities:{read_fixture:['read','draft'],write_fixture:['write','send']}}]}; }
const change = (patch, connection) => {const x={...fixture(),...patch};if(connection)x.connections=[{...x.connections[0],...connection}];return x;};
function approved(patch={}) {const x=change({action:'write',tool:'write_fixture',payload:'FICTIONAL CHECKLIST',...patch});x.approval={id:'synthetic-approval-1',granted:true,request_sha256:requestHash(x),issued_at:'2026-11-02T16:59:00Z',expires_at:'2026-11-02T17:05:00Z'};x.used_approval_ids=[];return x;}
function receipt(x) {return {source:'host_tool_response',invocation_id:'synthetic-invocation-1',request_sha256:requestHash(x),target:x.target,outcome:'succeeded',observed_at:'2026-11-02T17:00:01Z',result_present:true,readback:{source:'host_tool_response',target:x.target,account:x.account,payload_sha256:sha256(x.payload),observed_at:'2026-11-02T17:00:02Z'}};}
const cases=[
 ['current read',()=>fixture(),'READY_TO_REQUEST','INSTALLED'],
 ['chat draft',()=>change({action:'draft',draft_location:'chat'}),'READY_TO_REQUEST','INSTALLED'],
 ['ambiguous draft',()=>change({action:'draft'}),'NEEDS_DETAILS','INSTALLED'],
 ['provider draft writes',()=>change({action:'draft',draft_location:'provider'}),'NEEDS_APPROVAL','INSTALLED'],
 ['missing connector',()=>change({connections:[]}),'UNVERIFIED','UNVERIFIED'],
 ['wrong AI',()=>change({host:'gemini'}),'UNVERIFIED','UNVERIFIED'],
 ['user assertion',()=>change({}, {source:'user_report'}),'UNVERIFIED','UNVERIFIED'],
 ['marketing only',()=>change({}, {source:'vendor_marketing'}),'UNVERIFIED','UNVERIFIED'],
 ['available to install',()=>change({}, {installed:false}),'AVAILABLE','AVAILABLE'],
 ['installed unauthenticated',()=>change({}, {authenticated:false}),'NEEDS_CONNECTION','INSTALLED'],
 ['missing callable tool',()=>change({}, {tools:[]}),'UNVERIFIED','INSTALLED'],
 ['unsupported host',()=>change({}, {supported:false}),'UNSUPPORTED','UNSUPPORTED'],
 ['unsupported action',()=>change({action:'publish'}),'UNSUPPORTED','INSTALLED'],
 ['policy denial',()=>change({blocked_by_policy:true}),'DENIED','DENIED'],
 ['revocation',()=>change({}, {revoked:true}),'DENIED','DENIED'],
 ['denied connector',()=>change({}, {denied:true}),'DENIED','DENIED'],
 ['denial outranks unavailable',()=>change({}, {denied:true,installed:false,source:'vendor_marketing'}),'DENIED','DENIED'],
 ['duplicate identity',()=>change({connections:[...fixture().connections,...fixture().connections]}),'AMBIGUOUS','UNVERIFIED'],
 ['stale evidence',()=>change({}, {observed_at:'2026-11-02T16:54:59Z'}),'UNVERIFIED','UNVERIFIED'],
 ['future evidence',()=>change({}, {observed_at:'2026-11-02T17:00:01Z'}),'UNVERIFIED','UNVERIFIED'],
 ['copied session',()=>change({session:'new-session'}),'UNVERIFIED','UNVERIFIED'],
 ['changed account',()=>change({account:'another-account'}),'UNVERIFIED','UNVERIFIED'],
 ['missing clock',()=>change({as_of:undefined}),'UNVERIFIED','UNVERIFIED'],
 ['timezone required',()=>change({as_of:'2026-11-02T17:00:00'}),'UNVERIFIED','UNVERIFIED'],
 ['truthy authentication',()=>change({}, {authenticated:'true'}),'INVALID_INPUT','UNVERIFIED'],
 ['secret key rejected',()=>change({api_key:'FICTIONAL-NOT-A-KEY'}),'INVALID_INPUT','UNVERIFIED'],
 ['nested credentials rejected',()=>change({extra:{credentials:'FICTIONAL'}}),'INVALID_INPUT','UNVERIFIED'],
 ['unknown action',()=>change({action:'unlock_vault'}),'INVALID_INPUT','UNVERIFIED'],
 ['oversized payload',()=>change({payload:'x'.repeat(32769)}),'INVALID_INPUT','UNVERIFIED'],
 ['missing target',()=>change({target:''}),'INVALID_INPUT','UNVERIFIED'],
 ['write no approval',()=>change({action:'write',tool:'write_fixture',payload:'fictional'}),'NEEDS_APPROVAL','INSTALLED'],
 ['exact scoped approval',()=>approved(),'READY_TO_REQUEST','INSTALLED'],
 ['changed content',()=>({...approved(),payload:'changed'}),'APPROVAL_MISMATCH','INSTALLED'],
 ['changed target',()=>({...approved(),target:'different.txt'}),'APPROVAL_MISMATCH','INSTALLED'],
 ['changed tool with unsupported action',()=>({...approved(),tool:'read_fixture'}),'UNSUPPORTED','INSTALLED'],
 ['changed draft location',()=>({...approved({action:'draft',tool:'read_fixture',draft_location:'provider'}),draft_location:undefined}),'NEEDS_DETAILS','INSTALLED'],
 ['expired approval',()=>{const x=approved();x.approval.expires_at=x.as_of;return x;},'APPROVAL_EXPIRED','INSTALLED'],
 ['future approval',()=>{const x=approved();x.approval.issued_at='2026-11-02T17:01:00Z';return x;},'APPROVAL_EXPIRED','INSTALLED'],
 ['used approval',()=>({...approved(),used_approval_ids:['synthetic-approval-1']}),'APPROVAL_USED','INSTALLED'],
 ['truthy approval',()=>{const x=approved();x.approval.granted='yes';return x;},'NEEDS_APPROVAL','INSTALLED'],
];
for(const [name,make,status,state] of cases) test(name,()=>{const r=evaluate(make());assert.equal(r.status,status);assert.equal(r.connection_state,state);assert.equal(r.executed,false);assert.equal(r.can_execute,false);});
test('denial never recommends setup or bypass',()=>{const r=evaluate(change({blocked_by_policy:true}));assert.equal(r.connection_state,'DENIED');assert.match(r.next_action,/Stop/);});
test('full binding changes with host, session, account, timing in payload',()=>{const x=approved();for(const k of ['host','session','account','connector','tool','action','target','payload'])assert.notEqual(requestHash(x),requestHash({...x,[k]:'changed'}));});
test('invalid inputs never throw or echo secrets',()=>{for(const x of [null,[],true,3,'secret',{}, {api_key:'do-not-echo'}]) {const r=evaluate(x);assert.equal(r.status,'INVALID_INPUT');assert.ok(!JSON.stringify(r).includes('do-not-echo'));}});
for(const [name,patch,expected] of [
 ['read success',{},'VERIFIED'],['no result',{result_present:false},'UNVERIFIED'],
 ['API failure',{outcome:'failed'},'FAILED'],['timeout',{outcome:'unknown'},'UNVERIFIED'],
 ['host denial',{outcome:'denied'},'DENIED'],['wrong target',{target:'other'},'UNVERIFIED'],
 ['wrong request',{request_sha256:'other'},'UNVERIFIED'],['fake user receipt',{source:'user_report'},'UNVERIFIED'],
 ['missing invocation',{invocation_id:''},'UNVERIFIED'],['old response',{observed_at:'2026-11-02T16:00:00Z'},'UNVERIFIED']
]) test('result: '+name,()=>{const x=fixture();const r=verifyResult(x,{...receipt(x),...patch});assert.equal(r.status,expected);});
test('write succeeds only with same-target readback',()=>{const x=approved();assert.equal(verifyResult(x,receipt(x)).status,'VERIFIED');});
for(const [name,patch] of [['wrong account',{account:'another'}],['wrong bytes',{payload_sha256:sha256('wrong')}],['wrong target',{target:'other'}],['old readback',{observed_at:'2026-11-02T16:00:00Z'}],['untrusted readback',{source:'user_report'}]]) test('readback: '+name,()=>{const x=approved(),r=receipt(x);Object.assign(r.readback,patch);assert.equal(verifyResult(x,r).status,'UNVERIFIED');});
test('write without readback is not success',()=>{const x=approved(),r=receipt(x);delete r.readback;assert.equal(verifyResult(x,r).status,'UNVERIFIED');});
test('ineligible request cannot gain success from a receipt',()=>{const x=change({blocked_by_policy:true});assert.equal(verifyResult(x,receipt(x)).status,'UNVERIFIED');});
test('forged source labels remain explicitly unauthenticated',()=>{const x=fixture();assert.match(verifyResult(x,receipt(x)).evidence_level,/CONSISTENCY_ONLY/);assert.match(evaluate(x).evidence_level,/SUPPLIED/);});

test('connector-level write access cannot make a read-only tool writable',()=>{const x=approved({tool:'read_fixture'});assert.equal(evaluate(x).status,'UNSUPPORTED');});
