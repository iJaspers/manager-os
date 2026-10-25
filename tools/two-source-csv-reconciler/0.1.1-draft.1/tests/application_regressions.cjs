'use strict';
// Reviewer-authored synthetic application integration checks with minimal DOM.
// This checks application functions and state, not browser event dispatch or layout.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const root=path.resolve(process.argv[2]),version=process.argv[3],report=path.resolve(process.argv[4]);
if(!report.includes(path.sep+'reviewer'+path.sep))throw Error('Reports must stay in reviewer/');
const started=new Date().toISOString(),results=[],inputs=[];
function check(tool,name,fn){try{fn();results.push({tool,name,pass:true});}catch(e){results.push({tool,name,pass:false,detail:String(e.message).slice(0,800)});}}
function boot(tool,filename){const p=path.join(root,'tools',tool,version),html=fs.readFileSync(path.join(p,filename),'utf8'),common=fs.readFileSync(path.join(p,'common.js'),'utf8');
 for(const [name,bytes]of [[filename,html],['common.js',common]])inputs.push({path:path.relative(root,path.join(p,name)),sha256:crypto.createHash('sha256').update(bytes).digest('hex')});
 const nodes=new Map(),captures=[];
 function elem(){return {value:'',textContent:'',disabled:false,children:[],addEventListener(){},replaceChildren(){this.children=[]},append(...x){this.children.push(...x)},appendChild(x){this.children.push(x)}}}
 const document={getElementById(id){if(!nodes.has(id))nodes.set(id,elem());return nodes.get(id)},createElement:elem};
 const dec=x=>x.replaceAll('&gt;','>').replaceAll('&lt;','<').replaceAll('&amp;','&').replaceAll('&quot;','"');
 for(const x of html.matchAll(/<input\b[^>]*>/g)){const id=x[0].match(/\bid="([^"]+)"/),val=x[0].match(/\bvalue="([^"]*)"/);if(id)document.getElementById(id[1]).value=val?dec(val[1]):'';}
 for(const x of html.matchAll(/<textarea\b[^>]*id="([^"]+)"[^>]*>([\s\S]*?)<\/textarea>/g))document.getElementById(x[1]).value=dec(x[2]);
 for(const x of html.matchAll(/<select\b[^>]*id="([^"]+)"[^>]*>([\s\S]*?)<\/select>/g)){const choices=[...x[2].matchAll(/<option([^>]*)>([^<]*)<\/option>/g)],c=choices.find(v=>/selected/.test(v[1]))||choices[0];document.getElementById(x[1]).value=c[1].match(/value="([^"]+)"/)?.[1]||c[2];}
 const ctx=vm.createContext({document,TextEncoder},{codeGeneration:{strings:false,wasm:false}});
 const code=common+'\n'+[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(v=>v[1]).join('\n');
 vm.runInContext(code,ctx,{timeout:1000});ctx.capture=(...args)=>captures.push(args);vm.runInContext('downloadText=(...args)=>capture(...args)',ctx,{timeout:100});
 return {run:code=>vm.runInContext(code,ctx,{timeout:1000}),nodes,captures,html};}
const specs=[
 {tool:'two-source-csv-reconciler',file:'09_Two_Source_CSV_Reconciler.html',raw:'sourceText',reset:'displayExample(false)',calc:'evaluate()',parse:'csvTable(TEXT,"Synthetic")',exports:['exportIssues','exportReport','exportAI'],bad:'item_id,label,qty\nR-1,bad"label,1',valid:'item_id,label,qty\nR-1,"valid, label\nwith ""quotes""",1'},
 {tool:'regression-plan-forge',file:'10_Regression_Plan_Forge.html',raw:'reqCSV',reset:'sample()',calc:'prepare()',parse:'parseRequirements(TEXT)',exports:['exportCases','exportBrief','exportAI'],bad:'req_id,behavior,valid_input,expected_valid,invalid_input,expected_invalid,boundary_rule,risk,source_ref,privacy,rollback\nREQ-01,bad"behavior,toy-value,Valid input accepted,invalid-case,Invalid input rejected,NONE,LOW,SPEC-01,NO,NO',valid:'req_id,behavior,valid_input,expected_valid,invalid_input,expected_invalid,boundary_rule,risk,source_ref,privacy,rollback\nREQ-01,"valid, behavior\nwith ""quotes""",toy-value,Valid input accepted,invalid-case,Invalid input rejected,NONE,LOW,SPEC-01,NO,NO'},
 {tool:'dependency-critical-path-mapper',file:'11_Project_Dependency_Map.html',raw:'tasksCSV',reset:'demo()',calc:'analyze()',parse:'parseTasks(TEXT)',exports:['exportRows','exportBrief','exportAI'],bad:'task_id,title,duration_days,depends_on,status,owner_ref,source_ref,rights\nTASK-01,bad"title,1,NONE,PLANNED,TEAM-01,SPEC-01,CLEARED',valid:'task_id,title,duration_days,depends_on,status,owner_ref,source_ref,rights\nTASK-01,"valid, title\nwith ""quotes""",1,NONE,PLANNED,TEAM-01,SPEC-01,CLEARED'}
];
for(const s of specs){let a;check(s.tool,'boot with original application demo',()=>{a=boot(s.tool,s.file);assert.ok(a.run('last'));});if(!a)continue;
 const parse=text=>s.parse.replace('TEXT',JSON.stringify(text));
 check(s.tool,'UTF-8 byte bound is not character-count bound',()=>assert.throws(()=>a.run(s.parse.replace('TEXT',"'é'.repeat(MAX_BYTES/2+1)")),/KiB/));
 check(s.tool,'ASCII byte bound',()=>assert.throws(()=>a.run(s.parse.replace('TEXT',"'x'.repeat(MAX_BYTES+1)")),/KiB/));
 check(s.tool,'malformed bare quote rejected at application admission',()=>assert.throws(()=>a.run(parse(s.bad)),/quote|quoted/i));
 check(s.tool,'valid comma multiline doubled-quote fixture accepted',()=>assert.ok(a.run(parse(s.valid))));
 check(s.tool,'BOM-stripped application input accepted',()=>assert.ok(a.run(parse('\uFEFF'+s.valid))));
 check(s.tool,'failed input clears old result and locks every export',()=>{a.run(s.reset);a.nodes.get(s.raw).value=s.bad;a.run(s.calc);assert.equal(a.run('last'),null);for(const id of s.exports)assert.equal(a.nodes.get(id).disabled,true);assert.match(a.nodes.get('err').textContent,/quote|quoted/i);});
 check(s.tool,'fresh valid demo recovers after failure',()=>{a.run(s.reset);assert.ok(a.run('last'));for(const id of s.exports)assert.equal(a.nodes.get(id).disabled,false);});
 check(s.tool,'network CSP retained',()=>assert.match(a.html,/connect-src 'none'/));
 check(s.tool,'input-controlled output does not use HTML sinks',()=>assert.doesNotMatch(a.html,/innerHTML|outerHTML|insertAdjacentHTML|document\.write/));
 if(s.tool==='two-source-csv-reconciler'){
  check(s.tool,'mismatch demo six exceptions two paired records',()=>{assert.equal(a.run('last.issues.length'),6);assert.equal(a.run('last.pairedCount'),2)});
  check(s.tool,'clean demo matches selected fields',()=>{a.run('displayExample(true)');assert.equal(a.run('last.issues.length'),0)});
  check(s.tool,'aggregate excludes raw record keys and denies writes',()=>{a.run('displayExample(false);aiContract()');const x=JSON.parse(a.captures.at(-1)[1]);assert.equal(x.dataWriteAuthorized,false);assert.equal(x.containsRawRecords,false);assert.equal(x.containsRecordKeys,false);assert.doesNotMatch(JSON.stringify(x),/Widget|A-1|product_name/)});
 }else if(s.tool==='regression-plan-forge'){
  check(s.tool,'demo thirteen cases seven human specifications',()=>{assert.equal(a.run('last.cases.length'),13);assert.equal(a.run('last.cases.filter(x=>x.requires_human_review).length'),7)});
  check(s.tool,'aggregate remains unexecuted and identifiers excluded',()=>{const x=JSON.parse(JSON.stringify(a.run('aiSummary()')));assert.equal(x.actualTestsExecuted,false);assert.equal(x.anyTestPassedVerified,false);assert.equal(x.containsIdentifiers,false);assert.doesNotMatch(JSON.stringify(x),/CSV-01|SPEC-DEMO/)});
 }else{
  check(s.tool,'demo five tasks eleven days four critical',()=>{assert.equal(a.run('last.tasks.length'),5);assert.equal(a.run('last.baselineDays'),11);assert.equal(a.run('last.critical'),4)});
  check(s.tool,'two-node cycle rejected',()=>assert.throws(()=>a.run("solve(parseTasks(csvSerialize([HEAD,['AA','Sample task alpha','1','BB','PLANNED','TEAM-01','SPEC-01','CLEARED'],['BB','Sample task beta','1','AA','PLANNED','TEAM-01','SPEC-01','CLEARED']])))"),/CYCLE/));
  check(s.tool,'aggregate excludes private labels and denies work authorization',()=>{const x=JSON.parse(JSON.stringify(a.run('ai()')));assert.equal(x.workStartAuthorized,false);assert.equal(x.containsTaskIds,false);assert.doesNotMatch(JSON.stringify(x),/REQ-01|TEAM-01|SPEC-01/)});
 }
}
const out={schema:'private-contribution-application-review.v1',started_at_utc:started,finished_at_utc:new Date().toISOString(),scope:'Synthetic application function/state checks with minimal DOM; not browser event dispatch, layout, file picking or download verification',command:process.argv.join(' '),version,input_files:inputs,tests:results.length,passed:results.filter(x=>x.pass).length,failed:results.filter(x=>!x.pass).length,results};
fs.writeFileSync(report,JSON.stringify(out,null,2)+'\n');for(const r of results.filter(x=>!x.pass))console.log('FAIL '+r.tool+' :: '+r.name+' :: '+r.detail);console.log(JSON.stringify({tests:out.tests,passed:out.passed,failed:out.failed,report}));process.exitCode=out.failed?1:0;
