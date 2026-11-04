import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,writeFileSync,symlinkSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {readEvidence} from './evidence-files.mjs';
function fixture(fn){const dir=mkdtempSync(join(tmpdir(),'wit-synthetic-evidence-'));try{fn(dir);}finally{rmSync(dir,{recursive:true,force:true});}}
test('bounded file read returns exact synthetic bytes',()=>fixture(dir=>{const p=join(dir,'artifact');writeFileSync(p,'fictional');assert.equal(readEvidence(p,9).toString(),'fictional');}));
test('oversized evidence refused',()=>fixture(dir=>{const p=join(dir,'artifact');writeFileSync(p,'fictional');assert.throws(()=>readEvidence(p,8));}));
test('directory is not evidence',()=>fixture(dir=>assert.throws(()=>readEvidence(dir,10))));
test('final symlink is not followed',()=>fixture(dir=>{const p=join(dir,'artifact'),link=join(dir,'link');writeFileSync(p,'fictional');symlinkSync(p,link);assert.throws(()=>readEvidence(link,10));}));
test('unbounded caller limit refused',()=>assert.throws(()=>readEvidence('unused',Infinity)));
test('scanner review CLI retains human-only result with exact synthetic evidence',()=>fixture(dir=>{
 const artifact=Buffer.from('Fictional inert skill specimen.'),report=Buffer.from(JSON.stringify({execution_successful:true,metadata:{skillspector_version:'2.12.0',llm_requested:false},components:[{path:'SKILL.md'}],issues:[],suppressed:[],risk_assessment:{recommendation:'SAFE'},analysis_completeness:{status:'complete',is_complete:true,execution_successful:true,coverage_percent:100,ledger_exceptions:[],limitations:[],scope_exclusions:[]}}));
 const sha=b=>createHash('sha256').update(b).digest('hex');
 const receipt={scanner:'NVIDIA/SkillSpector',version:'2.12.0',execution:'completed',isolation:'external_sandbox_no_network',llm_used:false,exit_code:0,artifact_sha256:sha(artifact),report_sha256:sha(report)};
 const a=join(dir,'artifact'),r=join(dir,'report.json'),e=join(dir,'receipt.json');writeFileSync(a,artifact);writeFileSync(r,report);writeFileSync(e,JSON.stringify(receipt));
 const cli=fileURLToPath(new URL('./review-skill.mjs',import.meta.url));
 const run=()=>spawnSync(process.execPath,[cli,r,e,a],{encoding:'utf8',timeout:5000,env:{PATH:process.env.PATH}});
 const valid=run();assert.equal(valid.status,0);assert.equal(JSON.parse(valid.stdout).can_install,false);assert.equal(JSON.parse(valid.stdout).status,'READY_FOR_HUMAN_REVIEW');
 writeFileSync(a,'changed fictional specimen');const changed=run();assert.equal(changed.status,1);assert.equal(JSON.parse(changed.stdout).status,'HOLD');
}));
test('onboarding CLI checks supplied synthetic artifact',()=>{
 const local=name=>fileURLToPath(new URL(name,import.meta.url));
 const r=spawnSync(process.execPath,[local('./measure-onboarding.mjs'),local('./onboarding.example.json'),local('./first-result.example.txt')],{encoding:'utf8',timeout:5000,env:{PATH:process.env.PATH}});
 assert.equal(r.status,0);assert.equal(JSON.parse(r.stdout).status,'SYNTHETIC_ONLY');assert.equal(JSON.parse(r.stdout).first_useful_result_ms,500);
});
