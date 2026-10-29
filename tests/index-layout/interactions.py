"""Compare baseline/current Index controls only. No Backend or destination-page integration."""
from pathlib import Path
import json,http.server,threading,functools,urllib.parse,subprocess
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2];ASSETS=ROOT/'tests/index-layout/assets';OUT=Path('/workspace/index-layout-review');BASELINE=OUT/'baseline-index.html';PREFIX='/NVS-HVA-TEST/';phase=['before']
if not BASELINE.exists():
 OUT.mkdir(parents=True,exist_ok=True);BASELINE.write_bytes(subprocess.check_output(['git','show','7f30deb:index.html'],cwd=ROOT))
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
 def translate_path(self,path):
  if urllib.parse.urlsplit(path).path==PREFIX+'index.html' and phase[0]=='before':return str(BASELINE)
  return super().translate_path(path.replace(PREFIX,'/',1))
s=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)));threading.Thread(target=s.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{s.server_port}';app=base+PREFIX;results=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 for current in ['before','after']:
  phase[0]=current
  for role,job in [('bgh','Hiệu trưởng'),('teacher','Giáo viên'),('head','Tổ trưởng'),('staff','Nhân viên')]:
   for width in [375,1366]:
    c=b.new_context(viewport={'width':width,'height':900});c.add_init_script("localStorage.setItem('user',JSON.stringify({username:'QA_LAYOUT',hoTen:'Tài khoản đo bố cục',chucVu:"+json.dumps(job)+",viTriViecLam:"+json.dumps(job)+",toBoPhan:'Bộ phận kiểm thử'}));localStorage.setItem('hvaSessionToken','QA_ONLY_NOT_AUTHENTICATION');localStorage.setItem('hvaSessionExpiresAt',String(Date.now()+3600000));")
    def route(r):
     url=r.request.url
     if url.startswith(base):
      if r.request.is_navigation_request() and urllib.parse.urlsplit(url).path!=PREFIX+'index.html':r.fulfill(content_type='text/html',body='<title>Navigation target only; no source data loaded</title>');return
      r.continue_();return
     if 'bootstrap-icons.min.css' in url:r.fulfill(content_type='text/css',body=(ASSETS/'bootstrap-icons.css').read_text());return
     if 'bootstrap-icons.woff2' in url:r.fulfill(content_type='font/woff2',body=(ASSETS/'bootstrap-icons.woff2').read_bytes());return
     r.abort()
    c.route('**/*',route);page=c.new_page();dialogs=[];page.on('dialog',lambda d:(dialogs.append(d.message),d.accept()))
    checks={};selectors=['#nvsOpenRemind' if role=='bgh' else '#nvsQuickWork','[data-nvs-quick=notice]','[data-nvs-quick=survey]','#nvsOpenLibrary','#nvsAdminGate','#nvsWorkGate','#edosAssistantAsk']
    for selector in selectors:
     page.goto(app+'index.html',wait_until='domcontentloaded');page.wait_for_function("()=>{const m=document.getElementById('dthtAuthModal');return !m||getComputedStyle(m).display==='none';}");page.locator('#nvsOpenLibrary').wait_for();dialogs.clear();page.locator(selector).click();page.wait_for_timeout(150)
     if page.url.startswith(app+'index.html'):
      observation=page.evaluate("""()=>({visible:[...document.querySelectorAll('[aria-modal=true],#nvsQuickDetail')].filter(n=>n.getClientRects().length&&getComputedStyle(n).display!=='none'&&n.getAttribute('aria-hidden')!=='true').map(n=>n.id),adminDisabled:document.getElementById('nvsAdminGate')?.getAttribute('aria-disabled'),expanded:[...document.querySelectorAll('.nvs-quick button[aria-expanded=true]')].map(n=>n.id||n.dataset.nvsQuick)})""")
     else:observation={}
     checks[selector]={'path':urllib.parse.urlsplit(page.url).path,'dialogs':dialogs.copy(),**observation}
    # Search and role swap must preserve the same decision at runtime.
    page.goto(app+'index.html',wait_until='domcontentloaded');page.wait_for_function("()=>{const m=document.getElementById('dthtAuthModal');return !m||getComputedStyle(m).display==='none';}");page.locator('#nvsLiveSearch').fill('Cuộc họp');checks['search']={'visible':page.locator('#nvsSearchResults').is_visible(),'text':page.locator('#nvsSearchResults').inner_text()[:300]}
    results.append({'phase':current,'role':role,'width':width,'controls':checks});c.close()
 b.close()
(OUT/'interactions-observed.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
for before in [r for r in results if r['phase']=='before']:
 after=next(r for r in results if r['phase']=='after' and r['role']==before['role'] and r['width']==before['width']);assert before['controls']==after['controls'],(before,after)
 # These expected actions establish observable UI behavior, beyond a matching screenshot.
 assert after['controls']['#nvsOpenLibrary']['path']==PREFIX+'VanBan_QuyDinh.html'
 assert after['controls']['#nvsWorkGate']['path']==PREFIX+'NghiepVu.html'
 assert after['controls']['#edosAssistantAsk']['visible']
 if before['role']=='bgh':assert after['controls']['#nvsAdminGate']['path']==PREFIX+'DieuHanh.html'
 else:assert after['controls']['#nvsAdminGate']['path']==before['controls']['#nvsAdminGate']['path'] # destination enforces its existing guard; this test does not grant server access
(OUT/'interactions.json').write_text(json.dumps({'results':results,'comparison':'All observed Index control outcomes unchanged','integration':'NOT TESTED; API blocked and navigation targets intercepted'},ensure_ascii=False,indent=2)+'\n');print('Index UI interactions: baseline/current outcomes match for four roles at 375 and 1366; destination integration NOT tested.');s.shutdown()
