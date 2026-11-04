#!/usr/bin/env node
import {openSync,readSync,closeSync} from 'node:fs';
import {evaluate,verifyResult} from './connector-doctor.mjs';
// Bound bytes consumed and allocated before decoding or JSON parsing, including stdin.
let fd;
try {
  fd=process.argv[2] && process.argv[2]!=='--verify' ? openSync(process.argv[2],'r') : 0;
  const bytes=Buffer.alloc(65537);let size=0,n;
  while(size<bytes.length && (n=readSync(fd,bytes,size,bytes.length-size,null))>0) size+=n;
  if(size>65536) throw new Error('size');
  const x=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes.subarray(0,size)));
  console.log(JSON.stringify(process.argv.includes('--verify')?verifyResult(x.request,x.receipt):evaluate(x),null,2));
} catch {
  console.error(JSON.stringify({status:'INVALID_INPUT',executed:false}));
  process.exitCode=1;
} finally {
  if(fd!==undefined && fd!==0) closeSync(fd);
}
