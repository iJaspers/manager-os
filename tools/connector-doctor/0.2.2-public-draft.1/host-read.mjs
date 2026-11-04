/** Small read-only bridge. Trusted host functions enforce actual authorization.
 * Request intent is fixed before any await. No writes, credential handling or retries.
 */
import {evaluate,verifyResult,requestHash} from './connector-doctor.mjs';
const intentFields=['host','session','account','connector','tool','action','target','payload','draft_location'];
const inputFields=new Set([...intentFields,'connections','approval','used_approval_ids','as_of','blocked_by_policy']);
function intentOf(value){
  if(!value||typeof value!=='object'||![Object.prototype,null].includes(Object.getPrototypeOf(value)))throw Error('INVALID_REQUEST');
  const descriptors=Object.getOwnPropertyDescriptors(value);
  if(Reflect.ownKeys(value).some(k=>typeof k!=='string'||!inputFields.has(k)))throw Error('UNKNOWN_REQUEST_FIELD');
  if(Object.values(descriptors).some(d=>!Object.hasOwn(d,'value')))throw Error('ACCESSOR_REQUEST');
  const intent={};
  for(const k of intentFields){
    const v=descriptors[k]?.value;
    if(v!==undefined&&(typeof v!=='string'||v.length>(k==='payload'?32768:512)))throw Error('INVALID_INTENT');
    if(v!==undefined)intent[k]=v;
  }
  if(!['host','session','account','connector','tool'].every(k=>typeof intent[k]==='string'&&/^[a-z0-9_.:-]{1,128}$/i.test(intent[k]))||typeof intent.action!=='string'||typeof intent.target!=='string'||!intent.target.trim()||typeof intent.payload!=='string')throw Error('INVALID_INTENT');
  return Object.freeze(intent);
}
function freezeJSON(value){
  const text=JSON.stringify(value);if(!text||text.length>65536)throw Error('INVALID_OBSERVATION');
  const copy=JSON.parse(text);
  const freeze=x=>{if(x&&typeof x==='object'){Object.values(x).forEach(freeze);Object.freeze(x);}return x;};
  return freeze(copy);
}
export async function runReadOnly(request,host){
  const held=(status,reason)=>({status,reason,attempted:false,verified:false});
  let intent,binding,attempted=false;
  try{intent=intentOf(request);binding=requestHash(intent);}catch{return held('INVALID_INPUT','Request must contain only bounded plain-data fields.');}
  if(intent.action!=='read')return held('UNSUPPORTED','This bridge only executes read operations.');
  if(!host||!['observe','authorize','invoke','now'].every(k=>typeof host[k]==='function'))return held('UNVERIFIED','No current host adapter. Use ordinary conversation.');
  // Pin callbacks too; replacing one during authorization cannot widen scope.
  const observeHost=host.observe.bind(host),authorize=host.authorize.bind(host),invoke=host.invoke.bind(host),now=host.now.bind(host);
  const unchanged=()=>requestHash(intentOf(request))===binding;
  try{
    const observe=async()=>{
      const o=await observeHost(intent);
      return freezeJSON({...intent,as_of:now(),connections:o.connections,blocked_by_policy:o.blocked_by_policy});
    };
    let x=await observe(),gate=evaluate(x);
    if(!unchanged())return held('APPROVAL_MISMATCH','Request changed before authorization.');
    if(gate.status!=='READY_TO_REQUEST')return {...held(gate.status,gate.reason),gate};
    // This digest was captured before callbacks, not after their side effects.
    const authorizedAt=Date.parse(x.as_of);
    if(await authorize(x)!==true)return held('DENIED','Current host did not authorize the exact read.');
    if(!unchanged())return held('APPROVAL_MISMATCH','Request changed during authorization.');
    x=await observe();gate=evaluate(x);
    if(!unchanged()||requestHash(x)!==binding)return held('APPROVAL_MISMATCH','Request changed after authorization.');
    if(gate.status!=='READY_TO_REQUEST')return {...held(gate.status,gate.reason),gate};
    const current=Date.parse(now());
    if(!Number.isFinite(current)||current<authorizedAt||current-authorizedAt>300000)return held('APPROVAL_EXPIRED','Read authorization exceeded the five-minute local check window.');
    attempted=true;
    const receipt=await invoke(x);
    if(!unchanged())return {status:'UNVERIFIED',reason:'Request changed during invocation; inspect the actual result before retry.',attempted:true,verified:false};
    const verification=verifyResult(x,receipt);
    return {...verification,attempted:true,request_sha256:binding,invocation_id:receipt?.invocation_id??null};
  }catch{
    return {status:'UNVERIFIED',reason:attempted?'Invocation outcome unknown; inspect before retry.':'Host check unavailable; use permitted conversational help.',attempted,verified:false};
  }
}
