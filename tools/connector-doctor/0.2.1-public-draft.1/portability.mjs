/** Original WIT metadata helpers. No permissions, credentials, host config or I/O. */
import {sha256,evaluate} from './connector-doctor.mjs';
const object=x=>x!==null&&typeof x==='object'&&!Array.isArray(x)&&Object.getPrototypeOf(x)===Object.prototype;
const exact=(x,keys)=>object(x)&&Object.keys(x).length===keys.length&&keys.every(k=>Object.hasOwn(x,k));
const token=x=>typeof x==='string'&&/^[a-z0-9_.-]{1,80}$/i.test(x);
const hash=x=>typeof x==='string'&&/^[a-f0-9]{64}$/.test(x);
function reject(){throw new Error('INVALID_METADATA');}
export function preferences(x){
  if(!exact(x,['language','detail','mode'])||!['en','fr','es'].includes(x.language)||!['brief','normal','detailed'].includes(x.detail)||!['everyday','power','super'].includes(x.mode)) reject();
  return {language:x.language,detail:x.detail,mode:x.mode};
}
export const revision=x=>sha256(JSON.stringify(preferences(x)));
export function planPreferences(current,desired){
  const before=preferences(current),after=preferences(desired);
  return {schema:'wit.preferences-plan.v1',expected_revision:revision(before),next_revision:revision(after),before,after,changed:revision(before)!==revision(after)};
}
export function checkPlan(plan,current){
  if(!exact(plan,['schema','expected_revision','next_revision','before','after','changed'])||plan.schema!=='wit.preferences-plan.v1'||typeof plan.changed!=='boolean') reject();
  const expected=planPreferences(plan.before,plan.after);
  if(plan.expected_revision!==expected.expected_revision||plan.next_revision!==expected.next_revision||plan.changed!==expected.changed) reject();
  if(revision(current)!==plan.expected_revision) throw new Error('DRIFT_CONFLICT');
  return expected;
}
export function handoff(x){
  if(!exact(x,['schema','preferences','checkpoint','requirements'])||x.schema!=='wit.handoff.v1') reject();
  const p=preferences(x.preferences),c=x.checkpoint;
  if(!exact(c,['tool_id','version','step_id','artifact_sha256'])||!['tool_id','version','step_id'].every(k=>token(c[k]))||!hash(c.artifact_sha256)) reject();
  if(!Array.isArray(x.requirements)||x.requirements.length>25) reject();
  const requirements=x.requirements.map(r=>{
    if(!exact(r,['connector','tool','action'])||!token(r.connector)||!token(r.tool)||r.action!=='read') reject();
    return {connector:r.connector,tool:r.tool,action:'read'};
  });
  if(new Set(requirements.map(r=>r.connector+':'+r.tool)).size!==requirements.length) reject();
  return {schema:x.schema,preferences:p,checkpoint:{...c},requirements};
}
// Only the CURRENT trusted adapter can supply these observations. A saved handoff
// cannot carry a connection, account, approval or execution claim.
export function reviewResume(saved,current){
  const h=handoff(saved);
  const checks=h.requirements.map(r=>{
    const g=evaluate({...current,...r,target:'resume-capability-check',payload:'',approval:undefined});
    return {...r,status:g.status,next_action:g.next_action};
  });
  return {status:checks.some(c=>c.status==='DENIED')?'DENIED':checks.every(c=>c.status==='READY_TO_REQUEST')?'RECHECK_TARGET_AND_AUTHORIZE':'CONVERSATION_FALLBACK',checks,
    can_execute:false,executed:false,checkpoint_verified:false,
    next_action:'Recover the artifact through the existing owner record, compare its hash, then recheck the exact target and current host authorization. The handoff is not evidence of completion or permission.'};
}
export function capabilityDrift(before,after,requirements){
  const dummy={schema:'wit.handoff.v1',preferences:{language:'en',detail:'normal',mode:'everyday'},checkpoint:{tool_id:'synthetic',version:'0',step_id:'inspect',artifact_sha256:'0'.repeat(64)},requirements};
  const a=reviewResume(dummy,before).checks,b=reviewResume(dummy,after).checks;
  return {context_changed:['host','session','account'].some(k=>before?.[k]!==after?.[k]),
    changes:b.flatMap((c,i)=>c.status===a[i].status?[]:[{connector:c.connector,tool:c.tool,before:a[i].status,after:c.status}]),
    can_execute:false,requires_fresh_authorization:true};
}
