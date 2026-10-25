'use strict';
// Reviewer-authored bounded synthetic parser tests. Node VM is capability reduction,
// NOT an OS security boundary. The reviewed candidate is evaluated with no require,
// process, fetch, socket, filesystem, browser, or credential interfaces supplied.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const target = path.resolve(process.argv[2]);
const report = path.resolve(process.argv[3]);
if (!report.includes(path.sep + 'reviewer' + path.sep)) throw Error('Reports must stay in reviewer/');
const files = process.argv.slice(4).length ? process.argv.slice(4).map(p => path.resolve(target,p)) : [
 'two-source-csv-reconciler', 'regression-plan-forge', 'dependency-critical-path-mapper'
].map(n => path.join(target,'tools',n,'0.1.0-draft.1','common.js'));
const valid = [
 ['plain rows','a,b\n1,two',[['a','b'],['1','two']]],
 ['quoted commas','a,b\n1,"blue,green"',[['a','b'],['1','blue,green']]],
 ['doubled quotes','a,b\n1,"say ""hello"""',[['a','b'],['1','say "hello"']]],
 ['embedded LF','a,b\n1,"first\nsecond"',[['a','b'],['1','first\nsecond']]],
 ['embedded CRLF','a,b\r\n1,"first\r\nsecond"\r\n',[['a','b'],['1','first\r\nsecond']]],
 ['embedded CR','a,b\r1,"first\rsecond"\r',[['a','b'],['1','first\rsecond']]],
 ['quoted empty field','a,b\n1,""',[['a','b'],['1','']]],
 ['empty middle field','a,b,c\n1,,3',[['a','b','c'],['1','','3']]],
 ['empty final field','a,b,c\n1,two,',[['a','b','c'],['1','two','']]],
 ['empty initial field','a,b\n,two',[['a','b'],['','two']]],
 ['all quoted headers','"a","b"\n"1","two"',[['a','b'],['1','two']]],
 ['space after closing quote preserved compatibility','a,b\n1,"two" \t',[['a','b'],['1','two']]],
 ['space before delimiter after quoted field','a,b\n"1" \t,"two"',[['a','b'],['1','two']]],
 ['unquoted spaces preserved','a,b\n 1 , two ',[['a','b'],[' 1 ',' two ']]],
 ['Unicode','a,b\n1,"é😀漢字"',[['a','b'],['1','é😀漢字']]],
 ['single quote content','a,b\n1,it\'s fine',[['a','b'],['1',"it's fine"]]],
 ['one literal double quote','a,b\n1,""""',[['a','b'],['1','"']]],
 ['two literal double quotes','a,b\n1,""""""',[['a','b'],['1','""']]],
 ['blank lines ignored compatibility','\n\r\na,b\n\n1,two\n',[['a','b'],['1','two']]],
 ['quoted blank row ignored compatibility','a,b\n" ","\t"\n1,two',[['a','b'],['1','two']]],
 ['empty input','',[]],
 ['header only','a,b',[['a','b']]],
 ['comma and newline inside quoted field','a,b\n1,"left,\nright"',[['a','b'],['1','left,\nright']]],
 ['formula-shaped input remains inert text','a,b\n1,=1+1',[['a','b'],['1','=1+1']]],
 ];
const invalid = [
 ['bare quote middle','a,b\n1,ab"cd'],
 ['bare quote at end','a,b\n1,ab"'],
 ['bare quote first row','ab"cd,b\n1,two'],
 ['bare quote followed by comma','a,b\n1,ab",'],
 ['bare quote followed by newline','a,b\n1,ab"\n'],
 ['two bare quotes','a,b\n1,ab""cd'],
 ['quote after unquoted space','a,b\n1, "two"'],
 ['quote after unquoted tab','a,b\n1,\t"two"'],
 ['unclosed quoted field','a,b\n1,"two'],
 ['unclosed escape sequence','a,b\n1,"two""'],
 ['character immediately after quote','a,b\n1,"two"x'],
 ['character after closing quote whitespace','a,b\n1,"two" x'],
 ['quote after closing quote whitespace','a,b\n1,"two" "'],
 ['bare quote after previous quoted row','a,b\n1,"good"\n2,bad"row'],
 ['bare quote after earlier empty field','a,b,c\n1,,bad"row'],
 ];
const startedAt = new Date().toISOString();
const results=[]; const inputFiles=[];
function check(tool,name,fn) { try{fn();results.push({tool,name,pass:true});} catch(e){results.push({tool,name,pass:false,detail:String(e.message).slice(0,800)});} }
for(const file of files) {
 const tool=path.relative(target,file), source=fs.readFileSync(file,'utf8');
 inputFiles.push({path:tool,sha256:crypto.createHash('sha256').update(source).digest('hex')});
 const ctx=vm.createContext(Object.create(null),{codeGeneration:{strings:false,wasm:false}});
 vm.runInContext(source,ctx,{filename:tool,timeout:500});
 const run=code=>vm.runInContext(code,ctx,{timeout:100});
 for(const [name,input,expected] of valid) check(tool,'valid: '+name,()=>assert.deepEqual(JSON.parse(JSON.stringify(run('parseCSV('+JSON.stringify(input)+')'))),expected));
 for(const [name,input] of invalid) check(tool,'reject: '+name,()=>assert.throws(()=>run('parseCSV('+JSON.stringify(input)+')'),/quote|quoted/i));
 for(const prefix of ['=1+1','+1','-1','@SUM(A1)','\t=1','\r=1','  =1']) check(tool,'formula safe export: '+JSON.stringify(prefix),()=>{
   const cell=run('parseCSV(csvSerialize([['+JSON.stringify(prefix)+']]))[0][0]'); assert.equal(cell,"'"+prefix);
 });
 const roundtrip=[['id','value'],['R-1','comma, value'],['R-2','say "hello"'],['R-3','multi\nline'],['R-4','Unicode é😀']];
 check(tool,'serializer roundtrip',()=>assert.deepEqual(JSON.parse(JSON.stringify(run('parseCSV(csvSerialize('+JSON.stringify(roundtrip)+'))'))),roundtrip));
 check(tool,'host I/O globals unavailable',()=>assert.equal(run("[typeof require,typeof process,typeof fetch,typeof XMLHttpRequest,typeof WebSocket].join(',')"),'undefined,undefined,undefined,undefined,undefined'));
}
const out={schema:'private-contribution-review.v1',scope:'Independent reviewer parser regressions; synthetic-only Node VM, not rendered browser or external contributor acceptance',started_at_utc:startedAt,finished_at_utc:new Date().toISOString(),node:process.version,command:process.argv.join(' '),target,input_files:inputFiles,tests:results.length,passed:results.filter(x=>x.pass).length,failed:results.filter(x=>!x.pass).length,results};
fs.writeFileSync(report,JSON.stringify(out,null,2)+'\n');
for(const r of results.filter(x=>!x.pass)) console.log('FAIL '+r.tool+' :: '+r.name+' :: '+r.detail);
console.log(JSON.stringify({tests:out.tests,passed:out.passed,failed:out.failed,report}));
process.exitCode=out.failed?1:0;
