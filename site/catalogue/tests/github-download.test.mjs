import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {projectWebsite} from '../catalogue-adapter.mjs';
const fixture=()=>JSON.parse(fs.readFileSync(new URL('../../../tools/CATALOGUE.json',import.meta.url)));
const id='wit.connector-doctor';
test('same-commit exact repository ZIP is listed as WIP, never ready',()=>{
 const p=projectWebsite(fixture()),t=p.tools.find(t=>t.id===id);
 assert.equal(t.publicly_available,true);assert.equal(t.public_ready,false);
 assert.equal(p.holds.length,0);assert.match(t.download_url,/raw\.githubusercontent\.com/);
});
for(const [name,change] of [
 ['moving branch',s=>s.replace(/[a-f0-9]{40}/,'main')],
 ['other repository',s=>s.replace('/manager-os/','/unreviewed/')],
 ['other owner',s=>s.replace('/iJaspers/','/someone/')],
 ['other tool',s=>s.replaceAll('connector-doctor','different-tool')],
 ['other version',s=>s.replace('0.2.0-public-draft.1','0.9.0')],
 ['other commit',s=>s.replace(/[a-f0-9]{40}/,'a'.repeat(40))],
 ['query',s=>s+'?download=1'],
 ['fragment',s=>s+'#trusted'],
 ['host suffix',s=>s.replace('raw.githubusercontent.com','raw.githubusercontent.com.evil.invalid')]
])test('GitHub ZIP rejects '+name,()=>{const d=fixture();d.tools.find(t=>t.id===id).download_url=change(d.tools.find(t=>t.id===id).download_url);const p=projectWebsite(d);assert.equal(p.tools.find(t=>t.id===id).publicly_available,false);assert.equal(p.holds.length,1);});
