// Local-only checks of copied source with a minimal DOM stub. NOT a browser test.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const ROOT=path.resolve(__dirname,'../..'), results=[];
function check(name,fn){try{fn();results.push({name,pass:true});}catch(e){results.push({name,pass:false,detail:e.message});}}
function boot(dir,file){const p=path.join(ROOT,dir,dir==='dependency-critical-path-mapper'?'0.1.0-draft.2':'0.1.0-draft.1'), html=fs.readFileSync(path.join(p,file),'utf8'), nodes=new Map();
 function el(tag='div'){return {tag,value:'',textContent:'',className:'',disabled:false,children:[],files:[],addEventListener(){},replaceChildren(){this.children=[]},append(...xs){this.children.push(...xs)},appendChild(x){this.children.push(x)},remove(){},click(){}};}
 const document={getElementById(id){if(!nodes.has(id))nodes.set(id,el());return nodes.get(id)},createElement:el,body:el('body')};
 const decode=s=>s.replaceAll('&gt;','>').replaceAll('&lt;','<').replaceAll('&amp;','&').replaceAll('&quot;','"');
 for(const m of html.matchAll(/<input\b[^>]*>/g)){const id=m[0].match(/\bid="([^"]+)"/),v=m[0].match(/\bvalue="([^"]*)"/);if(id)document.getElementById(id[1]).value=v?decode(v[1]):'';}
 for(const m of html.matchAll(/<textarea\b[^>]*id="([^"]+)"[^>]*>([\s\S]*?)<\/textarea>/g))document.getElementById(m[1]).value=decode(m[2]);
 for(const m of html.matchAll(/<select\b[^>]*id="([^"]+)"[^>]*>([\s\S]*?)<\/select>/g)){const opts=[...m[2].matchAll(/<option([^>]*)>([^<]*)<\/option>/g)],o=opts.find(x=>/selected/.test(x[1]))||opts[0];document.getElementById(m[1]).value=o[1].match(/value="([^"]+)"/)?.[1]||o[2];}
 const downloads=[],context={document,TextEncoder,Intl,Blob,setTimeout(){},URL:{createObjectURL(){return 'blob:synthetic'},revokeObjectURL(){}}};vm.createContext(context);
 const code=fs.readFileSync(path.join(p,'common.js'),'utf8')+'\n'+[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(x=>x[1]).join('\n');
 vm.runInContext(code,context,{timeout:2000});vm.runInContext('downloadText=(name,text,type)=>capture(name,text,type)',context);context.capture=(name,text,type)=>downloads.push({name,text,type});
 return {run:(code)=>vm.runInContext(code,context,{timeout:2000}),nodes,downloads};}
const rec=boot('two-source-csv-reconciler','09_Two_Source_CSV_Reconciler.html');
check('reconciler: mismatch demo six exceptions',()=>assert.equal(rec.run('last.issues.length'),6));
check('reconciler: duplicate source isolated',()=>assert.equal(rec.run("last.issues.filter(x=>x.code==='DUPLICATE_KEY').length"),2));
check('reconciler: selected columns paired count two',()=>assert.equal(rec.run('last.pairedCount'),2));
check('reconciler: missing, extra, blank and mismatch classified',()=>assert(rec.run("['MISSING_DESTINATION','EXTRA_DESTINATION','BLANK_KEY','VALUE_MISMATCH'].every(c=>last.issues.some(x=>x.code===c))")));
check('reconciler: clean fixture matches',()=>{rec.run('displayExample(true)');assert.equal(rec.run('last.issues.length'),0)});
check('reconciler: input changes lock export state',()=>{rec.run('changed()');assert.equal(rec.run('last'),null);assert.equal(rec.nodes.get('exportAI').disabled,true)});
check('reconciler: byte limit enforced',()=>assert.throws(()=>rec.run("csvTable('x'.repeat(MAX_BYTES+1),'Input')"),/300 KiB/));
check('reconciler: duplicate headers rejected',()=>assert.throws(()=>rec.run("csvTable('id,id\\n1,2','Input')"),/duplicate/));
check('reconciler: missing field mapping rejected',()=>assert.throws(()=>rec.run("parseMapping('a => b',{names:['x']},{names:['b']},'id','id')"),/nonexistent/));
check('reconciler: aggregate export excludes keys and source text',()=>{rec.run('displayExample(false);aiContract()');const a=JSON.parse(rec.downloads.at(-1).text);assert.equal(a.containsRawRecords,false);assert.equal(a.dataWriteAuthorized,false);assert(!JSON.stringify(a).includes('Widget'))});
const reg=boot('regression-plan-forge','10_Regression_Plan_Forge.html');
check('regression: three requirements and thirteen draft cases',()=>{assert.equal(reg.nodes.get('mReq').textContent,'3');assert.equal(reg.nodes.get('mCases').textContent,'13')});
check('regression: seven cases need human expected outcomes',()=>assert.equal(reg.nodes.get('mReview').textContent,'7'));
check('regression: every case is unexecuted or needs review',()=>assert(reg.run("makeCases(parseRequirements($('reqCSV').value)).every(x=>['REVIEW_REQUIRED','PLAN_PREPARED_NOT_EXECUTED'].includes(x.planning_status))")));
check('regression: repeat, boundary, privacy and rollback generated',()=>assert(reg.run("['REPEAT','BOUNDARY','PRIVACY','ROLLBACK'].every(k=>makeCases(parseRequirements($('reqCSV').value)).some(x=>x.kind===k))")));
check('regression: duplicate requirement rejected',()=>assert.throws(()=>reg.run("parseRequirements(csvSerialize([HEAD,DEMO[0],DEMO[0]]))"),/Duplicate/));
check('regression: wrong header rejected',()=>assert.throws(()=>reg.run("parseRequirements('a,b\\n1,2')"),/11 exact/));
check('regression: byte limit enforced',()=>assert.throws(()=>reg.run("parseRequirements('x'.repeat(MAX_BYTES+1))"),/100 KiB/));
check('regression: input change invalidates prior plan',()=>{reg.run('invalidated()');assert.equal(reg.run('last'),null);assert.equal(reg.nodes.get('exportAI').disabled,true)});
const dep=boot('dependency-critical-path-mapper','11_Project_Dependency_Map.html');
check('dependency: five tasks and eleven estimated days',()=>{assert.equal(dep.run('last.tasks.length'),5);assert.equal(dep.run('last.baselineDays'),11)});
check('dependency: four critical tasks',()=>assert.equal(dep.run('last.critical'),4));
check('dependency: documentation has six days float',()=>assert.equal(dep.run("last.tasks.find(x=>x.task_id==='DOC-01').float"),6));
check('dependency: two human-review candidates, not work authorization',()=>{assert.equal(dep.run('last.readyForReview'),2);assert.equal(dep.run('ai().workStartAuthorized'),false)});
check('dependency: aggregate export omits identifiers',()=>{const a=JSON.stringify(dep.run('ai()'));assert(!a.includes('REQ-01'));assert.equal(dep.run('ai().containsTaskIds'),false)});
check('dependency: cycles rejected',()=>assert.throws(()=>dep.run("solve(parseTasks(csvSerialize([HEAD,['AA','Sample alpha','1','BB','PLANNED','TEAM-01','SPEC-01','CLEARED'],['BB','Sample bravo','1','AA','PLANNED','TEAM-01','SPEC-01','CLEARED']])))"),/CYCLE/));
check('dependency: missing dependency rejected',()=>assert.throws(()=>dep.run("parseTasks(csvSerialize([HEAD,['AA','Sample alpha','1','MISSING','PLANNED','TEAM-01','SPEC-01','CLEARED']]))"),/unknown dependency/));
check('dependency: self dependency rejected',()=>assert.throws(()=>dep.run("parseTasks(csvSerialize([HEAD,['AA','Sample alpha','1','AA','PLANNED','TEAM-01','SPEC-01','CLEARED']]))"),/self dependencies/));
check('dependency: byte limit enforced',()=>assert.throws(()=>dep.run("parseTasks('x'.repeat(MAX_BYTES+1))"),/100 KiB/));
check('dependency: input change locks exports',()=>{dep.run('invalidate()');assert.equal(dep.run('last'),null);assert.equal(dep.nodes.get('exportAI').disabled,true)});
for(const [name,app] of [['reconciler',rec],['regression',reg],['dependency',dep]]){
check(name+': quoted comma and doubled quote parsed',()=>assert.equal(app.run('parseCSV(\'a,b\\n1,"x,y"\\n2,"doubled ""quote"""\')[2][1]'),'doubled "quote"'));
check(name+': unclosed quote rejected',()=>assert.throws(()=>app.run('parseCSV(\'a,b\\n1,"unclosed\')'),/Unclosed/));
check(name+': formula-prefix export protected',()=>assert.equal(app.run('escapeCSV(\'=1+1\')'),'"\'=1+1"'));
check(name+': known parser gap reproduced, stray unquoted quote accepted',()=>assert.equal(app.run('parseCSV(\'a,b\\n1,ab"cd\')[1][1]'),'ab"cd'));
}
const result={scope:'Node VM logic checks with a minimal DOM stub; not browser, layout, file-host or download verification',tests:results.length,passed:results.filter(x=>x.pass).length,failed:results.filter(x=>!x.pass).length,known_issues:[{id:'CSV-BARE-QUOTE',severity:'data-validation-gap',description:'Shared parseCSV accepts a double quote inside an unquoted field rather than rejecting malformed CSV.',example:'a,b\\n1,ab"cd',affected:['two-source-csv-reconciler','regression-plan-forge','dependency-critical-path-mapper'],next_task:'Reject a quote that begins after unquoted cell content and add regression tests, preserving valid doubled quotes and multiline quoted fields.'}],results};
fs.writeFileSync(path.join(ROOT,'logic_test_results.json'),JSON.stringify(result,null,2)+'\n');for(const x of results)console.log((x.pass?'PASS ':'FAIL ')+x.name+(x.detail?': '+x.detail:''));console.log(`${result.passed}/${result.tests} passed`);if(result.failed)process.exit(1);
