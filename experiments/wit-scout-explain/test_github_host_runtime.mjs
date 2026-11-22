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
