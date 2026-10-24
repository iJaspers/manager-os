"""Actual local Chromium checks for sanitized synthetic Dependency Mapper."""
import os,shutil
import asyncio,csv,io,json,pathlib,traceback
from playwright.async_api import async_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1]; OUT=[]
def check(label,result,extra=''):
    success=bool(result);OUT.append({'test':label,'pass':success,'detail':str(extra)[:350]});print(('PASS ' if success else 'FAIL ')+label,flush=True)
    if not success:raise AssertionError(label+' '+str(extra))
HEAD=['task_id','title','duration_days','depends_on','status','owner_ref','source_ref','rights']
SAMPLE=[
['REQ-01','Agree synthetic requirements','2','NONE','REPORTED_DONE','TEAM-01','SPEC-01','CLEARED'],
['BUILD-01','Create harmless importer','5','REQ-01','PLANNED','TEAM-02','SPEC-02','CLEARED'],
['QA-01','Run synthetic importer checks','3','BUILD-01','PLANNED','TEAM-01','SPEC-03','CLEARED'],
['DOC-01','Write sample user instructions','2','REQ-01','PLANNED','TEAM-03','SPEC-04','CLEARED'],
['REVIEW-01','Prepare human release review','1','QA-01;DOC-01','PLANNED','TEAM-01','SPEC-05','REVIEW']]
def to_csv(rows):
    f=io.StringIO();w=csv.writer(f,lineterminator='\n');w.writerows(rows);return f.getvalue()
async def test():
 async with async_playwright() as pw:
    browser=await pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('chromium-browser'),headless=True,args=['--no-sandbox','--disable-gpu'])
    page=await browser.new_page(accept_downloads=True);page.set_default_timeout(8000)
    errors=[];requests=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url))
    html=(ROOT/'11_Project_Dependency_Map.html').read_text().replace('<link rel="stylesheet" href="styles.css">','<style>'+(ROOT/'styles.css').read_text()+'</style>').replace('<script src="common.js"></script>','<script>'+(ROOT/'common.js').read_text()+'</script>')
    await page.set_content(html,wait_until='load')
    async def text(id):return await page.locator('#'+id).inner_text()
    async def fill(rows):await page.fill('#tasksCSV',to_csv([HEAD]+rows));await page.click('#analyze')
    async def fail(name,expected='ANALYSIS BLOCKED'):
       check(name,expected in await text('status') and await page.locator('#exportAI').is_disabled(),await text('err'))
    check('five demonstration tasks',await text('mTasks')=='5')
    check('expected eleven-day precedence span',await text('mSpan')=='11')
    check('four critical tasks',await text('mCritical')=='4')
    check('two candidates for human review only',await text('mReady')=='2')
    check('rights hold and unverified completion visible','1 rights holds' in await text('findings') and '1 unverified claimed completions' in await text('findings'))
    check('baseline never implies accepted completion','NO CUSTOMER OR SOURCE ACCEPTANCE VERIFIED' in await text('status'))
    def tr_select(task):return page.locator('#results tr').filter(has=page.locator('td:first-child',has_text=task)).first
    req=await tr_select('REQ-01').locator('td').all_inner_texts()
    doc=await tr_select('DOC-01').locator('td').all_inner_texts()
    rev=await tr_select('REVIEW-01').locator('td').all_inner_texts()
    check('requirements critical path and transitive downstream count',req[3]=='0–2' and req[4]=='0' and req[5]=='YES' and req[7]=='4',req)
    check('noncritical documentation has six days float',doc[3]=='2–4' and doc[4]=='6' and doc[5]=='NO',doc)
    check('release review held by self-reported rights',rev[6].find('RIGHTS_REVIEW')>=0 and 'REVIEW_CANDIDATE' not in rev[6],rev)
    check('no browser JS errors',not errors,errors)
    check('no network requests',not requests,requests)
    check('all exports allowed only after structural validity',all([await page.locator('#'+x).is_enabled() for x in ['exportRows','exportBrief','exportAI']]))
    async with page.expect_download() as info:await page.click('#exportRows')
    rawcsv=pathlib.Path(await(await info.value).path()).read_text();parsed=list(csv.reader(io.StringIO(rawcsv)))
    check('private CSV has exact input plus computed records',len(parsed)==6 and len(parsed[0])==16 and len(parsed[1])==16)
    check('release output retains reported rights hold','RIGHTS_REVIEW' in rawcsv and 'REVIEW-01' in rawcsv)
    check('output marks estimates not actual schedules','duration_days_ESTIMATE' in parsed[0] and 'earliest_start_DAY_INDEX' in parsed[0])
    async with page.expect_download() as info:await page.click('#exportBrief')
    brief=pathlib.Path(await(await info.value).path()).read_text()
    check('brief explicitly forbids commitments','NOT A DELIVERY PROMISE' in brief and 'No automatic assignments' in brief)
    check('brief preserves private self entered scope','Synthetic report importer' in brief)
    async with page.expect_download() as info:await page.click('#exportAI')
    js=pathlib.Path(await(await info.value).path()).read_text();summary=json.loads(js)
    check('privacy-respecting PD-DEPEND schema',summary['schema']=='PD-DEPEND-1' and summary['taskCount']==5 and summary['baselineEstimatedDays']==11)
    check('JSON is aggregate with no private references',all(s not in js for s in ['REQ-01','TEAM-01','SPEC-01','synthetic requirements','Synthetic report importer']))
    check('no false authorization or completion assertions',all(summary[k] is False for k in ['sourceRightsVerified','taskCompletionVerified','clientApprovalVerified','workStartAuthorized','scheduleCommitted','paymentAuthorized','publicReleaseAuthorized','privateDataUploadAuthorized','instructionAuthority']))
    await page.fill('#assumption','Updated planning scenario')
    check('editing assumption prevents stale export',await page.locator('#exportRows').is_disabled() and 'INPUTS CHANGED' in await text('status'))
    await page.click('#analyze')
    check('fresh calculation unlocks exports',await page.locator('#exportRows').is_enabled())
    # Independent graphs and state controls.
    await fill([["ROOT-01","Root prerequisite task","4","NONE","PLANNED","TEAM-01","REF-01","CLEARED"]])
    check('one task span exact, ready means review only',await text('mSpan')=='4' and await text('mReady')=='1')
    row=await page.locator('#results tr').first.locator('td').all_inner_texts()
    check('one-task critical path is whole network',row[3]=='0–4' and row[4]=='0' and row[5]=='YES')
    alt=SAMPLE[:]; alt=[x.copy() for x in alt];alt[1][4]='BLOCKED';await fill(alt)
    check('blocked predecessor prevents dependent start',await text('mReady')=='1' and '1 blocked tasks' in await text('findings'))
    alt=[x.copy() for x in SAMPLE];alt[4][7]='CLEARED';await fill(alt)
    check('rights cleared does not override unfinished prereqs',await text('mReady')=='2' and '0 rights holds' in await text('findings'))
    alt=[x.copy() for x in SAMPLE];alt[0][4]='PLANNED';await fill(alt)
    check('no reported completion closes readiness dependency',await text('mReady')=='1' and '0 unverified claimed completions' in await text('findings'))
    alt=[x.copy() for x in SAMPLE];alt[1][2]='1';alt[3][2]='3';await fill(alt)
    check('nontrivial alternate path recomputed',await text('mSpan')=='7' and await text('mCritical')=='4')
    # Another branch ties at 8 days, so all five can be critical.
    alt=[x.copy() for x in SAMPLE];alt[1][2]='2';alt[3][2]='5';await fill(alt)
    check('parallel paths tie at common eight-day release gate',await text('mSpan')=='8' and await text('mCritical')=='5')
    # Structural fail closed.
    await fill([]);await fail('reject empty task register')
    await page.fill('#tasksCSV','incorrect,header\nA,Good title,2,NONE,PLANNED,TEAM-01,REF-01,CLEARED');await page.click('#analyze');await fail('reject wrong header')
    await fill(SAMPLE+[SAMPLE[0]]);await fail('reject duplicated task IDs')
    for i,val,label in [(0,'X','short task ID'),(0,'#hack','invalid task ID'),(2,'0','zero duration'),(2,'181','overlong duration'),(2,'1.5','fractional duration'),(2,'-10','negative duration'),(3,'UNKNOWN-99','unknown prerequisite'),(3,'BUILD-01;BUILD-01','duplicate dependency'),(3,'QA-01','self dependency'),(4,'DONE','invalid status'),(7,'YES','invalid rights'),(5,'Jane Smith','private owner name'),(6,'bad email@x.test','invalid source label'),(1,'Too','short description'),(1,'X'*501,'oversized title')]:
       row=SAMPLE[1].copy();row[i]=val;await fill([SAMPLE[0],row]);await fail(label)
    # 2-node cycle without self ref.
    cyc=[SAMPLE[0].copy(),SAMPLE[1].copy()];cyc[0][3]='BUILD-01';await fill(cyc);await fail('two-node cycle rejected')
    # actual three-node cycle via adding bridge edge.
    cyc=[SAMPLE[0].copy(),SAMPLE[1].copy(),SAMPLE[3].copy()];cyc[0][3]='DOC-01';cyc[1][3]='REQ-01';cyc[2][3]='BUILD-01';await fill(cyc);await fail('three-node cycle rejected')
    await page.fill('#tasksCSV','task_id,title,duration_days,depends_on,status,owner_ref,source_ref,rights\nA-01,"unterminated,2,NONE,PLANNED,TEAM-01,REF-01,CLEARED');await page.click('#analyze');await fail('unclosed CSV quote rejected')
    await page.fill('#tasksCSV','X'*102401);await page.click('#analyze');await fail('100 KiB input limit enforced')
    many=[[f'TASK-{n:03d}','Fictional source requirement', '1','NONE','PLANNED','TEAM-01','SPEC-01','CLEARED'] for n in range(81)]
    await fill(many);await fail('81 rows rejected')
    # 80 row boundary and no network.
    await fill(many[:80]);check('80 rows accepted',await text('mTasks')=='80' and await text('mSpan')=='1')
    row=SAMPLE[1].copy();row[1]='<img src=x onerror=alert(1)> harmless mock';await fill([SAMPLE[0],row])
    check('HTML-shaped title escaped into table text',await page.locator('#results img').count()==0 and 'img src' in await page.locator('#results').inner_text())
    row=SAMPLE[1].copy();row[1]='=HYPERLINK("https://invalid.example","secret")';await fill([SAMPLE[0],row])
    async with page.expect_download() as info:await page.click('#exportRows')
    data=pathlib.Path(await(await info.value).path()).read_text();cells=list(csv.reader(io.StringIO(data)))
    check('formula-like title neutralized in exported CSV',any(x.startswith("'=HYPERLINK") for rw in cells for x in rw))
    check('adversarial values cause zero outside requests',not requests,requests)
    check('adversarial values cause no script exceptions',not errors,errors)
    # Input file import should invalidate previous calculations.
    await page.click('#demo');await page.locator('#taskFile').set_input_files(str(ROOT/'examples/dependency_tasks_fictional.csv'))
    await page.wait_for_timeout(200)
    check('file import loads local fictional source','DOC-01' in await page.locator('#tasksCSV').input_value())
    check('file upload invalidates prior exports',await page.locator('#exportAI').is_disabled())
    await page.click('#analyze')
    check('imported local CSV generates expected baseline',await text('mTasks')=='5' and await text('mSpan')=='11')
    check('no remote network used in complete test',not requests,requests)
    check('zero browser JS errors after all cases',not errors,errors)
    await browser.close()
async def main():
 try:await test()
 except BaseException as exc:OUT.append({'test':'UNCAUGHT','pass':False,'detail':repr(exc)+'\n'+traceback.format_exc()[-1500:]})
 result={'suite':'dependency_browser_checks','tests':len(OUT),'passed':sum(x['pass'] for x in OUT),'failed':sum(not x['pass'] for x in OUT),'host':'headless Chromium, in-memory original HTML/JS/CSS, synthetic only','results':OUT}
 (ROOT/'tests/dependency_test_results.json').write_text(json.dumps(result,indent=2)+'\n')
 print('DEPEND',result['passed'],'/',result['tests'])
 if result['failed']:
    for row in OUT:
      if not row['pass']:print('FAIL',row)
    raise SystemExit(1)
if __name__=='__main__':asyncio.run(main())
