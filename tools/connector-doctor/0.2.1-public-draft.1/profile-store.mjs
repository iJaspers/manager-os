/** Local, user-selected private workspace only. Never changes AI host settings. */
import {openSync,readSync,writeFileSync,closeSync,fsyncSync,renameSync,unlinkSync,mkdirSync,rmdirSync,realpathSync,lstatSync,fstatSync,constants} from 'node:fs';
import {resolve,join} from 'node:path';
import {randomUUID} from 'node:crypto';
import {preferences,revision,checkPlan,planPreferences} from './portability.mjs';
const PROFILE='wit-preferences.json',BACKUP='wit-preferences.previous.json';
export function readJSON(path){
  let fd;
  try {
    fd=openSync(path,constants.O_RDONLY|constants.O_NOFOLLOW|constants.O_NONBLOCK);
    const stat=fstatSync(fd);if(!stat.isFile()||stat.size>65536)throw new Error('INVALID_METADATA');
    // A pipe/device is not a profile. Size is bounded before JSON parsing.
    const b=Buffer.alloc(65537);let n=0,k;
    while(n<b.length&&(k=readSync(fd,b,n,b.length-n,null))>0)n+=k;
    if(n>65536)throw new Error('INVALID_METADATA');
    return JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(b.subarray(0,n)));
  } finally {if(fd!==undefined)closeSync(fd);}
}
function workspace(dir){
  const d=resolve(dir);
  if(realpathSync(d)!==d||!lstatSync(d).isDirectory())throw new Error('UNSAFE_WORKSPACE');
  return d;
}
function safeFile(p,missing=false){
  try {const s=lstatSync(p);if(!s.isFile()||s.nlink!==1)throw new Error('UNSAFE_FILE');}
  catch(e){if(!(missing&&e.code==='ENOENT'))throw e;}
}
function atomic(p,value){
  safeFile(p,true);const temp=p+'.tmp-'+randomUUID();let fd;
  try {fd=openSync(temp,'wx',0o600);writeFileSync(fd,JSON.stringify(value,null,2)+'\n');fsyncSync(fd);closeSync(fd);fd=undefined;renameSync(temp,p);}
  finally {if(fd!==undefined)closeSync(fd);try{unlinkSync(temp);}catch(e){if(e.code!=='ENOENT')throw e;}}
}
function locked(dir,fn){
  const d=workspace(dir),lock=join(d,'wit-preferences.lock');
  mkdirSync(lock,{mode:0o700});
  try{return fn(d);}finally{rmdirSync(lock);}
}
export function initializeProfile(dir,value){
  const p=preferences(value);
  return locked(dir,d=>{const f=join(d,PROFILE);let fd;try{fd=openSync(f,'wx',0o600);writeFileSync(fd,JSON.stringify(p,null,2)+'\n');fsyncSync(fd);}finally{if(fd!==undefined)closeSync(fd);}return {status:'INITIALIZED',revision:revision(p)};});
}
export function loadProfile(dir){const f=join(workspace(dir),PROFILE);safeFile(f);return preferences(readJSON(f));}
export function applyProfile(dir,plan,consent){
  if(consent!==true)throw new Error('CONSENT_REQUIRED');
  return locked(dir,d=>{
    const f=join(d,PROFILE),backup=join(d,BACKUP);safeFile(f);safeFile(backup,true);
    const checked=checkPlan(plan,preferences(readJSON(f)));
    if(!checked.changed)return {status:'UNCHANGED',revision:checked.next_revision};
    atomic(backup,checked);atomic(f,checked.after);
    const actual=loadProfile(d);if(revision(actual)!==checked.next_revision)throw new Error('READBACK_FAILED');
    return {status:'VERIFIED',revision:revision(actual),backup_revision:checked.expected_revision};
  });
}
export function rollbackProfile(dir,expectedRevision,consent){
  if(consent!==true)throw new Error('CONSENT_REQUIRED');
  return locked(dir,d=>{
    const f=join(d,PROFILE),b=join(d,BACKUP);safeFile(f);safeFile(b);
    const current=preferences(readJSON(f)),saved=readJSON(b);
    // Validate all backup fields, then bind rollback to both recorded revisions.
    const checked=checkPlan(saved,saved.before);
    if(revision(current)!==expectedRevision||expectedRevision!==checked.next_revision)throw new Error('DRIFT_CONFLICT');
    const inverse=planPreferences(current,checked.before);
    atomic(f,inverse.after);
    if(revision(loadProfile(d))!==inverse.next_revision)throw new Error('READBACK_FAILED');
    return {status:'ROLLED_BACK',revision:inverse.next_revision};
  });
}
