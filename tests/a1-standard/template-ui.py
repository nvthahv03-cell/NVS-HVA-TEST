"""Template lookup UI with closed source and isolated fixture rendering; not a Drive download test."""
from pathlib import Path
import http.server,threading,functools,json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2];PREFIX='/NVS-HVA-TEST/'
class H(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
 def translate_path(self,path):return super().translate_path(path.replace(PREFIX,'/',1))
s=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(H,directory=str(ROOT)));threading.Thread(target=s.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{s.server_port}';app=base+PREFIX
fixture={'code':'QA-A14-HSG-01','name':'DỮ LIỆU THỬ — Bồi dưỡng học sinh giỏi','description':'Không phải biểu mẫu nhà trường; chỉ kiểm thử giao diện','module':'A.1.4','documentType':'Kế hoạch','subject':'Vật lý','aliases':['BD HSG'],'keywords':['đội tuyển'],'fileType':'docx','fileId':'QA_ONLY_NOT_REAL','fileName':'QA-A14-HSG-01_Chi_dung_kiem_thu.docx','url':'https://drive.google.com/file/d/QA_ONLY_NOT_REAL/view','approvalStatus':'approved','active':True,'version':'QA','accessScope':'fixture-only','canDownload':True}
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);c=b.new_context();c.route('**/*',lambda r:r.continue_() if r.request.url.startswith(base) else r.abort());page=c.new_page();page.goto(app+'NVS_BieuMau.html?code=HVA-A14-HSG-01');assert page.locator('#templateQuery').input_value()=='HVA-A14-HSG-01';page.get_by_role('button',name='Tra cứu',exact=True).click();assert 'Chờ kết nối' in page.locator('#templateStatus').inner_text();assert page.locator('#templateResults a').count()==0;assert page.locator('input[type=file]').count()==0
 # Test-only injection at the dependency boundary; no operating records or fake success shipped to app.
 c.route('**/NVS_Forms.js*',lambda r:r.fulfill(content_type='application/javascript',body=(ROOT/'NVS_Forms.js').read_text()+'\nwindow.NVSForms=Object.freeze({...window.NVSForms,getState:()=>({status:"ready",items:window.NVSForms.filterVerifiedResponse('+json.dumps({'subject':'QA','items':[fixture,{**fixture,'code':'QA-DRAFT-01','approvalStatus':'pending'}]})+',{subject:"QA",verifiedByApprovedAdapter:true})})});'))
 page.goto(app+'NVS_BieuMau.html');page.fill('#templateQuery','boi duong');page.get_by_role('button',name='Tra cứu',exact=True).click();assert page.locator('#templateResults article').count()==1;assert page.locator('#templateResults a').get_attribute('href')==fixture['url'];assert 'QA-DRAFT' not in page.locator('#templateResults').inner_text();page.select_option('#templateFileType','pdf');page.get_by_role('button',name='Tra cứu',exact=True).click();assert page.locator('#templateResults article').count()==0
 print('PASS lookup pending-source UI and isolated fixture rendering/filtering; live templates, ACL and Word downloads NOT TESTED.');b.close()
s.shutdown()
