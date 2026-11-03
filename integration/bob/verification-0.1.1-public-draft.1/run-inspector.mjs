import {checkFixture} from './inspector-adapter.mjs';
import {writeFileSync,mkdirSync} from 'node:fs';
import {join,resolve} from 'node:path';
const [cliArg,outArg]=process.argv.slice(2);
try {
 if(!cliArg||!outArg||process.argv.length!==4)throw new Error('USAGE');
 const cli=resolve(cliArg),out=resolve(outArg);
 mkdirSync(out,{mode:0o700});
 const results=[];
 for(const [id,item,consent,expected] of [['read','checklist',true,'VERIFIED'],['no-consent','checklist',false,'DENIED'],['remote-denial','denied',true,'DENIED'],['failed','failed',true,'FAILED'],['unsupported-target','outside',true,'DENIED']]){
  const r=await checkFixture(cli,join(out,id),item,consent);
  const pass=r.result.status===expected&&(!(id==='no-consent'||id==='unsupported-target')||r.trace.every(t=>t.method!=='tools/call'));
  results.push({id,expected,pass,...r});
 }
 const receipt={schema:'wit.inspector-run.v1',version:'2.13.0',passed:results.filter(r=>r.pass).length,failed:results.filter(r=>!r.pass).length,results};
 writeFileSync(join(out,'receipt.json'),JSON.stringify(receipt,null,2)+'\n',{mode:0o600,flag:'wx'});
 console.log(JSON.stringify(receipt,null,2));if(receipt.failed)process.exitCode=1;
}catch{console.error('Inspector run unavailable or incomplete; inspect local evidence before retry.');process.exitCode=1;}
