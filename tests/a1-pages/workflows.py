"""Full NVS A1–A6 browser UI checks at TEST Pages prefix. External traffic always blocked.
These are technical checks, never evidence of Backend integration or owner acceptance.
"""
from pathlib import Path
import functools,http.server,threading,json,re,os
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2];schemas=json.loads((ROOT/'NVS_Workflows.schemas.json').read_text());PREFIX='/NVS-HVA-TEST/'
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
 def translate_path(self,path):return super().translate_path(path.replace(PREFIX,'/',1))
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}';app=base+PREFIX;checks=[];variants=0
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage']);c=b.new_context(viewport={'width':1200,'height':950});external=[];errors=[]
 def route(r):
  if r.request.url.startswith(base):r.continue_()
  else:external.append(r.request.url);r.abort()
 c.route('**/*',route)
 c.add_init_script("localStorage.setItem('user',JSON.stringify({username:'QA_ONLY',hoTen:'Người kiểm thử',toBoPhan:'Bộ phận kiểm thử',chucVu:'Giáo viên'}));localStorage.setItem('hvaSessionToken','QA_ONLY_NOT_AUTHENTICATION');localStorage.setItem('hvaSessionExpiresAt',String(Date.now()+3600000));")
 page=c.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('dialog',lambda d:d.accept())
 page.goto(app+'NghiepVu.html');links=page.locator('a[href^="./NVS_TacNghiep.html?item="]');assert links.count()==19;assert page.locator('a[href="./PhanCong_DeKiemTra.html"]').count()==1
 assert page.locator('b.item-num').filter(has_text=re.compile(r'^A\.[1-6]\.[1-4]$')).count()==24
 checks.append('24 catalog items; 19 new links; A21 connected link unchanged')
 for code,schema in schemas.items():
  page.goto(app+'NghiepVu.html');page.locator('details.group').nth(int(code.split('.')[1])-1).locator('summary .chev').click();page.locator(f'a[href="./NVS_TacNghiep.html?item={code}"]').click();page.wait_for_function("()=>!document.getElementById('fields').disabled")
  assert code in page.locator('#heading').inner_text();assert page.locator('#type option').count()==len(schema['variants']);assert page.locator('input[type=file]').count()==1 # only inherited assistant, not dossier upload
  assert page.locator('#routing textarea[readonly]').count()==3;assert page.locator('#send').is_disabled();assert page.locator('#sign').is_disabled()
  for variant in schema['variants']:
   variants+=1;page.select_option('#type',variant);page.fill('#title','Nội dung thử kỹ thuật, không gửi')
   for key,label,kind,required in schema['fields']:
    value={'number':'2','date':'2026-11-01','datetime-local':'2026-11-01T08:00','drive':'https://drive.google.com/file/d/QA_ONLY/view'}.get(kind,'Nội dung kiểm thử')
    if key=='to':value='2026-11-01T10:00'
    page.fill('#field-'+key,value)
   page.locator('#preview').click();assert page.locator('#previewSection').is_visible();assert variant in page.locator('#previewText').inner_text();page.locator('#confirmPreview').check();assert 'không phải chữ ký' in page.locator('#confirmation').inner_text();assert page.locator('#send').is_disabled();page.locator('#edit').click();assert page.locator('#title').input_value()=='Nội dung thử kỹ thuật, không gửi'
  page.locator('[data-nvs-nav=ai]').click();assert code in page.locator('#nvsAiIdentity').inner_text();page.locator('#nvsAiClose').click();checks.append(code+' all variants input/preview/edit/confirmation/assistant; send locked')
 # Validation and unsafe input remain local and text-only.
 page.goto(app+'NVS_TacNghiep.html?item=A.3.1');page.wait_for_function("()=>!document.getElementById('fields').disabled");page.fill('#title','<img src=x onerror=alert(1)>')
 for key,label,kind,required in schemas['A.3.1']['fields']:page.fill('#field-'+key,'https://evil.example/file' if kind=='drive' else 'QA')
 page.locator('#preview').click();assert 'hợp lệ' in page.locator('#notice').inner_text();page.fill('#field-lesson','https://docs.google.com/document/d/QA_ONLY/edit');page.locator('#preview').click();assert page.locator('#previewText img').count()==0;checks.append('Drive host validation; preview text escapes HTML')
 page.fill('#field-lesson','https://drive.google.com.evil.example/file/d/QA');page.locator('#preview').click();assert page.locator('#notice').get_attribute('data-error')=='true';checks.append('lookalike Drive host denied')
 # Required distribution scenarios: no inference or success for any local persona.
 for name,user in [('teacher',{'username':'QA_ONLY','chucVu':'Giáo viên','toBoPhan':'Tổ thử'}),('employee',{'username':'QA_ONLY','chucVu':'Nhân viên','toBoPhan':'Văn phòng'}),('head',{'username':'QA_ONLY','chucVu':'Tổ trưởng','toBoPhan':'Tổ thử'}),('missing_manager',{'username':'QA_ONLY'}),('unauthorized',None)]:
  page.goto(app+'NVS_TacNghiep.html?item=A.5.4');page.wait_for_function("()=>document.getElementById('type').options.length>0")
  page.evaluate('(u)=>{if(u)localStorage.setItem("user",JSON.stringify(u));else{localStorage.removeItem("user");localStorage.removeItem("hvaSessionToken")}}',user)
  page.fill('#title','Báo cáo thử');page.locator('#preview').click();assert page.locator('#send').is_disabled();assert 'Chờ Backend' in page.locator('#routing textarea').nth(1).input_value();checks.append(name+' blocked pending authoritative Backend routing')
 # Mid-page identity switch must close the local workflow.
 page.goto(app+'NVS_TacNghiep.html?item=A.5.4');page.wait_for_function("()=>!document.getElementById('fields').disabled");page.evaluate("localStorage.setItem('user',JSON.stringify({username:'OTHER_QA'}))");page.locator('#preview').click();page.wait_for_function("()=>document.getElementById('fields').disabled");assert 'thay đổi' in page.locator('#notice').inner_text();checks.append('account change disables form')
 for width in [375,663,1200]:
  page.set_viewport_size({'width':width,'height':950});page.goto(app+'NVS_TacNghiep.html?item=A.6.2');page.wait_for_function("()=>!document.getElementById('fields').disabled");assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.screenshot(path=f'/tmp/nvs-a1-a6-{width}.png');checks.append(str(width)+' responsive without horizontal overflow')
 assert not errors,errors;assert not [url for url in external if 'script.google.com' in url or 'docs.google.com' in url],external
 result={'checks':checks,'new_item_count':19,'new_variant_count':variants,'page_errors':errors,'blocked_external_static_assets':sorted(set(external)),'production_api_requests':0,'backend_integration':'NOT TESTED / NOT CONNECTED','owner_acceptance':'PENDING'};(ROOT/'docs/A1_A6_TEST_RESULTS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2));b.close()
server.shutdown()
