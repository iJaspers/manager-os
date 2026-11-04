/** Playwright HTTP and optional rendered-link check. Never operates an AI account. */
import {createRequire} from 'node:module';
import {join,resolve} from 'node:path';
import {mkdirSync,writeFileSync} from 'node:fs';
import {ENTRY,BOB,checkEntry,checkBob} from './web-contract.mjs';
const [packageDir,outArg,mode]=process.argv.slice(2);
let api,browser;
try {
 if(!packageDir||!outArg||process.argv.length>5||(mode!==undefined&&mode!=='--browser'))throw new Error('USAGE');
 const out=resolve(outArg);
 const require=createRequire(join(resolve(packageDir),'package.json'));
 const meta=require('./package.json');if(meta.name!=='playwright'||meta.version!=='1.62.1')throw new Error('VERSION');
 const pw=require('./index.js');mkdirSync(out,{mode:0o700});
 // Honor an existing environment network proxy; never bypass its access rules.
 const proxy=process.env.HTTPS_PROXY||process.env.https_proxy;
 api=await pw.request.newContext({timeout:15000,ignoreHTTPSErrors:false,...(proxy?{proxy:{server:proxy}}:{})});
 const page=await api.get(ENTRY,{maxRedirects:0});
 const pageCheck=page.status()===200?checkEntry(await page.text()):{passed:false,reason:'HTTP_STATUS',http_status:page.status()};
 const asset=await api.get(BOB,{maxRedirects:0});
 const assetCheck=asset.status()===200?checkBob(await asset.body()):{passed:false,reason:'HTTP_STATUS',http_status:asset.status()};
 let rendered={status:'NOT_RUN',reason:'Browser mode was not selected.'};
 if(mode==='--browser'){
  try {
   browser=await pw.chromium.launch({headless:true,chromiumSandbox:true});
   const context=await browser.newContext({serviceWorkers:'block',javaScriptEnabled:false});
   // Inspect only the already-read response; no untrusted page scripts or egress.
   await context.route('**/*',route=>route.abort());
   const tab=await context.newPage();
   await tab.setContent(await page.text());
   const count=await tab.locator('a').evaluateAll((links,url)=>links.filter(a=>a.href===url).length,BOB);
   rendered={status:count>0?'PASS':'FAIL',matching_links:count,scope:'Rendered static HTTP snapshot; dynamic site scripts and native AI journey not executed.'};
  }catch{rendered=browser?{status:'FAIL',reason:'Rendered snapshot check failed.'}:{status:'NOT_RUN',reason:'A usable sandboxed Chromium runtime was unavailable.'};}
 }
 const receipt={schema:'wit.web-to-bob-check.v1',playwright_version:meta.version,entry_url:ENTRY,bob_url:BOB,http_page:pageCheck,http_asset:assetCheck,rendered,native_ai_task:'NOT_RUN',first_useful_result:'NOT_MEASURED',product_accepted:false};
 writeFileSync(join(out,'receipt.json'),JSON.stringify(receipt,null,2)+'\n',{mode:0o600,flag:'wx'});console.log(JSON.stringify(receipt,null,2));
 if(!pageCheck.passed||!assetCheck.passed||rendered.status==='FAIL'||(mode==='--browser'&&rendered.status!=='PASS'))process.exitCode=1;
}catch{console.error('Web check unavailable or incomplete; no browser or host success claimed.');process.exitCode=1;}
finally{if(api)await api.dispose();if(browser)await browser.close();}
