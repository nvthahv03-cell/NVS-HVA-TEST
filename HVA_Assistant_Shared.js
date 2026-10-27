/* Trợ lý nghiệp vụ dùng chung HVA – chỉ tư vấn, không ghi dữ liệu. */
(function(root){'use strict';
  const URL='https://script.google.com/macros/s/AKfycbzTRkdqyYYI8LQo9MkiTjEIXkAC7BWK1MroUXPuvKMl9Yu_o9gXFS8QCcyQmq78-ikvvg/exec';
  const contexts=['Nghiệp vụ chung','Cuộc họp','Thông báo','Báo cáo','Kho văn bản','Lịch công tác','Công việc'];
  function store(k){for(const s of [root.sessionStorage,root.localStorage]){try{const v=s.getItem(k);if(v)return v;}catch(_){}}return '';}
  function session(){
    for(const k of ['sessionToken','nvsSessionToken','NVS_SESSION_TOKEN','hvaSessionToken','token']){const v=store(k);if(v)return v;}
    for(const k of ['user','nguoiDung','nvsUser','NVS_USER','hvaUser']){try{const v=JSON.parse(store(k)||'null');if(v&&typeof v==='object'&&(v.sessionToken||v.token))return v.sessionToken||v.token;}catch(_){}}
    return '';
  }
  async function ask({question,context='Nghiệp vụ chung',sessionToken,signal}={}){
    const q=String(question||'').trim();
    if(!q)throw Error('Vui lòng nhập nội dung yêu cầu.');
    if(q.length>4000)throw Error('Yêu cầu không vượt quá 4.000 ký tự.');
    if(!contexts.includes(context))throw Error('Ngữ cảnh không hợp lệ.');
    const token=sessionToken||session();
    if(!token)throw Error('Không tìm thấy phiên đăng nhập có mã xác thực. Vui lòng đăng nhập lại từ trang chủ.');
    const response=await fetch(URL,{method:'POST',headers:{'Content-Type':'text/plain;charset=utf-8'},body:JSON.stringify({action:'askVirtualAssistant',question:q,context,sessionToken:token}),redirect:'follow',signal});
    if(!response.ok)throw Error('Máy chủ không phản hồi thành công (HTTP '+response.status+').');
    let data;try{data=await response.json();}catch(_){throw Error('Không đọc được phản hồi của máy chủ; kiểm tra quyền Web App và CORS.');}
    if(!data||data.success!==true||!data.answer)throw Error(data?.message||'Trợ lý chưa trả lời được.');
    return String(data.answer);
  }
  async function draftReport({prompt,reportType='Nhiệm vụ được giao',sessionToken,signal}={}){
    const q=String(prompt||'').trim();
    if(!q||q.length>4000)throw Error('Yêu cầu soạn báo cáo phải từ 1 đến 4.000 ký tự.');
    const token=sessionToken||session();
    if(!token)throw Error('Chưa có phiên đăng nhập hợp lệ. Vui lòng đăng nhập lại.');
    const response=await fetch(URL,{method:'POST',headers:{'Content-Type':'text/plain;charset=utf-8'},body:JSON.stringify({action:'generateReportAIDraft',prompt:q,reportType,sessionToken:token}),signal});
    if(!response.ok)throw Error('Máy chủ HTTP '+response.status);
    let data;try{data=await response.json();}catch(_){throw Error('Không đọc được phản hồi máy chủ.');}
    if(!data||data.success!==true||!data.draft)throw Error(data?.message||'Không nhận được dự thảo.');
    return String(data.draft);
  }
  root.HVA_Assistant_Shared=Object.freeze({ask,draftReport,session,contexts});
})(window);
