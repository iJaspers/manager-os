// Pure data only. No network, dynamic imports, eval, tool execution or writes.
const statuses = new Set(['public_preview','wip','held','withdrawn']);
const text = (v, max=4000) => typeof v === 'string' && v.trim().length > 0 && v.length <= max;
const id = v => text(v,100) && /^[a-z0-9][a-z0-9._-]*$/.test(v);
const sha = v => typeof v === 'string' && /^[a-f0-9]{40}$/.test(v);
const digest = v => typeof v === 'string' && /^[a-f0-9]{64}$/.test(v);
function url(v,hosts) {if(typeof v!=='string')return false;try {const u=new URL(v);return v===u.href&&u.protocol==='https:'&&!u.username&&!u.password&&!u.port&&hosts.includes(u.hostname);}catch{return false;}}
const github = v => url(v,['github.com']) && !new URL(v).search && !new URL(v).hash && new URL(v).pathname.startsWith('/iJaspers/manager-os/');
const reviewUrl = v => github(v) && /^\/iJaspers\/manager-os\/(?:pull\/[1-9][0-9]*|commit\/[a-f0-9]{40})$/.test(new URL(v).pathname);
const pinned = (v,commit,version,kind) => github(v) && new URL(v).pathname.startsWith('/iJaspers/manager-os/'+kind+'/'+commit+'/tools/') && (kind==='tree' ? new URL(v).pathname.endsWith('/'+version) : new URL(v).pathname.includes('/'+version+'/')); 
const artifact = v => url(v,['0673fc92-1e06-494f-9e10-27641a3a4576.usrfiles.com']);
const list = v => Array.isArray(v) && v.length<=100 && v.every(x=>text(x));
export function project(doc) {
  if (!doc || doc.schema!=='witburrow.reviewed_catalogue.v1' || !text(doc.revision,100) || !sha(doc.source_commit) || !Array.isArray(doc.tools) || doc.tools.length>1000 || doc.expected_tool_count!==doc.tools.length || !Array.isArray(doc.events) || doc.events.length>10000) throw Error('Catalogue integrity hold');
  const seen=new Set(), holds=[], tools=[], eventIds=new Map(), credits=new Map();
  for(const t of doc.tools) {
    if(!id(t.id)||seen.has(t.id)) throw Error('Duplicate or invalid tool identity');
    seen.add(t.id);
    const issues=[];
    if(!text(t.name,200)||!text(t.version,100)||!statuses.has(t.status)) issues.push('identity/status');
    if(t.visibility!=='public') { holds.push({id:t.id,reasons:['not approved public metadata']});continue; }
    if(!list(t.known_failures)||(t.known_failures.length===0&&t.no_known_failures_declared!==true)||!text(t.verification)||!text(t.next_step)||!text(t.limits))issues.push('missing limitations/evidence');
    if(!t.review || t.review.privacy!=='approved'||t.review.license!=='approved'||t.review.authority!=='approved'||!(reviewUrl(t.review.reference)||t.review.reference===t.provenance_url||t.review.reference===t.source_url.replace('/tree/','/blob/')+'/TEST_RESULTS.md'))issues.push('review incomplete');
    if(!text(t.license,200)||!sha(t.source_commit)||!pinned(t.source_url,t.source_commit,t.version,'tree')||!pinned(t.provenance_url,t.source_commit,t.version,'blob')||!['PROVENANCE.md','PROVENANCE.json'].some(f=>t.provenance_url===t.source_url.replace('/tree/','/blob/')+'/'+f))issues.push('provenance not pinned');
    if(['public_preview','wip'].includes(t.status) && (!artifact(t.download_url)||!digest(t.zip_sha256)||!Number.isSafeInteger(t.zip_size_bytes)||t.zip_size_bytes<=0))issues.push('artifact unverified');
    if(issues.length) {holds.push({id:t.id,reasons:issues});continue;}
    // Explicit field allowlist: never project arbitrary private metadata.
    const out={};for(const k of ['id','name','version','status','license','source_commit','source_url','provenance_url','known_failures','known_failures_scope','verification','next_step','limits'])out[k]=t[k];
    if(['public_preview','wip'].includes(t.status))for(const k of ['download_url','zip_sha256','zip_size_bytes'])out[k]=t[k];
    out.review_reference=t.review.reference;tools.push(out);
  }
  const eligible=new Map(tools.map(t=>[t.id,t]));
  for(const e of doc.events) {
    if(!e||!id(e.event_id))throw Error('Invalid event identity');
    const serialized=JSON.stringify(['event_id','tool_id','version','kind','reviewed','public_credit_consent','contributor_id','display_name','evidence_url','review_url'].map(k=>e[k]));
    if(eventIds.has(e.event_id)){if(eventIds.get(e.event_id)!==serialized)throw Error('Conflicting duplicate event');continue;}
    eventIds.set(e.event_id,serialized);
    const t=eligible.get(e.tool_id);
    if(!t||t.version!==e.version||!['accepted_contribution','pickup'].includes(e.kind)||e.reviewed!==true||e.public_credit_consent!==true||!id(e.contributor_id)||!text(e.display_name,100)||!reviewUrl(e.evidence_url)||!reviewUrl(e.review_url)) {holds.push({event_id:e.event_id,reasons:['credit evidence/consent/version hold']});continue;}
    if(!credits.has(e.contributor_id))credits.set(e.contributor_id,{contributor_id:e.contributor_id,display_name:e.display_name,accepted_contributions:0,pickups:0,evidence:[]});
    const c=credits.get(e.contributor_id);
    if(c.display_name!==e.display_name)throw Error('Conflicting contributor identity');
    // Repeated webhook receipts cannot inflate the same contribution/claim.
    const key=[e.kind,e.tool_id,e.version,e.evidence_url].join('|');
    if(c.evidence.some(x=>x.key===key))continue;
    c[e.kind==='pickup'?'pickups':'accepted_contributions']++;
    c.evidence.push({key,kind:e.kind,url:e.evidence_url,tool_id:e.tool_id,version:e.version});
  }
  return {schema:'witburrow.public_projection.v1',revision:doc.revision,source_commit:doc.source_commit,tools:tools.sort((a,b)=>a.id.localeCompare(b.id)),board:{mode:'unranked_verified_contribution_credit',usage:null,ranking:null,contributors:[...credits.values()].sort((a,b)=>a.contributor_id.localeCompare(b.contributor_id))},holds};
}
