/** Local adapter for the existing RC1/host-receipt journey. No collection or storage. */
import {createHash} from 'node:crypto';
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const object=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const exact=(x,keys)=>object(x)&&Object.keys(x).length===keys.length&&keys.every(k=>Object.hasOwn(x,k));
const types=new Set(['entry_opened','capabilities_checked','result_produced','result_confirmed','save_verified','resume_verified','blocked']);
const hash=x=>typeof x==='string'&&/^[a-f0-9]{64}$/.test(x);
const invalid=()=>({status:'HOLD',reason:'INVALID_OR_UNVERIFIED_JOURNEY',first_useful_result_ms:null,product_accepted:false});
export function measureJourney(record,artifactBytes){
 if(!exact(record,['schema','host_kind','evidence_kind','events'])||record.schema!=='wit.onboarding-events.v1'||!['chatgpt','gemini','other','synthetic'].includes(record.host_kind)||!['observed','synthetic'].includes(record.evidence_kind)||!Array.isArray(record.events)||record.events.length>30)return invalid();
 if(!Buffer.isBuffer(artifactBytes)||artifactBytes.length===0||artifactBytes.length>65536)return invalid();
 const es=record.events;
 if(es.length<4||es[0]?.kind!=='entry_opened')return invalid();
 let last=-1,stage=0,confirmed=null,started=null,saved=false,resumed=false;
 for(const e of es){
  if(!exact(e,['kind','elapsed_ms','artifact_sha256','reviewed'])||!types.has(e.kind)||!Number.isSafeInteger(e.elapsed_ms)||e.elapsed_ms<0||e.elapsed_ms<last||e.elapsed_ms>86400000||typeof e.reviewed!=='boolean'||!(e.artifact_sha256===null||hash(e.artifact_sha256)))return invalid();
  last=e.elapsed_ms;
  if(e.kind==='entry_opened'){if(stage!==0)return invalid();started=e.elapsed_ms;stage=1;}
  else if(e.kind==='capabilities_checked'){if(stage!==1||!e.reviewed)return invalid();stage=2;}
  else if(e.kind==='result_produced'){if(stage!==2||e.artifact_sha256!==sha(artifactBytes))return invalid();stage=3;}
  else if(e.kind==='result_confirmed'){if(stage!==3||!e.reviewed||e.artifact_sha256!==sha(artifactBytes))return invalid();stage=4;confirmed=e.elapsed_ms;}
  else if(e.kind==='save_verified'){if(stage!==4||!e.reviewed||e.artifact_sha256!==sha(artifactBytes))return invalid();saved=true;stage=5;}
  else if(e.kind==='resume_verified'){if(stage!==5||!e.reviewed||e.artifact_sha256!==sha(artifactBytes))return invalid();resumed=true;stage=6;}
  else if(e.kind==='blocked')return {status:'BLOCKED',first_useful_result_ms:null,product_accepted:false};
 }
 if(confirmed===null)return invalid();
 return {status:record.evidence_kind==='synthetic'?'SYNTHETIC_ONLY':'OBSERVATION_REQUIRES_INDEPENDENT_REVIEW',host_kind:record.host_kind,
  first_useful_result_ms:confirmed-started,artifact_sha256:sha(artifactBytes),save_verified:saved,resume_verified:resumed,
  product_accepted:false,limits:'Timing and artifact consistency only; caller-supplied event records are not authenticated. Usefulness needs human confirmation; no provider compatibility or tenant-isolation proof.'};
}
