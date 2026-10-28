"""Browser checks of reused assistant. No production API requests."""
import http.server,threading,functools,json
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[2]
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
 def translate_path(self,path):return super().translate_path(path.replace('/NVS-HVA-TEST/','/',1))
s=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root)));threading.Thread(target=s.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{s.server_port}/NVS-HVA-TEST/';checks=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);c=b.new_context();c.route('**/*',lambda route:route.continue_() if route.request.url.startswith(base) else route.abort());page=c.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 for group in ['A11','A12','A13','A14']:
  page.goto(base+'NVS_BaoCao_A1.html?group='+group);page.locator('[data-nvs-nav="ai"]').click();assert page.locator('#nvsAiOverlay').get_attribute('aria-hidden')=='false';assert 'Cổng Nghiệp vụ số' in page.locator('#nvsAiIdentity').inner_text();assert 'A.1.' in page.locator('#nvsAiIdentity').inner_text();page.locator('#nvsAiQuestion').fill('Hướng dẫn báo cáo');page.locator('#nvsAiAsk').click();assert 'hết hạn' in page.locator('#nvsAiStatus').inner_text();page.keyboard.press('Escape');assert page.locator('#nvsAiOverlay').get_attribute('aria-hidden')=='true';page.locator('[data-nvs-nav="ai"]').click();page.locator('#nvsAiClose').click();checks.append(group+' visible/open/context/no-session/escape/close')
 page.goto(base+'NghiepVu.html');page.locator('[data-nvs-nav="ai"]').click();assert page.locator('#nvsAiOverlay').get_attribute('aria-hidden')=='false';checks.append('catalog opens reused assistant')
 page.evaluate("localStorage.setItem('hvaSessionToken','QA_ONLY_NOT_AUTHENTICATION');localStorage.setItem('hvaSessionExpiresAt',String(Date.now()+3600000))")
 page.locator('#nvsAiQuestion').fill('Hướng dẫn báo cáo');page.locator('#nvsAiAsk').click();page.wait_for_function("document.getElementById('nvsAiStatus').textContent.startsWith('Lỗi:')");assert not page.locator('#nvsAiAsk').is_disabled();checks.append('blocked network error displayed and retry enabled')
 for width in [375,1200]:
  page.set_viewport_size({'width':width,'height':900});assert page.locator('#nvsAiClose').is_visible();page.screenshot(path=f'/tmp/nvs-assistant-{width}.png');checks.append(str(width)+' assistant visible')
 assert not errors,errors
 print(json.dumps({'checks':checks,'pageErrors':errors,'integration':'NOT TESTED — all production requests blocked'},ensure_ascii=False,indent=2));b.close()
s.shutdown()
