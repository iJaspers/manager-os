// Original synthetic application checks. Minimal DOM fixture, not browser acceptance.
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const entry=fs.readdirSync(root).find(n=>n.endsWith('.html'));
const regression=entry.startsWith('10_');
function start(){
 const nodes=new Map(),downloads=[];
 function element(){return {value:'',textContent:'',disabled:false,children:[],events:{},
  addEventListener(k,f){this.events[k]=f},appendChild(x){this.children.push(x)},replaceChildren(){this.children=[]}}}
 const document={getElementById(id){if(!nodes.has(id))nodes.set(id,element());return nodes.get(id)},createElement:element};
 const html=fs.readFileSync(path.join(root,entry),'utf8');
 for(const input of html.matchAll(/<input\b[^>]*\bid="([^"]+)"[^>]*>/g))document.getElementById(input[1]).value=input[0].match(/\bvalue="([^"]*)"/)?.[1]||'';
 const context=vm.createContext({document,TextEncoder});
 vm.runInContext(fs.readFileSync(path.join(root,'common.js'),'utf8')+'\n'+[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n'),context,{timeout:1000});
 context.capture=(name,text)=>downloads.push({name,text});vm.runInContext('downloadText=capture',context);
 const run=s=>vm.runInContext(s,context,{timeout:1000});
 const click=id=>nodes.get(id).events.click();
 const field=regression?'reqCSV':'tasksCSV',button=regression?'buildPlan':'analyze';
 const submit=value=>{nodes.get(field).value=value;nodes.get(field).events.input();click(button)};
 return {nodes,run,click,submit,downloads,field};
}
test('fictional demo produces the documented result',()=>{const a=start();assert.equal(a.nodes.get(regression?'mCases':'mSpan').textContent,regression?'13':'11');assert.equal(a.nodes.get(regression?'mReview':'mCritical').textContent,regression?'7':'4');});
test('aggregate export retains no identifiers and grants no authority',()=>{const a=start();a.click('exportAI');const s=JSON.parse(a.downloads[0].text);assert.equal(s[regression?'actualTestsExecuted':'workStartAuthorized'],false);assert.equal(s.publicReleaseAuthorized,false);assert.ok(!a.downloads[0].text.includes('SPEC-'));assert.ok(!a.downloads[0].text.includes('TEAM-'));});
test('malformed quote blocks actual handler and prevents stale export',()=>{const a=start();a.submit(a.run("HEAD.join(',')+'\\n'+DEMO[0].map((v,i)=>i===1?'bad\\\"text':v).join(',')"));assert.match(a.nodes.get('err').textContent,/quote/i);assert.equal(a.run('last'),null);assert.equal(a.nodes.get('exportAI').disabled,true);a.click('exportAI');assert.equal(a.downloads.length,0);});
test('valid retry restores usable output',()=>{const a=start();a.submit('broken');a.click('demo');assert.equal(a.nodes.get('exportAI').disabled,false);assert.equal(a.nodes.get(regression?'mCases':'mSpan').textContent,regression?'13':'11');});
test('duplicate identifiers block export',()=>{const a=start();a.submit(a.run('csvSerialize([HEAD,DEMO[0],DEMO[0]])'));assert.match(a.nodes.get('err').textContent,/duplicate/i);assert.equal(a.nodes.get('exportAI').disabled,true);});
test('UTF8 byte limit applies to actual input handler',()=>{const a=start();a.submit('é'.repeat(51201));assert.match(a.nodes.get('err').textContent,/100 KiB/);assert.equal(a.run('last'),null);});
test('wrong schema is rejected without a success claim',()=>{const a=start();a.submit('a,b\n1,2');assert.match(a.nodes.get('status').textContent,/BLOCKED/);assert.equal(a.nodes.get('exportAI').disabled,true);});
test('editing after calculation clears old results',()=>{const a=start();a.nodes.get(a.field).events.input();assert.equal(a.run('last'),null);assert.equal(a.nodes.get('exportAI').disabled,true);assert.equal(a.nodes.get('results').children.length,0);});
test('quoted commas and multiline values remain valid',()=>{const a=start();a.submit(a.run("csvSerialize([HEAD,...DEMO.map((v,i)=>i===0?v.map((x,j)=>j===1?'Synthetic, quoted\\nexample':x):v)])"));assert.equal(a.nodes.get('exportAI').disabled,false);});
test('domain negative boundary remains held',()=>{const a=start();if(regression){a.submit(a.run("csvSerialize([HEAD,DEMO[0].map((v,i)=>i===3?'ok':v)])"));assert.match(a.nodes.get('err').textContent,/characters/);}else{a.submit(a.run("csvSerialize([HEAD,['TASK-AA','Synthetic alpha','1','TASK-BB','PLANNED','TEAM-01','SPEC-01','CLEARED'],['TASK-BB','Synthetic bravo','1','TASK-AA','PLANNED','TEAM-01','SPEC-01','CLEARED']])"));assert.match(a.nodes.get('err').textContent,/CYCLE/);}assert.equal(a.nodes.get('exportAI').disabled,true);});
