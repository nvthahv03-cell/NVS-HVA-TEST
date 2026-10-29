# A.1 — bản chạy thử để chủ dự án kiểm tra

Nguồn nền: TEST main `37248a6bc154762dde10a5425df7387661865722`. Nhánh `feature/a1-reports-standard`. Không sửa Index, A.2–A.6, B/C, Điều hành, Kho văn bản 04, Chủ nhiệm, DTHT hoặc sổ HSG độc lập. Chưa có Backend được cấp phép/kiểm chứng cho các chức năng mới.

## Mở và thao tác

https://nvthahv03-cell.github.io/NVS-HVA-TEST/NVS_BaoCao_A1.html?view=a1-20261029&group=A11

1. Đăng nhập theo cơ chế NVS hiện hành. Chọn A.1.1–A.1.4, rồi chọn nghiệp vụ con.
2. Báo cáo: nhập đúng các nội dung riêng → xem bản báo cáo A4 → quay lại chỉnh sửa. Bố cục header, nhận diện người báo cáo, card, các bước và bản xem trước kế thừa chuẩn BC_ChuNhiem; không sao chép nghiệp vụ Chủ nhiệm.
3. Kế hoạch / tài liệu: chỉ nhập thông tin quản lý, người cùng phụ trách khi cần và liên kết Drive; không nhập lại toàn bộ Word, không tải hồ sơ lên NVS.
4. Bấm Đối chiếu / Tải nhân sự để dùng đúng HVA_Personnel. Không tự gán tổ từ nhóm công tác; vai trò thiếu không mặc định là giáo viên. Chọn GV cùng phụ trách cần căn cứ vai trò giảng dạy từ dữ liệu nguồn. Kiểm thử nhân sự dùng fixture, không phải PASS nguồn thật.
5. Trợ lý NVS dùng chung giữ nguyên UI/helper, tự nhận tên nghiệp vụ đang mở. Chỉ mở/đóng/ngữ cảnh được kiểm tra, chưa kiểm thử dịch vụ AI thật.
6. Lưu nháp / ký / gửi / tiếp nhận / lịch sử mới đều Đang phát triển, không giả thành công. Nội dung chỉ giữ trong trang; rời trang sẽ mất và có cảnh báo.
7. A.1.2 mở thẳng BC_ChuNhiem hiện hành; A.1.4 mở thẳng DTHT hiện hành. Không dùng dữ liệu thử để gửi lên các luồng đang vận hành.

## Cấu trúc và trạng thái

A.1.1 có ba báo cáo nhập/xem trước với trường riêng: nhiệm vụ, điều động, tập huấn/bồi dưỡng/hội nghị/hội thảo. Báo cáo khác chờ yêu cầu và biểu mẫu được giao.

A.1.2 có không gian Chủ nhiệm hiện hành và bốn nhóm hòa nhập khóa hoàn toàn dữ liệu học sinh.

A.1.3 có bốn nghiệp vụ tổ/nhóm, năm nghiệp vụ cụm: kế hoạch/tài liệu/biên bản nộp liên kết; báo cáo kết quả có trường riêng; thành phần tham gia dùng nhân sự HVA. Phạm vi quyền GV/chủ trì/TTCM/BGH chưa được nhà trường cung cấp nên chưa mở quyền nộp/đọc/xử lý thật.

A.1.4 hiển thị đúng bốn nhóm BD HSG / Phụ đạo / Ôn thi / DTHT. HSG có kế hoạch dạng nộp liên kết, sổ chờ URL, báo cáo kiểm tra/đánh giá có các trường được chỉ đạo, danh sách đội tuyển khóa và mô tả đúng luồng GV → TTCM → BGH. Phụ đạo và ôn thi có kế hoạch nộp liên kết riêng; danh sách, phân công, theo dõi và báo cáo chưa có mẫu/nguồn/quyền đã chốt giữ Đang phát triển, không tự đặt chỉ tiêu.

## Biểu mẫu và nguồn còn thiếu

Mã được chủ dự án nêu: HVA-A14-HSG-01; tên tệp dự kiến HVA-A14-HSG-01_Mau_Ke_hoach_BD_HSG.docx. Chưa nhận tệp thực, File ID/URL Drive và xác nhận phê duyệt, vì vậy không công bố thông tin mẫu dự thảo trong kết quả, không bật tải và không tạo Word thay thế. Mã chỉ dùng làm khóa tra cứu ổn định của nghiệp vụ.

Nguồn được chốt: 03_TAI_NGUYEN_VAN_BAN_HVA/03_01_BIEU_MAU. Đây là quy hoạch, không có thao tác tạo/đổi/xóa thư mục. 04_BAN_HANH_PHAT_HANH và Kho văn bản đang chạy giữ nguyên. Không tạo cơ chế lưu trữ tài liệu mới, không đổi quyền Drive.

Tra cứu trong A.1: mã / tên / viết tắt / từ khóa có hoặc không dấu; lọc A.1, loại tệp, loại hồ sơ. Hàm phòng vệ kiểm tra mã duy nhất, tên tệp bắt đầu bằng mã, trạng thái duyệt/hiệu lực, phiên bản, File ID/URL và quyền tải từ nguồn được kiểm chứng. **Các phép thử dùng fixture cô lập**, không phải bằng chứng ACL thật. Không có adapter server đã được cấp phép/kiểm chứng nên trạng thái hoạt động luôn chờ kết nối, không đọc toàn bộ danh mục rồi lọc quyền tại client. Không có mẫu giả trong dữ liệu vận hành.

Sổ HSG 12 chưa có URL /exec; không gọi, không sao chép hay sửa HTML/Code.gs/Sheets/nhân sự/dữ liệu sổ.

Còn cần: mẫu và trường báo cáo phụ đạo/tiến độ ôn thi/kiểm tra-thi thử; yêu cầu báo cáo khác; mẫu kế hoạch/biên bản sinh hoạt đã duyệt; phân công/quyền người chủ trì, TTCM, BGH; nguồn/lớp-học sinh và ACL nếu sau này mở dữ liệu; hợp đồng Backend xác thực phiên, gửi, ký và định tuyến BGH/CC. Không suy diễn hoặc tự kích hoạt.

## Kiểm thử và giới hạn

CHECKLIST.csv ghi từng nghiệp vụ và thao tác còn khóa; evidence/RESULTS.json ghi kết quả trình duyệt. Sáu báo cáo riêng, chín biểu mẫu liên kết và một luồng chọn thành phần đã kiểm tra nhập/xem trước/chỉnh sửa ở môi trường cục bộ. Các trạng thái khóa còn lại được kiểm tra không có ô nhập dữ liệu nhạy cảm. Đã sửa trường hợp form còn thiếu trường khiến trình duyệt chặn submit trước khi kiểm tra phiên: controller xác minh phiên trước rồi gọi reportValidity; ca hết hạn và đổi tài khoản đã kiểm chứng khóa chuẩn bị. Mọi yêu cầu ngoài bị chặn/intercept; chưa gọi API sản xuất.

Bằng chứng bảo toàn không đồng nghĩa PASS hồi quy: Chủ nhiệm/DTHT/Cuộc họp và các nghiệp vụ PASS chưa kiểm thử lại Backend thật. Proxy chặn tên miền Pages/Google Fonts; Chromium dùng cùng icon font thật và Arial dự phòng. Pages chỉ xác minh qua build GitHub, chưa trực tiếp mở được website từ môi trường. Chưa PASS tích hợp hoặc nghiệm thu.

Kiểm thử cũ tests/a1-pages/browser.py dựa trên cấu trúc A.1 trước chỉ đạo mới; bộ kiểm tra thay thế là tests/a1-standard. Không coi các assertion của đặc tả cũ là kết quả nghiệm thu cho đặc tả mới.

## Tệp và hoàn nguyên

Tệp ứng dụng sửa: NVS_BaoCao_A1.html, NVS_A1.js, NVS_A1.schemas.json; NghiepVu.html chỉ thay vùng A.1, phần A.2/B/C và JS chung giữ nguyên. Tài nguyên A.1 có mã nội dung trong URL để tránh tải nhầm JavaScript/CSS cũ từ cache; không có nhãn phiên bản trên giao diện. Tệp ứng dụng mới: NVS_A1_Report.css (riêng A.1, không sửa CSS đang được A.2/B/C dùng), NVS_A1.sources.json, NVS_Forms.js, NVS_BieuMau.html/js. Không sửa NVS_A1.assistant.js hoặc HVA_Assistant_Shared.

Hoàn nguyên: revert commit đợt A.1 trên TEST về 37248a6; không cần sửa Backend/Sheets/Drive. Chưa nghiệm thu. Sau khi chủ dự án nghiệm thu A.1 mới xem xét mở rộng kính lúp Index.
