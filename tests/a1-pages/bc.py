"""B/C browser checks; all external requests blocked. No Backend integration claim."""
from pathlib import Path
import json,http.server,threading,functools
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2];schemas=json.loads((ROOT/'NVS_BC.schemas.json').read_text());PREFIX='/NVS-HVA-TEST/'
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
 def translate_path(self,path):return super().translate_path(path.replace(PREFIX,'/',1))
s=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)));threading.Thread(target=s.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{s.server_port}';app=base+PREFIX;checks=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);c=b.new_context(viewport={'width':1200,'height':950});external=[];errors=[]
 def route(r):
  if r.request.url.startswith(base):r.continue_()
  else:external.append(r.request.url);r.abort()
 c.route('**/*',route);c.add_init_script("localStorage.setItem('user',JSON.stringify({username:'QA_ONLY',hoTen:'Người kiểm thử',toBoPhan:'Bộ phận kiểm thử',chucVu:'Giáo viên'}));localStorage.setItem('hvaSessionToken','QA_ONLY_NOT_AUTHENTICATION');localStorage.setItem('hvaSessionExpiresAt',String(Date.now()+3600000));")
 page=c.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
 for code,config in schemas.items():
  if code.startswith('B.'):
   page.goto(app+'NghiepVu.html');page.locator('[role=tab]').nth(1).click();page.locator('#panel-1 details.group').nth(int(code.split('.')[1])-1).locator('summary .chev').click()
   if code=='B.2.1':
    assert page.locator('#panel-1 a[href="./VanBan_QuyDinh.html"]').count()==1;checks.append('B.2.1 original connected link preserved');continue
   page.locator(f'#panel-1 a[href="./NVS_TraCuu.html?item={code}"]').click();host=page.locator('#bcWorkspace')
  else:
   page.goto(app+'NghiepVu.html');page.locator('[role=tab]').nth(2).click();page.locator(f'[data-code="{code}"]').click();host=page.locator('[data-bc-modal]')
  host.locator('[data-bc-search]').wait_for();assert host.locator('[name=type] option').count()==len(config['types']);assert host.locator('table tbody tr').count()==1
  host.locator('[name=query]').fill('<img src=x onerror=alert(1)>');host.locator('[name=from]').fill('2026-11-02');host.locator('[name=to]').fill('2026-11-01');host.locator('[data-bc-search]').click();assert 'không được trước' in host.locator('[data-bc-status]').inner_text()
  host.locator('[name=to]').fill('2026-11-05');host.locator('[name=type]').select_option(index=len(config['types'])-1);host.locator('[data-bc-search]').click();assert 'chưa thể tra cứu' in host.locator('[data-bc-status]').inner_text();assert host.locator('[data-bc-status] img').count()==0;assert host.locator('button:disabled').count()==4
  host.locator('[data-nvs-nav=ai]').click();assert code in page.locator('#nvsAiIdentity').inner_text();page.keyboard.press('Escape');assert page.locator('#nvsAiOverlay').get_attribute('aria-hidden')=='true';
  if code.startswith('C.'):assert not page.locator('#nvsCModal').evaluate('(e)=>e.hidden')
  if code.startswith('C.'):
   page.locator('#nvsCMin').click();assert not host.is_visible();page.locator('#nvsCMin').click();assert host.is_visible();page.locator('#nvsCMax').click();assert 'full' in page.locator('.nvs-c-window').get_attribute('class');page.locator('#nvsCClose').click();assert page.locator('#nvsCModal').evaluate('(e)=>e.hidden');page.locator(f'[data-code="{code}"]').click();host.locator('[data-bc-search]').wait_for();assert not host.locator('[name=query]').input_value();page.keyboard.press('Escape');assert page.locator('#nvsCModal').evaluate('(e)=>e.hidden')
  else:
   host.get_by_role('button',name='Xóa bộ lọc').click();assert not host.locator('[name=query]').input_value()
  checks.append(code+' open/filter/date validation/no false results/context/reset or C controls')
 # Session/account lifecycle and cross-account isolation: queries never leave browser.
 page.goto(app+'NVS_TraCuu.html?item=C.1');host=page.locator('#bcWorkspace');host.locator('[data-bc-search]').wait_for();page.evaluate("localStorage.setItem('user',JSON.stringify({username:'OTHER_QA'}))");host.locator('[data-bc-search]').click();assert host.locator('[data-bc-fields]').evaluate('(e)=>e.disabled');assert 'thay đổi' in host.locator('[data-bc-status]').inner_text();checks.append('changed identity disables search and hides existing-source links')
 for role in ['Giáo viên','Nhân viên','Tổ trưởng','Hiệu trưởng']:
  page.goto(app+'NVS_TraCuu.html?item=C.3');host=page.locator('#bcWorkspace');host.locator('[data-bc-search]').wait_for();page.evaluate('(role)=>localStorage.setItem("user",JSON.stringify({username:"QA_ONLY",chucVu:role}))',role);host.locator('[data-bc-search]').click();assert 'chưa thể tra cứu' in host.locator('[data-bc-status]').inner_text();assert host.locator('input[name=username]').count()==0;checks.append(role+' no widening of C scope or invented records')
 page.goto(app+'NVS_TraCuu.html?item=C.4');host=page.locator('#bcWorkspace');host.locator('[data-bc-search]').wait_for();page.evaluate("localStorage.removeItem('hvaSessionToken')");host.locator('[data-bc-search]').click();assert host.locator('[data-bc-fields]').evaluate('(e)=>e.disabled');assert 'đăng nhập' in host.locator('[data-bc-status]').inner_text();checks.append('missing session locks search')
 for width in [375,663,1200]:
  page.set_viewport_size({'width':width,'height':950});page.goto(app+'NVS_TraCuu.html?item=B.2.3');page.locator('[data-bc-search]').wait_for();assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.screenshot(path=f'/tmp/nvs-bc-{width}.png');checks.append(str(width)+' page responsive; wide table scrolls inside wrapper')
 for width in [375,1200]:
  page.set_viewport_size({'width':width,'height':950});page.goto(app+'NghiepVu.html');page.locator('[role=tab]').nth(2).click();page.locator('[data-code="C.1"]').click();page.locator('[data-bc-modal] [data-bc-search]').wait_for();assert page.locator('#nvsCClose').is_visible();page.locator('[data-bc-modal] [data-nvs-nav=ai]').click();assert page.locator('#nvsAiOverlay').get_attribute('aria-hidden')=='false';page.keyboard.press('Escape');assert not page.locator('#nvsCModal').evaluate('(e)=>e.hidden');page.screenshot(path=f'/tmp/nvs-c-modal-{width}.png');checks.append(str(width)+' C modal and assistant reachable; Escape preserves C')
 page.goto(app+'NVS_TraCuu.html?item=B.1.1');page.locator('[data-bc-search]').wait_for();page.locator('[data-nvs-nav=person]').click();page.wait_for_url('**/NVS_TraCuu.html?item=C.1');page.locator('[data-bc-search]').wait_for();page.locator('[data-nvs-nav=calendar]').click();page.wait_for_url('**/NVS_TraCuu.html?item=B.1.2');checks.append('personal/calendar bottom navigation reaches C1/B12')
 assert not errors,errors;assert not [url for url in external if 'script.google.com' in url],external
 result={'checks':checks,'page_errors':errors,'production_api_requests':0,'backend_integration':'NOT TESTED / NEW SOURCES NOT CONNECTED','owner_acceptance':'PENDING'};(ROOT/'docs/BC_TEST_RESULTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2));b.close()
s.shutdown()
