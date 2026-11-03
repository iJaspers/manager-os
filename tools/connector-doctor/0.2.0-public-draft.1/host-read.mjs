/** Small read-only bridge. The host supplies trusted functions, not JSON callbacks.
 * No OAuth, credentials, URL fetching, dynamic tool imports, writes or retries.
 * The adapter must enforce its own policy and map only known callable tools.
 */
import {evaluate,verifyResult,requestHash} from './connector-doctor.mjs';
export async function runReadOnly(request,host) {
  const held=(status,reason)=>({status,reason,attempted:false,verified:false});
  if(request?.action!=='read') return held('UNSUPPORTED','This bridge only executes read operations.');
  if(!host||!['observe','authorize','invoke','now'].every(k=>typeof host[k]==='function')) return held('UNVERIFIED','No current host adapter. Use ordinary conversation.');
  let x, gate, attempted=false;
  try {
    // Discard caller-supplied connection/approval claims: current host owns them.
    const observe=async()=>{
      const o=await host.observe(request);
      return {...request,as_of:host.now(),connections:o.connections,blocked_by_policy:o.blocked_by_policy};
    };
    x=await observe(); gate=evaluate(x);
    if(gate.status!=='READY_TO_REQUEST') return {...held(gate.status,gate.reason),gate};
    if(await host.authorize(x)!==true) return held('DENIED','Current host did not authorize the exact read.');
    const authorizedHash=requestHash(x);
    // Revalidate capability/denial after authorization and immediately before call.
    x=await observe(); gate=evaluate(x);
    if(gate.status!=='READY_TO_REQUEST') return {...held(gate.status,gate.reason),gate};
    if(requestHash(x)!==authorizedHash) return held('APPROVAL_MISMATCH','Request changed after authorization.');
    attempted=true;
    const receipt=await host.invoke(x);
    const verification=verifyResult(x,receipt);
    return {...verification,attempted:true,request_sha256:requestHash(x),invocation_id:receipt?.invocation_id??null};
  } catch {
    return {status:'UNVERIFIED',reason:attempted?'Invocation outcome unknown; inspect before retry.':'Host check unavailable; use permitted conversational help.',attempted,verified:false};
  }
}
