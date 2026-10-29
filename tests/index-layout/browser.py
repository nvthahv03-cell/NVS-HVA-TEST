"""Index layout evidence: actual source, unchanged synthetic local session, real icon font.
All production services blocked. Does not verify server login or Backend behavior.
"""
from pathlib import Path
import json,http.server,threading,functools,argparse,re,datetime
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2];parser=argparse.ArgumentParser();parser.add_argument('--phase',required=True);parser.add_argument('--widths',default='320,375,390,600,720,721,1024,1366');parser.add_argument('--roles',default='bgh,teacher,head,staff');args=parser.parse_args();ASSETS=ROOT/'tests/index-layout/assets';OUT=Path('/workspace/index-layout-review')/args.phase;OUT.mkdir(parents=True,exist_ok=True)
PREFIX='/NVS-HVA-TEST/'
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
 def translate_path(self,path):return super().translate_path(path.replace(PREFIX,'/',1))
s=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)));threading.Thread(target=s.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{s.server_port}';app=base+PREFIX
roles={'bgh':'Hiệu trưởng','teacher':'Giáo viên','head':'Tổ trưởng','staff':'Nhân viên'};results=[]
measure=r"""()=>{const props=['display','position','box-sizing','width','height','min-height','max-height','padding-top','padding-right','padding-bottom','padding-left','border-top-width','border-radius','gap','align-items','justify-content','font-family','font-size','line-height','flex-shrink','grid-template-columns'];const rect=n=>{if(!n)return null;const r=n.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}};function info(n){if(!n)return null;const c=getComputedStyle(n);return {id:n.id,text:n.innerText,rect:rect(n),css:Object.fromEntries(props.map(p=>[p,c.getPropertyValue(p)])),icon:rect(n.querySelector('.nvs-quick-icon,.nvs-gate-icon')),label:rect(n.querySelector('strong')),before:{content:getComputedStyle(n,'::before').content,display:getComputedStyle(n,'::before').display}}};return {quick:[...document.querySelectorAll('.nvs-quick button')].filter(n=>n.getClientRects().length).map(info),gates:[...document.querySelectorAll('.nvs-gate')].map(info),grid:info(document.querySelector('.nvs-quick')),nav:info(document.querySelector('.nvs-premium-nav')),overflow:document.documentElement.scrollWidth>innerWidth+1,adminDisabled:document.getElementById('nvsAdminGate').getAttribute('aria-disabled'),libraryParent:document.getElementById('nvsOpenLibrary').parentElement.id}}
"""
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
 for role in args.roles.split(','):
  for width in map(int,args.widths.split(',')):
   context=b.new_context(viewport={'width':width,'height':900},device_scale_factor=1);calls=[];errors=[]
   user={'username':'QA_LAYOUT','tenDangNhap':'QA_LAYOUT','hoTen':'Tài khoản đo bố cục','chucVu':roles[role],'viTriViecLam':roles[role],'toBoPhan':'Bộ phận kiểm thử'}
   context.add_init_script("const OriginalDate=Date;window.Date=class extends OriginalDate{constructor(...args){super(...(args.length?args:[1793235600000]));}static now(){return 1793235600000;}};localStorage.setItem('user',"+json.dumps(json.dumps(user,ensure_ascii=False))+ ");localStorage.setItem('hvaSessionToken','QA_ONLY_NOT_AUTHENTICATION');localStorage.setItem('hvaSessionExpiresAt',String(Date.now()+3600000));")
   def route(r):
    u=r.request.url
    if u.startswith(base):r.continue_();return
    if 'bootstrap-icons.min.css' in u:r.fulfill(content_type='text/css',body=(ASSETS/'bootstrap-icons.css').read_text());return
    if 'bootstrap-icons.woff2' in u:r.fulfill(content_type='font/woff2',body=(ASSETS/'bootstrap-icons.woff2').read_bytes());return
    if 'bootstrap-icons.woff' in u:r.fulfill(content_type='font/woff',body=(ASSETS/'bootstrap-icons.woff').read_bytes());return
    if 'script.google.com' in u:
     data={}
     try:data=json.loads(r.request.post_data or '{}')
     except Exception:pass
     calls.append({'method':r.request.method,'action':data.get('action') or dict(__import__('urllib.parse',fromlist=['parse_qsl']).parse_qsl(__import__('urllib.parse',fromlist=['urlsplit']).urlsplit(u).query)).get('action')})
    r.abort()
   context.route('**/*',route);page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.goto(app+'index.html',wait_until='domcontentloaded');page.wait_for_timeout(1100);page.evaluate('document.fonts.ready');page.wait_for_function("document.getElementById('nvsOpenLibrary').closest('.nvs-quick')!==null")
   data=page.evaluate(measure);data.update(role=role,width=width,height=900,phase=args.phase,errors=errors,blocked_api_attempts=calls,font_limit='Google Inter unavailable through proxy; same Arial fallback before/after; original Bootstrap Icons loaded')
   if width in [375,1366]:
    page.screenshot(path=str(OUT/f'{role}-{width}-page.png'),full_page=True);page.locator('.nvs-quick').screenshot(path=str(OUT/f'{role}-{width}-quick.png'));page.locator('.nvs-two-gates').screenshot(path=str(OUT/f'{role}-{width}-gates.png'))
   # Store actual active matching CSS rules for the two different button structures.
   if role=='bgh' and width in [375,1366]:
    matching=page.evaluate(r"""()=>{let output={};for(const id of ['nvsOpenLibrary','nvsAdminGate','nvsWorkGate']){const element=document.getElementById(id),rules=[];function walk(list,origin){for(const r of list){if(r.conditionText&&r.media&&!matchMedia(r.conditionText).matches)continue;if(r.cssRules)walk(r.cssRules,origin);else if(r.selectorText){try{if(element.matches(r.selectorText))rules.push({origin,selector:r.selectorText,css:r.style.cssText});}catch(_){}}}}for(const sheet of document.styleSheets){try{walk(sheet.cssRules,sheet.ownerNode.id||'inline@'+[...document.querySelectorAll('style,link[rel=stylesheet]')].indexOf(sheet.ownerNode));}catch(_){}}output[id]=rules;}return output}""")
    (OUT/f'matched-css-{width}.json').write_text(json.dumps(matching,ensure_ascii=False,indent=2))
   results.append(data);print(json.dumps({'role':role,'width':width,'quick':[(v['text'],v['rect']['height'],v['icon']['height'] if v['icon'] else None) for v in data['quick']],'gates':[(v['rect']['height'],v['icon']['y']-v['rect']['y'],v['label']['height']) for v in data['gates']],'errors':len(errors)},ensure_ascii=False),flush=True);context.close()
 b.close()
(OUT/'metrics.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');s.shutdown()
