/** Disposable, synthetic, local end-to-end demo. This is not a provider adapter. */
import {mkdirSync,writeFileSync,readFileSync} from 'node:fs';
import {join} from 'node:path';
import {sha256,requestHash} from './connector-doctor.mjs';
import {handoff,reviewResume,planPreferences,revision} from './portability.mjs';
import {initializeProfile,loadProfile,applyProfile,rollbackProfile} from './profile-store.mjs';
import {runReadOnly} from './host-read.mjs';
try {
  if(process.argv.length!==3)throw new Error('USAGE');
  const dir=process.argv[2];mkdirSync(dir,{mode:0o700});
  const initial={language:'en',detail:'normal',mode:'everyday'},desired={language:'fr',detail:'brief',mode:'power'};
  initializeProfile(dir,initial);
  const plan=planPreferences(initial,desired),applied=applyProfile(dir,plan,true);
  const input='Synthetic packing checklist: notebook, pencil.\n';
  writeFileSync(join(dir,'fixture.txt'),input,{mode:0o600,flag:'wx'});
  const saved=handoff({...JSON.parse(readFileSync(new URL('./handoff.example.json',import.meta.url))),checkpoint:{tool_id:'wit.connector-doctor',version:'0.2.1-public-draft.1',step_id:'inspect-result',artifact_sha256:sha256(input)}});
  writeFileSync(join(dir,'handoff.json'),JSON.stringify(saved,null,2)+'\n',{mode:0o600,flag:'wx'});
  const current=JSON.parse(readFileSync(new URL('./example.json',import.meta.url)));
  const review=reviewResume(saved,current);
  let observed;
  const host={now:()=>current.as_of,observe:async()=>({connections:current.connections}),
    authorize:async r=>r.action==='read'&&r.tool==='read_fixture'&&r.target==='fixture.txt',
    invoke:async r=>{
      if(r.action!=='read'||r.tool!=='read_fixture'||r.target!=='fixture.txt')throw new Error('DENIED');
      observed=readFileSync(join(dir,'fixture.txt'),'utf8');
      return {source:'host_tool_response',invocation_id:'synthetic-local-read',request_sha256:requestHash(r),target:r.target,observed_at:current.as_of,outcome:'succeeded',result_present:true};
    }};
  const read=await runReadOnly(current,host);
  if(!read.verified||sha256(observed)!==saved.checkpoint.artifact_sha256)throw new Error('READBACK');
  const rollback=rollbackProfile(dir,revision(desired),true);
  const receipt={schema:'wit.local-demo.v1',synthetic:true,external_provider_tested:false,
    profile_apply:applied.status,resume_check:review.status,read:read.status,
    expected_output_sha256:sha256(input),observed_output_sha256:sha256(observed),
    rollback:rollback.status,profile_restored:revision(loadProfile(dir))===revision(initial)};
  writeFileSync(join(dir,'receipt.json'),JSON.stringify(receipt,null,2)+'\n',{mode:0o600,flag:'wx'});
  console.log(JSON.stringify(receipt,null,2));
} catch {console.error('Demo stopped. Inspect its disposable directory before retry.');process.exitCode=1;}
