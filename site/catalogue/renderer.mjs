import {projectWebsite} from './catalogue-adapter.mjs';
import {parseStrictJSON} from './strict-json.mjs';
import {project} from './projection.mjs';
// Integration MUST serve this reviewed module locally/pinned, never execute incoming tool code.
const SOURCE='https://raw.githubusercontent.com/iJaspers/manager-os/main/tools/CATALOGUE.json';
async function boundedBody(response) {
  const limit=2097152;
  if(Number(response.headers.get('content-length'))>limit)throw Object.assign(Error('Catalogue size hold'),{terminal:true});
  if(!response.body)throw Object.assign(Error('Empty catalogue'),{terminal:true});
  const reader=response.body.getReader(),chunks=[];let size=0;
  try{while(true){const {done,value}=await reader.read();if(done)break;size+=value.byteLength;if(size>limit){await reader.cancel();throw Object.assign(Error('Catalogue size hold'),{terminal:true});}chunks.push(value);}}finally{reader.releaseLock();}
  const bytes=new Uint8Array(size);let offset=0;for(const chunk of chunks){bytes.set(chunk,offset);offset+=chunk.byteLength;}try{return new TextDecoder('utf-8',{fatal:true}).decode(bytes);}catch{throw Object.assign(Error('Invalid UTF-8'),{terminal:true});}
}
export async function load(fetcher=fetch, sleep=ms=>new Promise(r=>setTimeout(r,ms))) {
  for(let attempt=0;attempt<3;attempt++) {
    try {
      const response=await fetcher(SOURCE,{cache:'no-store',credentials:'omit',referrerPolicy:'no-referrer',signal:AbortSignal.timeout(10000)});
      if(!response.ok){if(response.status!==429&&response.status<500)throw Object.assign(Error('Catalogue unavailable'),{terminal:true});throw Error('Temporary source error');}
      const body=await boundedBody(response);
      try{const d=parseStrictJSON(body);return d.schema==='witburrow.website_projection.v1'?projectWebsite(d):project(d);}catch(error){error.terminal=true;throw error;}
    }catch(error){if(error.terminal||attempt===2)throw error;await sleep(250*2**attempt);}
  }
}
export function render(root, data, document=root.ownerDocument) {
  const node=(tag,value,parent=root)=>{const e=document.createElement(tag);e.textContent=value;parent.append(e);return e;};
  root.replaceChildren();node('h2','Wit library');node('p',`Maintainer-reviewed catalogue revision: ${data.revision}. Contribution credit is not usage or popularity.`);
  for(const t of data.tools){const card=node('section','');node('h3',`${t.name} ${t.version} · ${t.availability||t.status}`,card);for(const k of ['verification','limits','next_step'])node('p',t[k],card);for(const f of t.known_failures||[])node('p',`Known failure: ${f}`,card);if(t.download_url){const a=node('a','Download reviewed source ZIP',card);a.href=t.download_url;a.rel='noopener noreferrer';}node('p',`Licence: ${t.license}`,card);for(const [label,key] of [['Pinned source','source_url'],['Provenance','provenance_url'],['Review record','review_reference']]){if(!t[key])continue;const a=node('a',label,card);a.href=t[key];a.rel='noopener noreferrer';}if(t.zip_sha256)node('p',`ZIP SHA-256: ${t.zip_sha256}; ${t.zip_size_bytes} bytes`,card);}
  node('h2','Reviewed contribution credit · unranked');
  if(!data.board.contributors.length)node('p','No verified public contribution credit recorded. Usage is not measured.');
  for(const c of data.board.contributors){node('p',`${c.display_name}: ${c.accepted_contributions} accepted contributions; ${c.pickups} recorded pickups. Neither is a usage count.`);for(const e of c.evidence){const a=node('a',`${e.kind}: ${e.tool_id}@${e.version}`);a.href=e.url;a.rel='noopener noreferrer';}}
  if(data.holds.length)node('p',`${data.holds.length} metadata records held for review. No unverified downloads or credit published.`);
}
export async function mount(root){try{render(root,await load());}catch{root.replaceChildren();const p=root.ownerDocument.createElement('p');p.textContent='Live catalogue unavailable or held for integrity review. No current download or ranking is asserted. Please consult the versioned repository and existing release notices.';root.append(p);}}
