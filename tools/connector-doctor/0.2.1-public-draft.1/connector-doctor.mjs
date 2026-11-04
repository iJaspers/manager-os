/** Connector Doctor 0.2.0: Bob's advisory preflight and receipt checker.
 * Host observations are supplied claims, never permission tokens. No I/O.
 * Host policy, authentication, clock and real invocation remain host-owned.
 */
import {createHash} from 'node:crypto';
const ACTIONS = new Set(['read','draft','write','send','publish','delete','pay','schedule','manage_permissions']);
const ID = /^[a-z0-9_.:-]{1,128}$/i;
const obj = v => !!v && typeof v === 'object' && !Array.isArray(v);
const text = (v,n=512) => typeof v === 'string' && v.trim().length>0 && v.length<=n;
const time = v => typeof v==='string' && /^\d{4}-\d\d-\d\dT.*(?:Z|[+-]\d\d:\d\d)$/.test(v) ? Date.parse(v) : NaN;
const secret = /^(password|credentials?|api[_-]?key|access[_-]?token|refresh[_-]?token|authorization|client[_-]?secret)$/i;
const hasSecret = v => obj(v) ? Object.entries(v).some(([k,x])=>secret.test(k)||hasSecret(x)) : Array.isArray(v)&&v.some(hasSecret);
export const sha256 = v => createHash('sha256').update(v,'utf8').digest('hex');
const fields = ['host','session','account','connector','tool','action','target','payload','draft_location'];
export const requestHash = x => sha256(JSON.stringify(fields.map(k=>[k,x[k]??null])));
export const mutates = x => x.action!=='read' && !(x.action==='draft' && x.draft_location==='chat');
const out = (status,state,reason,next,extra={}) => ({status,connection_state:state,reason,next_action:next,
  executed:false,can_execute:false,evidence_level:'SUPPLIED_OBSERVATIONS_ONLY; host must enforce permissions',...extra});
const invalid = () => out('INVALID_INPUT','UNVERIFIED','Missing, malformed or sensitive input.','Use bounded metadata only; keep credentials in the host connection settings.');
export function evaluate(x) {
  try { if (!obj(x) || JSON.stringify(x).length>65536 || hasSecret(x)) return invalid(); } catch { return invalid(); }
  if (!['host','session','account','connector','tool'].every(k=>typeof x[k]==='string'&&ID.test(x[k])) || !ACTIONS.has(x.action)) return invalid();
  if (x.blocked_by_policy!==undefined && typeof x.blocked_by_policy!=='boolean') return invalid();
  if (x.blocked_by_policy===true) return out('DENIED','DENIED','Current host policy denies this operation.','Stop this operation. Do not reconnect, switch accounts, use mirrors or paste to bypass denial.');
  if (!Array.isArray(x.connections)||x.connections.length>50||x.connections.some(c=>!obj(c))) return invalid();
  const matches=x.connections.filter(c=>c.host===x.host&&c.id===x.connector);
  if (matches.length>1) return out('AMBIGUOUS','UNVERIFIED','Multiple connector records conflict.','Resolve current identity before use.');
  const c=matches[0];
  if (!c) return out('UNVERIFIED','UNVERIFIED','No current-host observation.','Check host tools; otherwise continue ordinary conversation without claiming app access.');
  for (const k of ['denied','revoked','supported','installed','available','authenticated','observed']) if(c[k]!==undefined&&typeof c[k]!=='boolean') return invalid();
  if(c.denied===true||c.revoked===true) return out('DENIED','DENIED','Connection denied or revoked.','Stop this operation; no alternate-route bypass.');
  const now=time(x.as_of), observed=time(c.observed_at);
  if(c.source!=='host_tool_response'||c.session!==x.session||c.account!==x.account||!Number.isFinite(now)||!Number.isFinite(observed)||observed>now||now-observed>300000)
    return out('UNVERIFIED','UNVERIFIED','Observation is stale, copied, untrusted or belongs to another context.','Inspect the current host, account and session. No inherited access.');
  if(c.supported===false) return out('UNSUPPORTED','UNSUPPORTED','Host reports no supported integration.','Use ordinary conversation for permitted work; do not promise installation.');
  if(c.installed!==true) return c.available===true
    ? out('AVAILABLE','AVAILABLE','Host lists an optional connection; it is not installed.','Use the host connection UI if the user wants this app. No credentials in chat.')
    : out('UNVERIFIED','UNVERIFIED','Installation is not established.','Check host connection settings or continue manually.');
  if(c.authenticated!==true) return out('NEEDS_CONNECTION','INSTALLED','Installed, but authentication is not established.','Reconnect through the host connection UI only when authorized; never paste credentials.');
  if(c.observed!==true||!Array.isArray(c.tools)||!c.tools.includes(x.tool)) return out('UNVERIFIED','INSTALLED','Requested callable tool was not observed.','Inspect the real tool schema; installation alone is insufficient.');
  if(!Array.isArray(c.capabilities)||c.capabilities.some(a=>!ACTIONS.has(a))) return invalid();
  if(!c.capabilities.includes(x.action)) return out('UNSUPPORTED','INSTALLED','Connector does not support this action.','Use a supported, permitted action or conversational help.');
  if(!obj(c.tool_capabilities)||!Object.hasOwn(c.tool_capabilities,x.tool)||!Array.isArray(c.tool_capabilities[x.tool])) return out('UNVERIFIED','INSTALLED','No action schema for the exact callable tool.','Inspect this tool schema; connector-level access is insufficient.');
  if(c.tool_capabilities[x.tool].some(a=>!ACTIONS.has(a))) return invalid();
  if(!c.tool_capabilities[x.tool].includes(x.action)) return out('UNSUPPORTED','INSTALLED','This exact tool cannot perform this action.','Select a supported tool and re-evaluate its scope.');
  if(!text(x.target)||typeof x.payload!=='string'||x.payload.length>32768) return invalid();
  if(x.action==='draft'&&!['chat','provider'].includes(x.draft_location)) return out('NEEDS_DETAILS','INSTALLED','Draft destination is unclear.','Choose text in chat or a draft saved in the provider account.');
  const binding={request_sha256:requestHash(x)};
  if(!mutates(x)) return out('READY_TO_REQUEST','INSTALLED','Current supplied observation supports this read or in-chat draft.','Use only the actual host tool under current permission; verify its returned result.',binding);
  const a=x.approval;
  if(!obj(a)||a.granted!==true) return out('NEEDS_APPROVAL','INSTALLED','No exact current authorization recorded.','Prepare the exact action, account, target and content; use the host approval mechanism.',binding);
  if(!text(a.id,128)||a.request_sha256!==binding.request_sha256) return out('APPROVAL_MISMATCH','INSTALLED','Approval does not match the complete current request.','Obtain authorization for this exact request.',binding);
  const issued=time(a.issued_at), expiry=time(a.expires_at);
  if(!Number.isFinite(issued)||!Number.isFinite(expiry)||issued>now||expiry<=now||expiry<=issued) return out('APPROVAL_EXPIRED','INSTALLED','Approval is expired, future-dated or lacks valid time bounds.','Recheck authority with the current host clock.',binding);
  if(!Array.isArray(x.used_approval_ids)||x.used_approval_ids.some(id=>!text(id,128))) return invalid();
  if(x.used_approval_ids.includes(a.id)) return out('APPROVAL_USED','INSTALLED','This approval already had an attempted operation.','Inspect the previous result before any retry; do not replay.',binding);
  return out('READY_TO_REQUEST','INSTALLED','Supplied scoped authorization matches; host authorization still required.','Revalidate with the host immediately before invocation, record the attempt and verify the result.',binding);
}

// The caller passes the actual observed response, never a model-written success claim.
// This validates consistency only; it cannot authenticate a forged receipt.
export function verifyResult(request, receipt) {
  const r = (status, reason) => ({status,reason,verified:status==='VERIFIED',
    evidence_level:'SUPPLIED_RECEIPT_CONSISTENCY_ONLY',retry:'Inspect actual target before retry; no automatic retry.'});
  if(!obj(request)||!obj(receipt)||evaluate(request).status!=='READY_TO_REQUEST') return r('UNVERIFIED','Missing or ineligible request or result.');
  if(receipt.source!=='host_tool_response'||!text(receipt.invocation_id,128)||receipt.request_sha256!==requestHash(request)) return r('UNVERIFIED','Receipt not bound to this host request.');
  if(receipt.outcome==='denied') return r('DENIED','Actual host denied the operation; stop.');
  if(receipt.outcome==='failed') return r('FAILED','Execution reported failure; effects may need inspection.');
  if(receipt.outcome!=='succeeded') return r('UNVERIFIED','No definitive execution result.');
  if(receipt.target!==request.target||!Number.isFinite(time(receipt.observed_at))||time(receipt.observed_at)<time(request.as_of)) return r('UNVERIFIED','Wrong target or invalid observation time.');
  if(!Number.isFinite(time(request.as_of))) return r('UNVERIFIED','Missing request time.');
  if(mutates(request)) {
    const b=receipt.readback;
    if(!obj(b)||b.source!=='host_tool_response'||b.target!==request.target||b.account!==request.account||b.payload_sha256!==sha256(request.payload)||!Number.isFinite(time(b.observed_at))||time(b.observed_at)<time(receipt.observed_at)) return r('UNVERIFIED','No matching post-action readback on the same account and target.');
  } else if(receipt.result_present!==true) return r('UNVERIFIED','A successful call without an observed result is insufficient.');
  return r('VERIFIED','Observed result fields match the request; this is not independent authentication.');
}
