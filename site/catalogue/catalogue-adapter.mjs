import {project} from './projection.mjs';
export function projectWebsite(input){
 if(!input||input.schema!=='witburrow.website_projection.v1'||input.schema_version!==1||!Array.isArray(input.tools)||input.tools.length>1000||input.expected_tool_count!==input.tools.length||input.expected_total_entries!==input.tools.length+1||new Set(input.tools.map(t=>t.id)).size!==input.tools.length)throw Error('Website catalogue integrity hold');
 const m=input.management;if(!m||m.schema!=='witburrow.management.v1'||!Array.isArray(m.review_records)||!Array.isArray(m.contribution_events))throw Error('Management evidence missing');
 const reviews=new Map();for(const r of m.review_records){const k=r.id+'@'+r.version;if(reviews.has(k))throw Error('Duplicate release review');reviews.set(k,r);}
 const available=input.tools.filter(t=>t.publicly_available===true);
 const strict={schema:'witburrow.reviewed_catalogue.v1',revision:input.catalogue_revision,source_commit:m.source_commit,expected_tool_count:available.length,events:m.contribution_events,tools:available.map(t=>{const r=reviews.get(t.id+'@'+t.version)||{};return {...t,...r,id:t.id,version:t.version,status:t.lifecycle_status==='published_wip'?'wip':t.lifecycle_status==='published_preview'?'public_preview':'held',visibility:'public',source_url:t.source_url,download_url:t.download_url,zip_sha256:t.zip_sha256,zip_size_bytes:t.zip_size_bytes};})};
 const approved=project(strict),byId=new Map(approved.tools.map(t=>[t.id,t]));
 const safeFields=['id','name','legacy_name','version','category','runtime','description','keywords','availability','limits','requirements','verification','next_step','license','filename','lifecycle_status','readiness_status','tests_not_run'];
 const tools=input.tools.map(t=>{
   if(typeof t.id!=='string'||typeof t.name!=='string'||typeof t.version!=='string'||typeof t.category!=='string'||typeof t.runtime!=='string'||typeof t.description!=='string'||!Array.isArray(t.keywords)||!t.keywords.every(k=>typeof k==='string'))throw Error('Card metadata hold');
   const out={};for(const k of safeFields)if(t[k]!==undefined)out[k]=t[k];
   const approvedTool=byId.get(t.id);
   out.publicly_available=!!approvedTool&&['public_preview','wip'].includes(approvedTool.status);
   out.public_ready=out.publicly_available&&t.lifecycle_status==='published_preview'&&t.public_ready===true;
   if(approvedTool){Object.assign(out,approvedTool);out.release_url=approvedTool.source_url;}
   else{out.download_url=null;out.release_url=null;if(t.publicly_available===true)out.availability='Metadata held for review';else if(t.lifecycle_status!=='private_candidate')throw Error('Unknown unpublished lifecycle');}
   return out;
 });
 return {...approved,tools,expected_total_entries:input.expected_total_entries,expected_tool_count:input.expected_tool_count,catalogue_revision:input.catalogue_revision,publication_revision:input.publication_revision,approved_tool_leaderboard:tools.filter(t=>t.publicly_available).map(t=>({id:t.id,version:t.version,status:t.lifecycle_status==='published_wip'?'WIP_SOURCE_UNRANKED':'PUBLIC_UNRANKED',source_url:t.source_url})),problem_leaderboard:[]};
}
