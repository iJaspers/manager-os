import test from 'node:test';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const server=fileURLToPath(new URL('./mcp-fixture.mjs',import.meta.url));
function raw(input){return spawnSync(process.execPath,[server],{input,encoding:'utf8',timeout:5000,maxBuffer:65536,env:{PATH:process.env.PATH}});}
function call(method,params){const r=raw(JSON.stringify({jsonrpc:'2.0',id:1,method,params})+'\n');assert.equal(r.status,0);return JSON.parse(r.stdout);}
test('MCP handshake is synthetic and only advertises tools',()=>{const r=call('initialize');assert.equal(r.result.serverInfo.name,'wit-synthetic-fixture');assert.deepEqual(r.result.capabilities,{tools:{}});});
test('only one known read tool is discoverable',()=>{const r=call('tools/list');assert.equal(r.result.tools.length,1);assert.equal(r.result.tools[0].name,'wit_fixture_read');});
test('read result is real stdio output',()=>assert.deepEqual(call('tools/call',{name:'wit_fixture_read',arguments:{item:'checklist'}}).result.structuredContent.items,['notebook','pencil']));
test('unknown tool cannot execute',()=>assert.equal(call('tools/call',{name:'run_shell',arguments:{item:'checklist'}}).error.code,-32602));
test('extra argument cannot widen scope',()=>assert.equal(call('tools/call',{name:'wit_fixture_read',arguments:{item:'checklist',path:'outside'}}).error.code,-32602));
test('denied output carries error',()=>assert.equal(call('tools/call',{name:'wit_fixture_read',arguments:{item:'denied'}}).result.isError,true));
test('unsupported method refused',()=>assert.equal(call('resources/read',{uri:'file:outside'}).error.code,-32601));
test('oversized unterminated message fails before parsing',()=>assert.equal(raw('x'.repeat(65537)).status,1));
test('invalid UTF8 is not reflected',()=>{const r=raw(Buffer.from([255,10]));assert.equal(r.status,1);assert.equal(r.stderr,'');});
test('invalid JSON returns a generic error',()=>assert.equal(JSON.parse(raw('{private\n').stdout).error.code,-32700));

for(const value of [null,[],1,'text'])test('non-object JSON rejected: '+JSON.stringify(value),()=>{const r=raw(JSON.stringify(value)+'\n');assert.equal(r.status,0);assert.equal(r.stderr,'');assert.equal(JSON.parse(r.stdout).error.code,-32600);});
