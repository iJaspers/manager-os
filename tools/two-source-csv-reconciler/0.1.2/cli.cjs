#!/usr/bin/env node
'use strict';
// Local, synchronous reads only; atomic result-directory creation; no network or telemetry.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {TextDecoder}=require('node:util');
const {reconcile,csvSerialize}=require('./reconcile.cjs');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
function read(p,max){const fd=fs.openSync(p,'r');try{const st=fs.fstatSync(fd);if(!st.isFile()||st.size>max)throw Error('Input must be a regular file within its size limit');const b=fs.readFileSync(fd);if(b.length>max)throw Error('Input exceeds size limit');return {text:new TextDecoder('utf-8',{fatal:true}).decode(b),sha256:hash(b)}}finally{fs.closeSync(fd)}}
function run(configPath,outPath){
 const configInput=read(configPath,16384),c=JSON.parse(configInput.text);
 const allowed=new Set(['source','destination','sourceKey','destinationKey','mapping','mode']);
 if(!c||Array.isArray(c)||Object.keys(c).some(k=>!allowed.has(k)))throw Error('Unknown configuration field');
 for(const key of ['source','destination','sourceKey','destinationKey','mapping'])if(typeof c[key]!=='string'||!c[key])throw Error('Missing configuration field: '+key);
 const resolve=p=>path.resolve(path.dirname(configPath),p);
 const source=read(resolve(c.source),300*1024),destination=read(resolve(c.destination),300*1024);
 const result=reconcile(source.text,destination.text,c.sourceKey,c.destinationKey,c.mapping,c.mode||'trim');
 const counts={};for(const i of result.issues)counts[i.code]=(counts[i.code]||0)+1;
 const summary={schema:'WIT-RECON-CLI-1',version:'0.1.2',sourceRecords:result.sourceCount,destinationRecords:result.destCount,pairedRecords:result.pairedCount,comparedCells:result.comparedCells,exceptionCounts:counts,exceptionsTotal:result.issues.length,sourceAuthorityVerified:false,realWorldCorrectnessVerified:false,dataWriteAuthorized:false,fileReady:false,containsRawRecords:false,containsRecordKeys:false,instructionAuthority:false};
 const receipt={...summary,inputHashes:{source:source.sha256,destination:destination.sha256,configuration:configInput.sha256},mode:result.mode};
 const rows=[['code','side','source_row','destination_row','record_key_PRIVATE','compared_field','source_value_PRIVATE','destination_value_PRIVATE','human_review_action'],...result.issues.map(x=>[x.code,x.side,x.src,x.dst,x.key,x.field,x.old,x.new,x.action])];
 const outputs={'summary.json':JSON.stringify(summary,null,2)+'\n','PRIVATE_receipt.json':JSON.stringify(receipt,null,2)+'\n','PRIVATE_exceptions.csv':csvSerialize(rows)};
 // Deterministic and resumable: only byte-identical existing results may be reused.
 const out=path.resolve(outPath);let exists=fs.existsSync(out);
 if(exists){const names=fs.readdirSync(out).sort();if(names.join('|')!==Object.keys(outputs).sort().join('|')||Object.entries(outputs).some(([k,v])=>fs.lstatSync(path.join(out,k)).isSymbolicLink()||fs.readFileSync(path.join(out,k),'utf8')!==v))throw Error('Existing output differs; choose a new directory');return summary}
 const parent=path.dirname(out);fs.mkdirSync(parent,{recursive:true});const tmp=fs.mkdtempSync(path.join(parent,'.recon-incomplete-'));
 try{for(const [k,v]of Object.entries(outputs))fs.writeFileSync(path.join(tmp,k),v,{mode:0o600,flag:'wx'});fs.renameSync(tmp,out)}catch(e){fs.rmSync(tmp,{recursive:true,force:true});throw e}
 return summary;
}
if(require.main===module){try{if(process.argv.length!==4)throw Error('Usage: node cli.cjs configuration.json output-directory');const r=run(process.argv[2],process.argv[3]);console.log(JSON.stringify(r));process.exitCode=r.exceptionsTotal?2:0}catch(e){console.error('Reconciliation stopped: '+e.message);process.exitCode=1}}
module.exports={run};
