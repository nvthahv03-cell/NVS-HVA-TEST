/* Recipient distribution is a Backend responsibility. No recipient inference or send API. */
(()=>{'use strict';
const host=document.getElementById('routing');if(!host)return;
const wrap=document.createElement('label');wrap.textContent='Chuyển nhóm nghiệp vụ';const select=document.createElement('select');select.setAttribute('aria-label','Chuyển nhóm nghiệp vụ');select.append(new Option('— Chọn nhóm —',''));
for(const [code,label] of [['A.1','Báo cáo chuyên môn'],['A.2','Kiểm tra – Đánh giá'],['A.3','Hồ sơ dạy học'],['A.4','Sản phẩm chuyên môn'],['A.5','Đơn – Đề nghị'],['A.6','Thiết bị – Đồ dùng dạy học']])select.append(new Option(code+' — '+label,code==='A.1'?'./NVS_BaoCao_A1.html?group=A11':'./NVS_TacNghiep.html?item='+code+(code==='A.2'?'.2':'.1')));
select.onchange=()=>{if(select.value)location.assign(select.value);};wrap.append(select);document.getElementById('heading')?.parentElement.after(wrap);
const heading=document.createElement('h2');heading.textContent='Tiếp nhận bắt buộc: BGH và cấp quản lý trực tiếp';host.append(heading);
for(const [label,value] of [
 ['Người nhận chính','Ban Giám hiệu Trường THPT Hòa Vang — chờ Backend xác minh danh sách đang có hiệu lực'],
 ['Người nhận CC','Chờ Backend xác định Tổ trưởng / quản lý trực tiếp theo phân công chính thức'],
 ['Trạng thái phân phối','Đang phát triển — chưa kết nối Backend xác thực và phân phối; chưa gửi']
]){const wrap=document.createElement('label'),field=document.createElement('textarea');wrap.textContent=label;field.value=value;field.readOnly=true;field.rows=2;wrap.append(field);host.append(wrap);}
const note=document.createElement('p');note.textContent='Không cho người gửi thay đổi người nhận bắt buộc. Giáo viên, nhân viên, Tổ trưởng và trường hợp thiếu dữ liệu đều phải được Backend kiểm tra. Không suy đoán cấp quản lý từ tên tổ hoặc chức vụ. Chưa có xác nhận lưu và phân phối từ Backend thì không ghi “Đã gửi”.';host.append(note);
})();
