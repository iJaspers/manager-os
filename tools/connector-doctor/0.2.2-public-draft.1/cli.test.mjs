import test from 'node:test';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {readFileSync} from 'node:fs';
const cli=new URL('./doctor-cli.mjs',import.meta.url);
const run=(input,args=[])=>spawnSync(process.execPath,[cli.pathname,...args],{input,encoding:'utf8',timeout:5000});
test('CLI evaluates the shipped fictional input',()=>{
 const r=run(readFileSync(new URL('./example.json',import.meta.url)));
 assert.equal(r.status,0);assert.equal(JSON.parse(r.stdout).status,'READY_TO_REQUEST');
 assert.equal(JSON.parse(r.stdout).can_execute,false);
});
for(const [name,input] of [['malformed JSON','{'],['oversize ASCII',' '.repeat(65537)],['oversize UTF8','é'.repeat(32769)],['invalid UTF8',Buffer.from([0xff])]])
 test('CLI rejects '+name,()=>{const r=run(input);assert.equal(r.status,1);assert.equal(r.stdout,'');assert.deepEqual(JSON.parse(r.stderr),{status:'INVALID_INPUT',executed:false});});
test('missing file does not echo a private path',()=>{const r=run('', ['fictional-missing-record.json']);assert.equal(r.status,1);assert.ok(!r.stderr.includes('fictional-missing'));});
test('stdin verification rejects missing receipt',()=>{const r=run('{}',['--verify']);assert.equal(r.status,0);assert.equal(JSON.parse(r.stdout).status,'UNVERIFIED');});
