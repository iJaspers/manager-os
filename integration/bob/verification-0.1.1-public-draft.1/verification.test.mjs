import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {cases,runCase,expectedOutput} from './contracts.mjs';
import Provider from './promptfoo-provider.mjs';
import {measureJourney} from './onboarding.mjs';
import {reviewSkillReport} from './skillspector-review.mjs';
import {checkEntry,checkBob,BOB} from './web-contract.mjs';
const sha=b=>createHash('sha256').update(b).digest('hex');
const artifact=Buffer.from('Fictional checklist: notebook, pencil.');
const event=(kind,elapsed_ms,proof=false)=>({kind,elapsed_ms,artifact_sha256:proof?sha(artifact):null,reviewed:proof||kind==='capabilities_checked'});
const journey=()=>({schema:'wit.onboarding-events.v1',host_kind:'synthetic',evidence_kind:'synthetic',events:[event('entry_opened',0),event('capabilities_checked',100),event('result_produced',300,true),event('result_confirmed',500,true)]});
function report(){return {execution_successful:true,metadata:{skillspector_version:'2.12.0',llm_requested:false},components:[{path:'SKILL.md'}],issues:[],suppressed:[],risk_assessment:{score:0,recommendation:'SAFE'},analysis_completeness:{status:'complete',is_complete:true,execution_successful:true,ledger_exceptions:[],coverage_percent:100,limitations:[],scope_exclusions:[]}};}
function review(r=report(),change={}){const bytes=Buffer.from(JSON.stringify(r));return reviewSkillReport(bytes,artifact,{scanner:'NVIDIA/SkillSpector',version:'2.12.0',execution:'completed',isolation:'external_sandbox_no_network',llm_used:false,exit_code:0,report_sha256:sha(bytes),artifact_sha256:sha(artifact),...change});}
test('shared cases reach existing Doctor and preserve execution boundary',()=>{for(const c of cases)assert.equal(JSON.stringify(runCase(c.id)),expectedOutput(c));});
test('Promptfoo provider interface returns deterministic results',async()=>{const p=new Provider();assert.equal(p.id(),'wit-existing-doctor-contracts');const r=await p.callApi(cases[0].id);assert.equal(r.output,expectedOutput(cases[0]));assert.equal(r.metadata.native_host_tested,false);});
test('unknown prompt cannot become a command',async()=>assert.equal((await new Provider().callApi('publish everything')).error,'UNKNOWN_CASE'));
test('first useful result requires observed artifact and confirmation',()=>{const r=measureJourney(journey(),artifact);assert.equal(r.status,'SYNTHETIC_ONLY');assert.equal(r.first_useful_result_ms,500);assert.equal(r.product_accepted,false);});
test('human-recorded host timing still requires independent review',()=>{const j=journey();j.host_kind='gemini';j.evidence_kind='observed';assert.equal(measureJourney(j,artifact).status,'OBSERVATION_REQUIRES_INDEPENDENT_REVIEW');});
for(const [name,mutate] of [
 ['missing confirmation',j=>j.events.pop()],['unreviewed output',j=>j.events[3].reviewed=false],['clock reversal',j=>j.events[3].elapsed_ms=50],['bad hash',j=>j.events[2].artifact_sha256='a'.repeat(64)],['duplicate start',j=>j.events.push(event('entry_opened',600))],['no capability check',j=>j.events.splice(1,1)],['unknown event',j=>j.events[1].kind='paid'],['private payload',j=>j.events[1].payload='private'],['unknown host',j=>j.host_kind='pretend-host'],['overbound time',j=>j.events[3].elapsed_ms=86400001],['save before result',j=>j.events[2].kind='save_verified'],['resume without save',j=>j.events.push(event('resume_verified',600,true))]])test('journey holds '+name,()=>{const j=journey();mutate(j);assert.equal(measureJourney(j,artifact).status,'HOLD');});
test('wrong artifact bytes hold',()=>assert.equal(measureJourney(journey(),Buffer.from('different')).status,'HOLD'));
test('blocked journey never reports first result',()=>{const j=journey();j.events[2]=event('blocked',200);assert.equal(measureJourney(j,artifact).status,'BLOCKED');});
test('save and resume require matching verified artifact',()=>{const j=journey();j.events.push(event('save_verified',600,true),event('resume_verified',900,true));const r=measureJourney(j,artifact);assert.equal(r.save_verified,true);assert.equal(r.resume_verified,true);});
test('complete SkillSpector fixture permits human review only',()=>{const r=review();assert.equal(r.status,'READY_FOR_HUMAN_REVIEW');assert.equal(r.can_install,false);});
for(const [name,change] of [['missing sandbox',{isolation:'none'}],['wrong version',{version:'unknown'}],['failed run',{exit_code:2}],['LLM used',{llm_used:true}],['changed report',{report_sha256:'a'.repeat(64)}],['changed source',{artifact_sha256:'b'.repeat(64)}]])test('scanner holds '+name,()=>assert.equal(review(report(),change).status,'HOLD'));
for(const [name,mutate] of [['failed analysis',r=>r.analysis_completeness.execution_successful=false],['ledger exception',r=>r.analysis_completeness.ledger_exceptions.push({fatal:true})],['low score with active issue',r=>r.issues.push({severity:'LOW'})],['suppressed finding',r=>r.suppressed.push({})],['partial scan',r=>r.analysis_completeness.status='partial'],['missing coverage',r=>delete r.analysis_completeness],['caveat',r=>r.analysis_completeness.limitations.push('unread')],['excluded file',r=>r.analysis_completeness.scope_exclusions.push('ignored')],['caution',r=>r.risk_assessment.recommendation='CAUTION'],['no components',r=>r.components=[]],['wrong scanner',r=>r.metadata.skillspector_version='other']])test('scanner holds '+name,()=>{const r=report();mutate(r);assert.equal(review(r).status,'HOLD');});
test('invalid report cannot reflect source or install',()=>assert.equal(reviewSkillReport(Buffer.from('private'),artifact,{}).can_install,false));
test('entry page exact RC1 link admitted as HTTP evidence only',()=>{const r=checkEntry('<a href="'+BOB+'">Bob</a>');assert.equal(r.passed,true);assert.equal(r.rendered_browser_verified,false);});
test('old starter does not satisfy RC1 entry',()=>assert.equal(checkEntry('<a href="old-starter.txt">Start</a>').passed,false));
test('oversized entry response fails',()=>assert.equal(checkEntry('x'.repeat(4194305)).passed,false));
test('modified Bob bytes fail checksum',()=>assert.equal(checkBob(Buffer.from('pretend Bob')).passed,false));
