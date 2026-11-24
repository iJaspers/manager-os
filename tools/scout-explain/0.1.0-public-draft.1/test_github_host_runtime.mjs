import test from 'node:test';
import assert from 'node:assert/strict';
import {readPinnedGithub, gitBlobSha} from './github_host_runtime.mjs';
const target={repo:'iJaspers/manager-os',path:'SECURITY.md',commit:'57c8de2d5d7dc5b43e4108b36078c9b41e2be75a'};
const url='https://github.com/' + target.repo + '/blob/' + target.commit + '/' + target.path;
const text='Witburrow source evidence.\n';
function host(content=text, sha=gitBlobSha(content), display_url=url) {
  let calls=[];
  return {calls,tools:{mcp__GitHub__fetch_file:async (args)=>{
    calls.push(args);return {result:{content,sha,display_url}};}}};
}
const payload = (content=text) => ({content, sha:gitBlobSha(content), display_url:url, encoding:'utf-8'});
const withReply = (reply, key='mcp__GitHub__fetch_file') => ({[key]:async()=>reply});
test('known git object vector',()=>{
  assert.equal(gitBlobSha('test\n'), '9daeafb9864cf43055ae93beb0afd6c7d144bfa4');
});
test('exact pinned read and validated blob', async()=>{
  const x=host(),v=await readPinnedGithub(x.tools,target,[target]);
  assert.equal(v.text,text);assert.equal(v.sha1,gitBlobSha(text));
  assert.deepEqual(x.calls,[{repository_full_name:target.repo,path:target.path,ref:target.commit}]);
});
test('unapproved file is rejected before connector call',async()=>{
  const x=host();await assert.rejects(readPinnedGithub(x.tools,target,[]));
  assert.equal(x.calls.length,0);
});
test('tampered source rejected',async()=>{
  await assert.rejects(readPinnedGithub(host(text,'0'.repeat(40)).tools,target,[target]));
});
test('display-url mismatch rejected',async()=>{
  await assert.rejects(readPinnedGithub(host(text,gitBlobSha(text),'https://evil.example.com').tools,target,[target]));
});
test('mutable ref rejected',async()=>{
  const bad={...target,commit:'main'};
  const x=host();await assert.rejects(readPinnedGithub(x.tools,bad,[bad]));
});
test('path traversal rejected',async()=>{
  const bad={...target,path:'docs/../SECURITY.md'};
  const x=host();await assert.rejects(readPinnedGithub(x.tools,bad,[bad]));
});
test('oversized content rejected',async()=>{
  const over='x'.repeat(200001);
  await assert.rejects(readPinnedGithub(host(over).tools,target,[target]));
});
test('no connector fails',async()=>{
  await assert.rejects(readPinnedGithub({},target,[target]));
});
test('real MCP structuredContent wrapper and current host binding work',async()=>{
  let calls=[];
  const tools={mcp__codex_apps__github_fetch_file:async(args)=>{
    calls.push(args);
    return {content:[{type:'text',text:'Presentation only; not source bytes.'}],
      structuredContent:payload(),isError:false};
  }};
  const result=await readPinnedGithub(tools,target,[target]);
  assert.equal(result.text,text);
  assert.equal(result.sha1,gitBlobSha(text));
  assert.deepEqual(calls,[{repository_full_name:target.repo,path:target.path,ref:target.commit}]);
});
test('direct payload compatibility remains',async()=>{
  assert.equal((await readPinnedGithub(withReply(payload()),target,[target])).text,text);
});
test('error replies cannot promote plausible source data',async()=>{
  for (const reply of [
    {...payload(),isError:true},
    {result:payload(),isError:true},
    {structuredContent:payload(),isError:true},
    {result:{...payload(),isError:true}},
    {structuredContent:{...payload(),isError:true},isError:false},
  ]) await assert.rejects(readPinnedGithub(withReply(reply),target,[target]));
});
test('malformed error-status fields are rejected',async()=>{
  for (const isError of ['false',null,0,[]])
    await assert.rejects(readPinnedGithub(withReply({structuredContent:payload(),isError}),target,[target]));
});
test('competing or nested payload locations are rejected without precedence guessing',async()=>{
  for (const reply of [
    {result:payload(),structuredContent:payload()},
    {structuredContent:payload(),content:text},
    {structuredContent:payload(),sha:gitBlobSha(text)},
    {result:{structuredContent:payload()}},
    {structuredContent:{...payload(),result:payload()}},
    {structuredContent:null},
    {result:[]},
  ]) await assert.rejects(readPinnedGithub(withReply(reply),target,[target]));
});
test('reported encoding must identify decoded UTF-8',async()=>{
  for (const encoding of ['base64','utf-16',null,0,['utf-8']])
    await assert.rejects(readPinnedGithub(withReply({structuredContent:{...payload(),encoding}}),target,[target]));
});
test('malformed source metadata and nonexact pinned URLs are rejected',async()=>{
  for (const change of [
    {sha:null},{sha:1},{sha:gitBlobSha(text).toUpperCase()},
    {display_url:null},{display_url:false},{display_url:0},{display_url:''},
    {display_url:url+'#section'},{display_url:url+'?utm_source=copy'},
  ]) await assert.rejects(readPinnedGithub(withReply({structuredContent:{...payload(),...change}}),target,[target]));
});
test('structuredContent still rejects corrupt bytes and wrong file refs',async()=>{
  for (const change of [{content:text+'altered'}, {display_url:url.replace(target.commit,'main')}])
    await assert.rejects(readPinnedGithub(withReply({structuredContent:{...payload(),...change}}),target,[target]));
});
test('UTF-8 source vector matches git hash-object exactly',async()=>{
  const source='Café ☃️ 中文 🧰\n';
  assert.equal(gitBlobSha(source),'5fe68f608dda5057ff80041a027aed4b882c1521');
  const result=await readPinnedGithub(withReply({structuredContent:payload(source)}),target,[target]);
  assert.equal(result.text,source);
});
test('size limit applies to UTF-8 bytes, including multibyte input',async()=>{
  const source='🧰'.repeat(50001);
  await assert.rejects(readPinnedGithub(withReply({structuredContent:payload(source)}),target,[target]));
});
test('distinct host bindings require an explicit selection',async()=>{
  let calls=0;
  const tools={mcp__GitHub__fetch_file:async()=>{calls++;return payload();},
    mcp__codex_apps__github_fetch_file:async()=>{calls++;return payload();}};
  await assert.rejects(readPinnedGithub(tools,target,[target]));
  assert.equal(calls,0);
});
