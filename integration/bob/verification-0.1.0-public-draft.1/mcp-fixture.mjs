/** Synthetic stdio MCP fixture. Not a host connector or arbitrary command server. */
const tool={name:'wit_fixture_read',description:'Read a fixed fictional checklist.',annotations:{readOnlyHint:true,destructiveHint:false,openWorldHint:false},inputSchema:{type:'object',properties:{item:{type:'string',enum:['checklist','denied','failed']}},required:['item'],additionalProperties:false}};
function reply(id,result,error){process.stdout.write(JSON.stringify({jsonrpc:'2.0',id,...(error?{error}:{result})})+'\n');}
function handle(line){
 let m;try{m=JSON.parse(line);}catch{reply(null,null,{code:-32700,message:'Parse error'});return;}
 if(!m||typeof m!=='object'||Array.isArray(m)){reply(null,null,{code:-32600,message:'Invalid request'});return;}
 if(m.jsonrpc!=='2.0'||!['string','number'].includes(typeof m.id)){if(m.id===undefined)return;reply(null,null,{code:-32600,message:'Invalid request'});return;}
 if(m.method==='initialize')reply(m.id,{protocolVersion:'2025-06-18',capabilities:{tools:{}},serverInfo:{name:'wit-synthetic-fixture',version:'0.1.0'}});
 else if(m.method==='ping')reply(m.id,{});
 else if(m.method==='tools/list')reply(m.id,{tools:[tool]});
 else if(m.method==='tools/call'){
  const p=m.params,a=p?.arguments;
  if(p?.name!==tool.name||!a||Object.keys(a).length!==1||!['checklist','denied','failed'].includes(a.item))reply(m.id,null,{code:-32602,message:'Unsupported tool or arguments'});
  else if(a.item!=='checklist')reply(m.id,{isError:true,content:[{type:'text',text:JSON.stringify({outcome:a.item==='denied'?'denied':'failed'})}]});
  else reply(m.id,{isError:false,content:[{type:'text',text:'Fictional packing checklist: notebook, pencil.'}],structuredContent:{fixture:'checklist',items:['notebook','pencil']}});
 }else reply(m.id,null,{code:-32601,message:'Method not supported'});
}

let pending=Buffer.alloc(0);
for await(const chunk of process.stdin){
 pending=Buffer.concat([pending,chunk]);let end;
 while((end=pending.indexOf(10))>=0){
  if(end>65536){process.exit(1);}
  let line;try{line=new TextDecoder("utf-8",{fatal:true}).decode(pending.subarray(0,end));}catch{process.exit(1);}
  pending=pending.subarray(end+1);handle(line);
 }
 if(pending.length>65536)process.exit(1);
}
if(pending.length)process.exitCode=1;
