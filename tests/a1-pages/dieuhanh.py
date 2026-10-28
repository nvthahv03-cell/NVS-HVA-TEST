"""Điều hành UI checks. Personnel responses intercepted; never tests production Backend."""
from pathlib import Path
import http.server,threading,functools,json,urllib.parse,re
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2];PREFIX='/NVS-HVA-TEST/';schema=json.loads((ROOT/'NVS_DieuHanh.schemas.json').read_text())
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
 def translate_path(self,path):return super().translate_path(path.replace(PREFIX,'/',1))
s=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)));threading.Thread(target=s.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{s.server_port}';app=base+PREFIX;checks=[];variants=0
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);c=b.new_context(viewport={'width':1200,'height':1000});calls=[];errors=[];fail=[False]
 c.add_init_script("localStorage.setItem('user',JSON.stringify({username:'QA_BGH',hoTen:'Người kiểm thử BGH',chucVu:'Hiệu trưởng'}));localStorage.setItem('hvaSessionToken','QA_ONLY_NOT_AUTHENTICATION');localStorage.setItem('hvaSessionExpiresAt',String(Date.now()+3600000));")
 def route(r):
  if r.request.url.startswith(app+'index.html'):r.fulfill(content_type='text/html',body='<title>Navigation target only</title>');return
  if r.request.url.startswith(base):r.continue_();return
  if r.request.url.startswith('https://script.google.com/'):
   q=urllib.parse.parse_qs(urllib.parse.urlsplit(r.request.url).query);action=q.get('action',[''])[0]
   if r.request.method=='POST':action=json.loads(r.request.post_data)['action'];calls.append(action);r.abort();return
   calls.append(action);assert action=='getNVSMeetingPersonnel',action
   if fail[0]:r.abort();return
   person={'username':'QA_MEMBER','hoTen':'Nhân sự kiểm thử','to':'Bộ phận kiểm thử'};payload={'success':True,'groups':[{'groupKey':'TEAM:QA','tenTo':'Tổ kiểm thử','kind':'TEAM','members':[person]},{'groupKey':'WORK:QA','tenTo':'Nhóm kiểm thử','kind':'WORKGROUP','members':[person]}]}
   r.fulfill(content_type='application/javascript',body=q['callback'][0]+'('+json.dumps(payload)+');');return
  r.abort()
 c.route('**/*',route);page=c.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('dialog',lambda d:d.accept())
 page.goto(app+'DieuHanh.html');assert page.locator('#sections .tile').count()==14;assert page.locator('.tile-status').count()==14;page.locator('#search').fill('Phân công chuyên môn');assert page.locator('#sections .tile').count()==1;page.locator('#search').fill('khongcotrongdanhmuc');assert page.locator('#empty').is_visible();page.locator('#search').fill('');assert page.locator('#sections .tile').count()==14;checks.append('14 existing names, sections, search and source-status labels')
 for name,config in schema.items():
  page.goto(app+'DieuHanh.html');page.locator('.tile').filter(has=page.locator('.tile-title',has_text=re.compile('^'+re.escape(name)+'$'))).click();host=page.locator('#dhWorkspace');host.locator('[data-dh-view]').wait_for()
  assert host.locator('button:disabled').count()==3
  if config['people']:
   host.locator('[data-dh-load]').click();page.wait_for_function("()=>document.querySelector('[data-dh-count]').textContent.includes('0 người')&&document.querySelector('[data-dh-people] details')");host.locator('[data-dh-people] details').first.locator('summary').click();host.locator('[data-dh-people] input[type=checkbox]').first.check();assert '1 người' in host.locator('[data-dh-count]').inner_text();assert host.locator('[data-dh-people] details').first.get_attribute('open') is not None
   # Same username in two groups must stay one recipient; changing keyword must preserve selection.
   host.locator('[data-dh-search]').fill('nhan su');assert host.locator('[data-dh-people] input:checked').count()==2;assert '1 người' in host.locator('[data-dh-count]').inner_text();host.locator('[data-dh-search]').fill('')
  for variant in config['types']:
   variants+=1;host.locator('[data-dh-field=type]').select_option(variant)
   for key,label,kind,required in config['fields']:
    value={'number':'2','date':'2026-11-01','datetime-local':'2026-11-01T08:00'}.get(kind,'Nội dung kiểm thử, không phát hành')
    if key=='options':value='Phương án một\nPhương án hai'
    if key=='to':value='2026-11-02T10:00' if kind=='datetime-local' else '2026-11-02'
    host.locator(f'[data-dh-field={key}]').fill(value)
   host.locator('[data-dh-view]').click();assert host.locator('[data-dh-preview]').is_visible();assert 'CHƯA PHÁT HÀNH' in host.locator('pre').inner_text();host.get_by_role('button',name='Quay lại chỉnh sửa').click();assert not host.locator('[data-dh-preview]').is_visible()
  host.locator('[data-nvs-nav=ai]').click();assert name in page.locator('#nvsAiIdentity').inner_text();page.keyboard.press('Escape');assert page.locator('#modal').get_attribute('aria-hidden')=='false';assert page.locator('#nvsAiOverlay').get_attribute('aria-hidden')=='true';page.locator('#modalClose').click();assert page.locator('#modal').get_attribute('aria-hidden')=='true';checks.append(name+' all variants, personnel where required, preview/edit, assistant and close')
 assert not page.evaluate("localStorage.getItem('TTDHS_CURRENT_DOC')||localStorage.getItem('HVA_MEETING_DRAFT')");checks.append('no writes to CuocHop publishing/draft keys; no meeting/create/send actions')
 # Input validation is checked before any publishing path could be enabled.
 page.goto(app+'DieuHanh.html');page.locator('.tile',has=page.locator('.tile-title',has_text=re.compile('^Khảo sát$'))).click();host=page.locator('#dhWorkspace');host.locator('[data-dh-view]').wait_for();host.locator('[data-dh-field=title]').fill('<img src=x onerror=alert(1)>');host.locator('[data-dh-field=question]').fill('Câu hỏi thử');host.locator('[data-dh-field=from]').fill('2026-11-01T08:00');host.locator('[data-dh-field=to]').fill('2026-11-02T08:00');host.locator('[data-dh-view]').click();assert 'chọn người liên quan' in host.locator('[data-dh-status]').inner_text();checks.append('personnel required before preview like CuocHop')
 host.locator('[data-dh-load]').click();page.wait_for_function("()=>document.querySelector('[data-dh-people] details')");host.locator('[data-dh-people] summary').first.click();host.locator('[data-dh-people] input[type=checkbox]').first.check();host.locator('[data-dh-field=to]').fill('2026-10-30T08:00');host.locator('[data-dh-view]').click();assert 'không được trước' in host.locator('[data-dh-status]').inner_text();checks.append('invalid interval rejected')
 host.locator('[data-dh-field=to]').fill('2026-11-02T08:00');host.locator('[data-dh-field=drive]').fill('https://drive.google.com.evil.example/file/d/QA');host.locator('[data-dh-view]').click();assert 'hợp lệ' in host.locator('[data-dh-status]').inner_text();checks.append('lookalike Drive domain denied')
 host.locator('[data-dh-field=drive]').fill('');host.locator('[data-dh-field=options]').fill('Một lựa chọn');host.locator('[data-dh-view]').click();assert 'hai phương án' in host.locator('[data-dh-status]').inner_text();host.locator('[data-dh-field=options]').fill('Một\nHai');host.locator('[data-dh-view]').click();assert host.locator('[data-dh-preview]').is_visible();assert host.locator('[data-dh-preview] img').count()==0;checks.append('survey choice validation and HTML-safe text preview')
 # Retry/error path through the real shared personnel core, intercepted remote transport.
 page.goto(app+'DieuHanh.html');page.locator('.tile',has=page.locator('.tile-title',has_text=re.compile('^Giao nhiệm vụ$'))).click();host=page.locator('#dhWorkspace');host.locator('[data-dh-view]').wait_for();fail[0]=True;host.locator('[data-dh-load]').click();page.wait_for_function("()=>document.querySelector('[data-dh-status]').dataset.error==='true'");assert host.locator('[data-dh-selected]').inner_text()=='';fail[0]=False;host.locator('[data-dh-load]').click();page.wait_for_function("()=>document.querySelector('[data-dh-status]').dataset.error==='false'");checks.append('personnel failure clears stale selection; retry works')
 for width in [375,663,1200]:
  page.set_viewport_size({'width':width,'height':950});page.goto(app+'DieuHanh.html');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.locator('.tile',has=page.locator('.tile-title',has_text=re.compile('^Kiểm tra nội bộ$'))).click();page.locator('[data-dh-view]').wait_for();assert page.locator('#dhCloseTop').is_visible();page.screenshot(path=f'/tmp/nvs-dh-{width}.png');checks.append(str(width)+' menu/workspace responsive')
 # Existing local role policy retained; no server privilege claim.
 for role,allowed in [('Giáo viên',False),('Nhân viên',False),('Tổ trưởng',False),('Hiệu trưởng',True),('Phó Hiệu trưởng',True)]:
  page.goto(app+'DieuHanh.html');page.evaluate('(role)=>localStorage.setItem("user",JSON.stringify({username:"QA_BGH",chucVu:role}))',role);page.evaluate('guardNVS()')
  if allowed:assert page.locator('#sections .tile').count()==14
  else:assert 'không có quyền' in page.locator('body').inner_text()
  checks.append(role+' local gate '+str(allowed))
 page.goto(app+'DieuHanh.html');page.evaluate("localStorage.setItem('hvaSessionExpiresAt','Infinity')");page.evaluate('guardNVS()');page.wait_for_url('**/index.html');checks.append('nonfinite session expiry denied')
 assert not errors,errors;assert set(calls)<= {'getNVSMeetingPersonnel'},calls
 result={'checks':checks,'form_count':len(schema),'variant_count':variants,'intercepted_actions':sorted(set(calls)),'page_errors':errors,'backend_integration':'NOT TESTED; NEW WRITES DISABLED','owner_acceptance':'PENDING'};(ROOT/'docs/DIEUHANH_TEST_RESULTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2));b.close()
s.shutdown()
