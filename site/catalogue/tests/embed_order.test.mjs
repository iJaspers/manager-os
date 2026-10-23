import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import vm from 'node:vm';
const html=[0,1,2].map(i=>fs.readFileSync(new URL(`../deployment/managed-embed-${i}.candidate.html`,import.meta.url),'utf8'));
const source=fs.readFileSync(new URL('../../../tools/CATALOGUE.json',import.meta.url),'utf8');
for(const order of [[0,1,2],[0,2,1],[1,0,2],[1,2,0],[2,0,1],[2,1,0]])test('module/part order '+order.join(','),async()=>{
 const listeners={},document={body:{style:{},prepend(){}},readyState:'complete',getElementById(){return null;},querySelectorAll(){return [];},addEventListener(){}};
 const sandbox={document,location:{pathname:'/unrelated',search:''},URL,URLSearchParams,AbortSignal,TextEncoder,TextDecoder,Response,console,Event:class{constructor(type){this.type=type;}},setTimeout(){},setInterval(){},fetch:async()=>new Response(source)};
 sandbox.window=sandbox;sandbox.addEventListener=(type,f)=>(listeners[type]??=[]).push(f);sandbox.dispatchEvent=e=>(listeners[e.type]||[]).forEach(f=>f(e));vm.createContext(sandbox);
 for(const i of order)for(const [,script]of html[i].matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g))vm.runInContext(script,sandbox);
 assert.equal(sandbox.__witburrowLibraryParts.filter(x=>typeof x==='string').length,3);
 const d=await sandbox.__witManaged.load();assert.equal(d.tools.length,11);assert.equal(d.tools.filter(t=>t.publicly_available).length,6);
});
