"""A.1 functional/UI checks. No real Backend calls, no synthetic send-success responses."""
from pathlib import Path
import http.server,functools,threading,json,urllib.parse,re
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2];ASSETS=ROOT/'tests/index-layout/assets';OUT=Path('/workspace/nvs-a1-standard-evidence');OUT.mkdir(exist_ok=True);spec=json.loads((ROOT/'NVS_A1.schemas.json').read_text());ops=spec['operations'];PREFIX='/NVS-HVA-TEST/'
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
 def translate_path(self,path):return super().translate_path(path.replace(PREFIX,'/',1))
s=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)));threading.Thread(target=s.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{s.server_port}';app=base+PREFIX;checks=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);c=b.new_context(viewport={'width':1366,'height':950});calls=[];errors=[];fail=[False]
 c.add_init_script("localStorage.setItem('user',JSON.stringify({username:'QA_A1',hoTen:'Người kiểm thử',toBoPhan:'Bộ phận kiểm thử',chucVu:'Giáo viên'}));localStorage.setItem('hvaSessionToken','QA_ONLY_NOT_AUTHENTICATION');localStorage.setItem('hvaSessionExpiresAt',String(Date.now()+3600000));")
 def route(r):
  url=r.request.url
  if url.startswith(base):r.continue_();return
  if 'bootstrap-icons.min.css' in url:r.fulfill(content_type='text/css',body=(ASSETS/'bootstrap-icons.css').read_text());return
  if 'bootstrap-icons.woff2' in url:r.fulfill(content_type='font/woff2',body=(ASSETS/'bootstrap-icons.woff2').read_bytes());return
  if url.startswith('https://script.google.com/'):
   q=urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
   if r.request.method=='POST':calls.append(json.loads(r.request.post_data)['action']);r.abort();return
   calls.append(q.get('action',[''])[0]);assert calls[-1]=='getNVSMeetingPersonnel'
   if fail[0]:r.abort();return
   user={'username':'QA_A1','hoTen':'Họ tên từ nguồn thử','to':'Bộ phận từ nguồn thử','chucVu':'Giáo viên'};person={'username':'QA_COLLEAGUE','hoTen':'Đồng nghiệp thử','to':'Bộ phận thử','chucVu':'Giáo viên'}
   data={'success':True,'groups':[{'groupKey':'TEAM:QA','tenTo':'Tổ kiểm thử','kind':'TEAM','members':[user,person,{'username':'QA_STAFF','hoTen':'Nhân viên thử','to':'Bộ phận thử','chucVu':'Nhân viên'}]},{'groupKey':'WORKGROUP:QA','tenTo':'Nhóm kiểm thử','kind':'WORKGROUP','members':[person]}]}
   r.fulfill(content_type='application/javascript',body=q['callback'][0]+'('+json.dumps(data)+');');return
  r.abort()
 c.route('**/*',route);page=c.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('dialog',lambda d:d.accept())
 def goto(id):
  op=ops[id];page.goto(app+'NVS_BaoCao_A1.html?group='+op['group']+'&item='+id);page.wait_for_function("()=>document.getElementById('notice').textContent!=='Đang tải danh mục…'")
 def fill(id):
  for f in ops[id]['fields']:
   value={'number':'12','date':'2026-11-01'}.get(f['kind'],'Nội dung kiểm thử, không gửi')
   if f['kind']=='url':value='https://drive.google.com/file/d/QA_ONLY/view'
   if f['key']=='year':value='2026–2027'
   if f['key']=='to':value='2026-11-02'
   page.fill('#field-'+f['key'],value)
  if ops[id]['kind']=='link':page.fill('#field-drive','https://drive.google.com/file/d/QA_ONLY/view')
 # Complete source-defined tree, not a renamed single form.
 assert len(ops)==31;assert spec['groups']['A14']['name']=='A.1.4 – BD HSG – DTHT';assert [s['id'] for s in spec['groups']['A14']['sections']]==['hsg','support','exam','dtht']
 assert {f['key'] for f in ops['task']['fields']}!={f['key'] for f in ops['training']['fields']};assert all(f['kind']!='textarea' for f in ops['hsg-plan']['fields']);assert 'team' not in {f['key'] for f in ops['exam-plan']['fields']}
 for group,g in spec['groups'].items():
  page.goto(app+'NVS_BaoCao_A1.html?group='+group);page.wait_for_selector('#catalog [data-operation]');assert page.locator('#catalog [data-operation]').count()==sum(op['group']==group for op in ops.values());assert page.locator('#catalog [data-section]').count()==len(g['sections']);checks.append(group+' complete catalog and distinct spaces')
 # A12: exactly two balanced homeroom cards, original report route and four inclusion cards.
 page.goto(app+'NVS_BaoCao_A1.html?group=A12');page.wait_for_selector('[data-operation=homeroom-notebook]')
 home=page.locator('#catalog [data-section=homeroom]');assert home.locator('[data-operation]').count()==2
 assert home.locator('[data-operation=homeroom]').get_attribute('href')=='./BC_ChuNhiem.html'
 assert 'Đã kết nối' in home.locator('[data-operation=homeroom]').inner_text();assert 'Đang phát triển' in home.locator('[data-operation=homeroom-notebook]').inner_text()
 for width in [375,768,1366]:
  page.set_viewport_size({'width':width,'height':950});boxes=home.locator('[data-operation]').evaluate_all('(els)=>els.map(e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}})');assert abs(boxes[0]['y']-boxes[1]['y'])<1;assert abs(boxes[0]['w']-boxes[1]['w'])<1;assert abs(boxes[0]['h']-boxes[1]['h'])<1
 assert page.locator('#catalog [data-section=inclusive] [data-operation]').count()==4
 home.locator('[data-operation=homeroom-notebook]').click();page.wait_for_selector('#operation h2');assert 'Đang phát triển' in page.locator('#operation').inner_text();assert page.locator('#operation li').count()==3;assert page.locator('#operation input,#operation textarea,#operation select').count()==0
 checks.append('A12 two balanced homeroom cards, notebook safely blocked with three structural areas; original CN route and four inclusion cards preserved')
 page.goto(app+'NghiepVu.html');page.locator('details.group').first.locator('summary .chev').click();page.locator('[aria-controls=nvs-a14]').click();assert page.locator('#nvs-a14 .nvs-a-branch').count()==4;assert page.locator('#nvs-a14 a[href="./BC_DayThemHocThem.html"]').count()==1;assert page.locator('#nvs-a12 a[href="./BC_ChuNhiem.html"]').count()==1;checks.append('entry menu: four A14 branches, original CN/DTHT links')
 page.locator('[aria-controls=nvs-a12]').click()
 for width in [375,768,1366]:
  page.set_viewport_size({'width':width,'height':950});tiles=page.locator('#nvs-a12 .nvs-a-branch').first.locator('a');assert tiles.count()==2
  boxes=tiles.evaluate_all('(els)=>els.map(e=>{const r=e.getBoundingClientRect();return {y:r.y,w:r.width,h:r.height}})');assert abs(boxes[0]['y']-boxes[1]['y'])<1;assert abs(boxes[0]['w']-boxes[1]['w'])<1;assert abs(boxes[0]['h']-boxes[1]['h'])<1
  page.screenshot(path=str(OUT/f'a12-menu-{width}.png'),full_page=True)
 assert page.locator('#nvs-a12 .nvs-a-branch').nth(1).locator('a').count()==4
 page.locator('#nvs-a12 a[href*=homeroom-notebook]').click();page.wait_for_selector('#operation h2');assert 'Sổ chủ nhiệm điện tử' in page.locator('#heading').inner_text();assert page.locator('#operation input').count()==0
 checks.append('A12 entry menu: exactly two equal cards on one row at 375/768/1366; notebook navigation and four inclusion links preserved')
 for id,op in ops.items():
  if op['kind'] in ['legacy']:continue
  goto(id)
  if op['kind'] in ['blocked','external']:
   assert page.locator('#operation input,#operation select,#operation textarea').count()==0
   if id=='hsg-diary':assert page.locator('#operation button:disabled').count()==1;assert page.locator('#operation iframe').count()==0
   checks.append(id+' blocked safely; no sensitive data entry');continue
  page.wait_for_function("()=>!document.getElementById('formFields').disabled");assert page.locator('#reportForm input[type=file]').count()==0;assert page.locator('#reportForm button:disabled').count()==3;fill(id)
  if op.get('people'):
   page.locator('[data-load-people]').click();page.wait_for_function("()=>document.getElementById('peopleList').querySelectorAll('input').length===3");assert 'Họ tên từ nguồn thử' in page.locator('#identityName').inner_text();
   if op['people']=='colleagues':assert page.locator('[data-person=qa_staff]').is_disabled()
   page.locator('[data-person=qa_colleague]').check();assert '1 người' in page.locator('#peopleCount').inner_text();page.locator('#peopleSearch').fill('đồng nghiệp');assert page.locator('#peopleList input').count()==1;page.locator('#peopleSearch').fill('')
  page.locator('#preview').click();assert page.locator('#previewCard').is_visible();assert 'CHƯA GỬI' in page.locator('#previewPaper').inner_text();assert page.locator('#previewPaper').get_attribute('class')==('official-paper' if op['kind']=='report' else None)
  if op['kind']=='link':assert page.locator('#field-drive').get_attribute('required') is not None
  page.locator('#edit').click();assert not page.locator('#previewCard').is_visible();assert page.locator('#field-year').input_value();page.locator('#reportForm [data-nvs-nav=ai]').click();assert op['name'] in page.locator('#nvsAiIdentity').inner_text();page.keyboard.press('Escape');checks.append(id+' correct fields/input/preview/edit/shared assistant; save/sign/send disabled')
 # A13: exact four-by-four structure, merged links and old URL compatibility.
 page.goto(app+'NVS_BaoCao_A1.html?group=A13');page.wait_for_selector('[data-section=team]')
 for width in [375,768,1366]:
  page.set_viewport_size({'width':width,'height':950})
  for section in ['team','cluster']:
   cards=page.locator('#catalog [data-section='+section+'] [data-operation]');assert cards.count()==4
   boxes=cards.evaluate_all('(els)=>els.map(e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,overflow:e.scrollWidth>e.clientWidth}})')
   assert abs(boxes[0]['y']-boxes[1]['y'])<1 and abs(boxes[2]['y']-boxes[3]['y'])<1 and boxes[2]['y']>boxes[0]['y']
   assert max(x['w'] for x in boxes)-min(x['w'] for x in boxes)<1 and max(x['h'] for x in boxes)-min(x['h'] for x in boxes)<1
   assert not any(x['overflow'] for x in boxes)
  page.screenshot(path=str(OUT/f'a13-catalog-{width}.png'),full_page=True)
 page.goto(app+'NVS_BaoCao_A1.html?group=A14');page.wait_for_selector('[data-section=hsg]')
 for width in [375,768,1366]:
  page.set_viewport_size({'width':width,'height':950})
  for section in ['hsg','support','exam']:
   cards=page.locator('#catalog [data-section='+section+'] [data-operation]');assert cards.count()==4
   boxes=cards.evaluate_all('(els)=>els.map(e=>{const r=e.getBoundingClientRect();return {y:r.y,w:r.width,h:r.height}})');assert abs(boxes[0]['y']-boxes[1]['y'])<1;assert abs(boxes[2]['y']-boxes[3]['y'])<1;assert boxes[2]['y']>boxes[0]['y'];assert max(x['h'] for x in boxes)-min(x['h'] for x in boxes)<1
  page.screenshot(path=str(OUT/f'a14-catalog-{width}.png'),full_page=True)
 page.goto(app+'NghiepVu.html');page.locator('details.group').first.locator('summary .chev').click();page.locator('[aria-controls=nvs-a13]').click();page.locator('[aria-controls=nvs-a14]').click()
 for width in [375,768,1366]:
  page.set_viewport_size({'width':width,'height':950})
  for section in range(2):
   tiles=page.locator('#nvs-a13 .nvs-a-branch').nth(section).locator('a');assert tiles.count()==4
   boxes=tiles.evaluate_all('(els)=>els.map(e=>{const r=e.getBoundingClientRect();return {y:r.y,w:r.width,h:r.height}})');assert abs(boxes[0]['y']-boxes[1]['y'])<1;assert abs(boxes[2]['y']-boxes[3]['y'])<1;assert max(x['h'] for x in boxes)-min(x['h'] for x in boxes)<1
  for branch in range(3):
   cards=page.locator('#nvs-a14 .nvs-a-branch').nth(branch).locator('a');assert cards.count()==4
   boxes=cards.evaluate_all('(els)=>els.map(e=>{const r=e.getBoundingClientRect();return {y:r.y,h:r.height}})');assert abs(boxes[0]['y']-boxes[1]['y'])<1;assert abs(boxes[2]['y']-boxes[3]['y'])<1;assert max(x['h'] for x in boxes)-min(x['h'] for x in boxes)<1
  dtht=page.locator('#nvs-a14 .nvs-a-branch').last;assert dtht.locator('a').count()==1
  assert dtht.locator('a').evaluate('(e)=>Math.abs(e.getBoundingClientRect().width-e.parentElement.getBoundingClientRect().width)<1')
  page.screenshot(path=str(OUT/f'a13-a14-menu-{width}.png'),full_page=True)
 page.goto(app+'NVS_BaoCao_A1.html?group=A14');page.wait_for_selector('[data-section=dtht]');dtht=page.locator('[data-section=dtht] .a1-catalog-grid');assert dtht.locator('a').count()==1;assert dtht.locator('a').evaluate('(e)=>Math.abs(e.getBoundingClientRect().width-e.parentElement.getBoundingClientRect().width)<1')
 goto('cluster-report');page.wait_for_selector('#field-materialsDrive');fill('cluster-report');page.fill('#field-materialsDrive','https://example.org/file');page.locator('#preview').click();assert 'hợp lệ' in page.locator('#notice').inner_text();page.fill('#field-materialsDrive','https://drive.google.com/file/d/QA_MATERIAL/view');page.fill('#field-evidenceDrive','https://docs.google.com/document/d/QA_EVIDENCE/edit');page.locator('#preview').click();assert page.locator('#previewPaper a[href*=QA_MATERIAL]').count()==1;assert page.locator('#previewPaper a[href*=QA_EVIDENCE]').count()==1;assert 'Kiến nghị' in page.locator('#previewPaper').inner_text();page.locator('#edit').click();assert 'QA_MATERIAL' in page.locator('#field-materialsDrive').input_value()
 page.goto(app+'NVS_BaoCao_A1.html?group=A13&item=cluster-materials');page.wait_for_selector('#field-materialsDrive');assert page.locator('#heading').inner_text()=='Báo cáo, minh chứng và kiến nghị'
 checks.append('A13 both groups 2x2 equal cards at 375/768/1366; merged materials/evidence links validate and survive preview/edit; old materials URL opens merged report; DTHT single full-width tile')
 # Source Word not received/approved and diary URL absent: no invented download or deployment.
 goto('hsg-plan');page.wait_for_selector('[data-template-download]');assert page.locator('[data-template-download]').is_disabled();assert 'HVA-A14-HSG-01' not in page.locator('.a1-template').inner_text();assert 'code=HVA-A14-HSG-01' in page.locator('.a1-template a').get_attribute('href');checks.append('HSG lookup uses stable code without publishing draft metadata; Word download NOT TESTED')
 # URL validation and permission honesty.
 fill('hsg-plan');page.fill('#field-drive','https://drive.google.com.evil.example/file/d/QA');page.locator('#preview').click();assert 'hợp lệ' in page.locator('#notice').inner_text();page.fill('#field-drive','https://docs.google.com/document/d/QA_ONLY/edit');assert 'Chưa kiểm chứng quyền' in page.locator('#driveStatus').inner_text();page.locator('#preview').click();assert page.locator('#previewCard').is_visible();checks.append('Drive syntax rejects lookalike host; no claim of Drive access validation')
 goto('task');page.wait_for_function("()=>!document.getElementById('formFields').disabled");fill('task');page.fill('#field-year','khong phai nam hoc');page.locator('#preview').click();assert 'Năm học' in page.locator('#notice').inner_text();page.fill('#field-year','2026–2027');page.fill('#field-from','2026-11-03');page.locator('#preview').click();assert 'không được trước' in page.locator('#notice').inner_text();page.fill('#field-from','2026-11-01');page.fill('#field-content','<img src=x onerror=alert(1)>');page.locator('#preview').click();assert page.locator('#previewPaper img').count()==0;checks.append('date order and safe report preview')
 goto('cluster-members');page.wait_for_function("()=>!document.getElementById('formFields').disabled");fill('cluster-members');page.locator('#preview').click();assert 'chọn người tham gia' in page.locator('#notice').inner_text();fail[0]=True;page.locator('[data-load-people]').click();page.wait_for_function("()=>document.getElementById('notice').dataset.error==='true'");assert page.locator('#peopleList input').count()==0;fail[0]=False;page.locator('[data-load-people]').click();page.wait_for_selector('[data-person=qa_colleague]');page.locator('[data-person=qa_colleague]').check();page.locator('#preview').click();assert page.locator('#previewCard').is_visible();checks.append('participants validation, personnel error and retry without fake roster')
 # Do not assume missing personnel role/unit equals teacher or current group.
 assert 'Chưa xác định' in page.locator('#peopleList').inner_text() or 'Bộ phận thử' in page.locator('#peopleList').inner_text()
 page.evaluate("localStorage.setItem('user',JSON.stringify({username:'OTHER_QA'}))");page.locator('#edit').click();page.locator('#preview').click();assert page.locator('#formFields').evaluate('(e)=>e.disabled');assert 'thay đổi' in page.locator('#notice').inner_text();checks.append('account change blocks continuation')
 goto('task');page.wait_for_function("()=>!document.getElementById('formFields').disabled");page.evaluate("localStorage.setItem('hvaSessionExpiresAt',String(Date.now()-1000))");page.locator('#preview').click();assert page.locator('#formFields').evaluate('(e)=>e.disabled');assert page.locator('#loginLink').is_visible();checks.append('expired session locks preparation; no extra rights for non-teaching staff')
 for width in [375,768,1366]:
  page.set_viewport_size({'width':width,'height':950})
  for id in ['task','hsg-plan']:
   goto(id);page.wait_for_function("()=>!document.getElementById('formFields').disabled");fill(id);page.locator('#preview').click();assert page.locator('#previewCard').is_visible();assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.evaluate('window.scrollTo({top:0,behavior:"instant"})');page.wait_for_timeout(100);page.screenshot(path=str(OUT/f'{id}-{width}.png'),full_page=True)
  checks.append(str(width)+' report and compact-link responsive; A4 scrolls within its wrapper')
 assert not errors,errors;assert set(calls)<= {'getNVSMeetingPersonnel'},calls
 result={'checks':checks,'runtime_errors':errors,'intercepted_actions':sorted(set(calls)),'template_download':'NOT TESTED — Word/source/approval pending','diary':'NOT CONNECTED — official URL pending','integration':'NOT TESTED; all external services blocked','legacy_CN_DTHT_regression':'NOT TESTED live; source links and files preserved','owner_acceptance':'PENDING'};(OUT/'RESULTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2));b.close()
s.shutdown()
