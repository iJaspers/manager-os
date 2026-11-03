/** Operator-selected Inspector CLI; only the bundled synthetic stdio fixture is callable. */
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {join} from 'node:path';
import {mkdirSync} from 'node:fs';
import {runReadOnly} from '../../../tools/connector-doctor/0.2.1-public-draft.1/host-read.mjs';
import {request,requestHash} from './contracts.mjs';
const fixture=fileURLToPath(new URL('./mcp-fixture.mjs',import.meta.url));
export function makeInspectorHost(cli,stateDir,{consent=false,trace=[]}={}){
 mkdirSync(stateDir,{recursive:true,mode:0o700});
 const env={PATH:process.env.PATH,TMPDIR:stateDir,NO_COLOR:'1',MCP_AUTO_OPEN_ENABLED:'false',MCP_INSPECTOR_SECRET_STORE:'memory',MCP_STORAGE_DIR:join(stateDir,'inspector')};
 const version=spawnSync(process.execPath,[cli,'--version'],{env,cwd:stateDir,encoding:'utf8',timeout:10000,maxBuffer:65536});
 if(version.status!==0||version.stdout.trim()!=='2.13.0')throw new Error('INSPECTOR_VERSION_UNVERIFIED');
 const invokeCLI=(method,item)=>{
  const args=[cli,process.execPath,fixture,'--method',method,'--format','json','--connect-timeout','5000'];
  if(item!==undefined)args.push('--tool-name','wit_fixture_read','--tool-arg','item='+item);
  const r=spawnSync(process.execPath,args,{env,cwd:stateDir,encoding:'utf8',timeout:15000,maxBuffer:65536});
  trace.push({method,exit_code:r.status});
  if(r.error||!r.stdout)throw new Error('INSPECTOR_FAILED');
  const data=JSON.parse(r.stdout);
  if(!data.result||data.error)throw new Error('INSPECTOR_FAILED');
  if(r.status!==0&&data.result.isError!==true)throw new Error('INSPECTOR_FAILED');
  return data.result;
 };
 const now=()=>new Date().toISOString();
 const base=request();
 return {now,
  observe:async()=>{
   const list=invokeCLI('tools/list');
   const t=Array.isArray(list.tools)&&list.tools.find(t=>t.name==='wit_fixture_read');
   // Read-only authority comes from this fixed fixture allowlist, not untrusted hints.
   if(!t||t.inputSchema?.properties?.item?.type!=='string')throw new Error('TOOL_SCHEMA_UNVERIFIED');
   return {connections:[{...base.connections[0],observed_at:now(),tools:[t.name]}]};
  },
  authorize:async r=>consent===true&&r.action==='read'&&r.tool==='wit_fixture_read'&&r.connector==='fixture'&&r.host===base.host&&r.session===base.session&&r.account===base.account&&['checklist','denied','failed'].includes(r.target),
  invoke:async r=>{
   if(r.action!=='read'||r.tool!=='wit_fixture_read'||!['checklist','denied','failed'].includes(r.target))throw new Error('NOT_ALLOWLISTED');
   const actual=invokeCLI('tools/call',r.target);let outcome='succeeded';
   if(actual.isError){try{outcome=JSON.parse(actual.content?.[0]?.text).outcome;}catch{outcome='failed';}}
   const present=actual.structuredContent?.fixture==='checklist'&&JSON.stringify(actual.structuredContent.items)===JSON.stringify(['notebook','pencil']);
   return {source:'host_tool_response',invocation_id:'synthetic-inspector-read',request_sha256:requestHash(r),target:r.target,outcome,observed_at:now(),result_present:present};
  }};
}
export async function checkFixture(cli,stateDir,item='checklist',consent=false){
 const trace=[],host=makeInspectorHost(cli,stateDir,{consent,trace}),r=request();
 r.target=item;
 const result=await runReadOnly(r,host);
 return {schema:'wit.inspector-proof.v1',synthetic:true,external_provider_tested:false,result,trace};
}
