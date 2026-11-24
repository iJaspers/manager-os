/** Host-owned GitHub MCP adapter for the WIT Scout experiment.
 *
 * Only allowlisted, immutable commit/file targets are fetched. This script
 * needs an explicitly bound GitHub fetch_file function injected by the host
 * (the legacy or current connector name below). It does not do network
 * requests independently or load untrusted code.
 * The Git object hash protects against mismatched provider bytes, not forged
 * tool metadata or adversarial page content.
 */
function utf8Bytes(s) {
  const encoded = encodeURIComponent(s), out = [];
  for (let i = 0; i < encoded.length; i++) {
    if (encoded[i] === '%') {
      out.push(parseInt(encoded.slice(i + 1, i + 3), 16)); i += 2;
    } else out.push(encoded.charCodeAt(i));
  }
  return out;
}
export function sha1(raw) {
  const bytes = raw.slice(), n = BigInt(bytes.length) * 8n;
  bytes.push(128);
  while (bytes.length % 64 !== 56) bytes.push(0);
  for (let k = 7; k >= 0; k--) bytes.push(Number((n >> BigInt(8 * k)) & 255n));
  let h0 = 0x67452301, h1 = 0xEFCDAB89, h2 = 0x98BADCFE;
  let h3 = 0x10325476, h4 = 0xC3D2E1F0;
  for (let start = 0; start < bytes.length; start += 64) {
    const w = new Array(80);
    for (let i = 0; i < 16; i++) {
      const p = start + i * 4;
      w[i] = ((bytes[p] << 24) | (bytes[p+1] << 16) |
             (bytes[p+2] << 8) | bytes[p+3]) >>> 0;
    }
    for (let i = 16; i < 80; i++) {
      const a = w[i-3] ^ w[i-8] ^ w[i-14] ^ w[i-16];
      w[i] = ((a << 1) | (a >>> 31)) >>> 0;
    }
    let a=h0, b=h1, c=h2, d=h3, e=h4;
    for (let i=0; i<80; i++) {
      let f,k;
      if (i < 20) { f=(b&c)|(~b&d); k=0x5A827999; }
      else if (i < 40) { f=b^c^d; k=0x6ED9EBA1; }
      else if (i < 60) { f=(b&c)|(b&d)|(c&d); k=0x8F1BBCDC; }
      else { f=b^c^d; k=0xCA62C1D6; }
      const t = (((((a << 5) | (a >>> 27)) + f + e + k + w[i])) >>> 0);
      e=d; d=c; c=((b << 30) | (b >>> 2)) >>> 0; b=a; a=t;
    }
    h0=(h0+a)>>>0; h1=(h1+b)>>>0; h2=(h2+c)>>>0;
    h3=(h3+d)>>>0; h4=(h4+e)>>>0;
  }
  return [h0,h1,h2,h3,h4].map(v=>v.toString(16).padStart(8,'0')).join('');
}
export function gitBlobSha(content) {
  if (typeof content !== 'string') throw Error('Expected UTF-8 content');
  const raw = utf8Bytes(content);
  const header = utf8Bytes('blob ' + raw.length + '\0');
  return sha1([...header, ...raw]);
}
function connectorData(reply) {
  const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);
  const owns = (value, key) => Object.prototype.hasOwnProperty.call(value, key);
  const checkError = value => {
    if (owns(value, 'isError') && value.isError !== false)
      throw Error('GitHub connector reported an error or invalid status');
  };
  if (!object(reply)) throw Error('Invalid GitHub connector response');
  checkError(reply);
  const wrappers = ['result', 'structuredContent'].filter(key => owns(reply, key));
  if (wrappers.length > 1) throw Error('Ambiguous GitHub connector response');
  let data = reply;
  if (wrappers.length) {
    // MCP content blocks are presentation only. Never parse them as source
    // bytes or let a second payload location silently override this one.
    if (['sha', 'display_url', 'encoding'].some(key => owns(reply, key)) ||
        (owns(reply, 'content') && !Array.isArray(reply.content)))
      throw Error('Conflicting GitHub connector payload locations');
    data = reply[wrappers[0]];
    if (!object(data) || ['result', 'structuredContent'].some(key => owns(data, key)))
      throw Error('Invalid or nested GitHub connector payload');
    checkError(data);
  }
  if (owns(data, 'encoding') && data.encoding !== 'utf-8')
    throw Error('Expected decoded UTF-8 GitHub source');
  return data;
}
export async function readPinnedGithub(tools, target, approved) {
  const legacy = tools?.mcp__GitHub__fetch_file;
  const current = tools?.mcp__codex_apps__github_fetch_file;
  if (typeof legacy === 'function' && typeof current === 'function' && legacy !== current)
    throw Error('Ambiguous host GitHub connector binding');
  const fetchFile = typeof legacy === 'function' ? legacy : current;
  if (typeof fetchFile !== 'function')
    throw Error('Trusted GitHub connector unavailable');
  if (!target || !Array.isArray(approved) || !approved.some(t =>
      t.repo === target.repo && t.path === target.path && t.commit === target.commit))
    throw Error('Not on host-approved source allowlist');
  const repo = target.repo, path = target.path, commit = target.commit;
  if (!/^[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+$/.test(repo) ||
      !/^[a-zA-Z0-9_./-]+$/.test(path) ||
      path.split('/').some(x => !x || x === '.' || x === '..') ||
      !/^[a-f0-9]{40}$/.test(commit)) throw Error('Invalid pinned source target');
  const url = 'https://github.com/' + repo + '/blob/' + commit + '/' + path;
  const reply = await fetchFile.call(tools, {repository_full_name:repo,path,ref:commit});
  const data = connectorData(reply);
  if (!data || typeof data.content !== 'string' ||
      data.content.length > 200000 || utf8Bytes(data.content).length > 200000 || !data.content.trim() ||
      typeof data.sha !== 'string' || !/^[a-f0-9]{40}$/.test(data.sha) ||
      data.sha !== gitBlobSha(data.content) ||
      (Object.prototype.hasOwnProperty.call(data, 'display_url') && data.display_url !== url))
    throw Error('Connector response integrity failure');
  return {schema:'wit.github-connector-read.v1', requested_url:url,
    final_url:url, retrieval_method:'github_connector',
    provider_ref:'github-blob:' + data.sha, sha1:data.sha,
    text:data.content, observed_at:new Date().toISOString()};
}
