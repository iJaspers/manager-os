/** Runs only the pinned local contract config. Never starts a model/API/red-team job. */
import {spawnSync} from 'node:child_process';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {join,resolve} from 'node:path';
const [cliArg,outArg,mode]=process.argv.slice(2);
try {
 if(!cliArg||!outArg||process.argv.length>5||(mode!==undefined&&mode!=='--negative-control'))throw new Error('USAGE');
 const cli=resolve(cliArg),out=resolve(outArg);
 mkdirSync(out,{mode:0o700});
 const env={PATH:process.env.PATH,TMPDIR:out,NO_COLOR:'1',PROMPTFOO_CONFIG_DIR:join(out,'state'),PROMPTFOO_DISABLE_TELEMETRY:'1',PROMPTFOO_DISABLE_UPDATE:'1',PROMPTFOO_DISABLE_REMOTE_GENERATION:'1'};
 const version=spawnSync(process.execPath,[cli,'--version'],{env,cwd:out,encoding:'utf8',timeout:10000,maxBuffer:65536});
 if(version.status!==0||version.stdout.trim()!=='0.125.1')throw new Error('VERSION');
 const config=JSON.parse(readFileSync(new URL('./promptfooconfig.json',import.meta.url)));
 config.providers=['file://'+fileURLToPath(new URL('./promptfoo-provider.mjs',import.meta.url))];
 if(mode==='--negative-control')config.tests[0].assert[0].value='INTENTIONAL_NEGATIVE_CONTROL';
 const cfg=join(out,'config.json'),raw=join(out,'raw-results.json');writeFileSync(cfg,JSON.stringify(config),{mode:0o600,flag:'wx'});
 const r=spawnSync(process.execPath,[cli,'eval','--config',cfg,'--no-cache','--output',raw],{env,cwd:out,encoding:'utf8',timeout:90000,maxBuffer:1048576});
 const data=JSON.parse(readFileSync(raw));const stats=data.results?.stats;
 if(!stats||r.error)throw new Error('RESULT');
 const positive=mode!=='--negative-control',expected=positive?{successes:20,failures:0,errors:0}:{successes:19,failures:1,errors:0};
 const passed=Object.entries(expected).every(([k,v])=>stats[k]===v)&&(positive?r.status===0:r.status!==0);
 const receipt={schema:'wit.promptfoo-run.v1',version:'0.125.1',evidence_kind:'SYNTHETIC_CONTRACT',native_host_tested:false,mode:positive?'positive':'intentional-negative-control',stats:{successes:stats.successes,failures:stats.failures,errors:stats.errors},expected,passed,exit_code:r.status};
 writeFileSync(join(out,'receipt.json'),JSON.stringify(receipt,null,2)+'\n',{mode:0o600,flag:'wx'});console.log(JSON.stringify(receipt,null,2));if(!passed)process.exitCode=1;
}catch{console.error('Promptfoo run unavailable or incomplete; inspect local evidence. No provider call was configured.');process.exitCode=1;}
