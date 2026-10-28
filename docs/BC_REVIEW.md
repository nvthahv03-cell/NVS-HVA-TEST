# B và C — kiểm thử giao diện NVS

Mở https://nvthahv03-cell.github.io/NVS-HVA-TEST/NghiepVu.html, đăng nhập theo cơ chế hiện hành rồi chọn tab B hoặc C. Không cần cài phần mềm.

B có 8 mục, C có 4 mục, giữ đúng tên và cấu trúc danh mục. B.2.1 giữ nguyên liên kết Văn bản – Quy định đã kết nối. B mới mở trang tra cứu thống nhất; C giữ nguyên cửa sổ chi tiết cùng các nút thu gọn/phóng to/đóng. C cũng mở được qua NVS_TraCuu.html?item=C.1 đến C.4.

## Cách thử

1. Bấm từng mục. Kiểm tra tên, tài khoản và mô tả phạm vi truy cập.
2. Nhập từ khóa, chọn loại, kỳ, ngày và trạng thái. Thử ngày kết thúc trước ngày bắt đầu để xem cảnh báo.
3. Bấm Tra cứu: hệ thống phải nói chưa kết nối, không hiển thị dữ liệu giả hoặc kết luận không có hồ sơ. Xóa bộ lọc chỉ xóa điều kiện trên trang.
4. Bấm Trợ lý NVS ngay trong trang / cửa sổ: kiểm tra đúng mã mục và loại nội dung. Escape chỉ đóng Trợ lý, không đóng nhầm cửa sổ C. Dịch vụ AI thật chưa kiểm thử.
5. Thử thu gọn, phóng to, đóng và mở lại từng cửa sổ C. Bấm lịch công tác/cá nhân ở thanh dưới để đến B.1.2/C.1.
6. Liên kết nguồn giữ nguyên cơ chế hiện hành; không nhập/gửi dữ liệu thử lên nguồn thật. Không coi việc có liên kết là bằng chứng Backend nguồn đã hoạt động.

## Trạng thái thực chất

Chưa cấu hình nguồn đọc mới được xác minh quyền. Không gọi API đọc toàn trường để lọc trên client, không tải dữ liệu người khác, không tạo hồ sơ mẫu. Số lượng/cập nhật giữ dấu —. Mở chi tiết, lịch sử, bổ sung và xuất mới đều khóa. Danh tính local chỉ để hiển thị; không coi là xác thực server. Nguồn thật và ACL/CC cần Backend được cấp phép trước khi mở truy vấn.

C.3 không tự ghi nhận kỷ luật/khen thưởng; C.4 không tự chấm điểm hoặc dùng AI đánh giá nhân sự. Không tự kết nối thời khóa biểu từ kho khác. Không thay đổi quyền, email hoặc dữ liệu thật.

Tệp thay đổi: NghiepVu.html, NVS_A1.assistant.js. Tệp mới: NVS_TraCuu.html, NVS_BC.js/css/schemas.json, kiểm thử và tài liệu BC. Trợ lý dùng lại nguyên view/helper hiện hành, chỉ bổ sung định tuyến ngữ cảnh B/C.

Nguồn PASS giữ nguyên byte theo BC_PRESERVED.json. Bảo toàn tệp không tương đương kiểm thử hồi quy tích hợp. Kết quả kỹ thuật: BC_TEST_RESULTS.json; checklist 11 cột: BC_CHECKLIST.csv. Chưa PASS tích hợp hoặc nghiệm thu.

GitHub Pages được kiểm tra qua trạng thái build của GitHub; proxy môi trường vẫn chặn mở trực tiếp tên miền website. Chromium kiểm thử dưới đúng /NVS-HVA-TEST/, mọi dịch vụ ngoài bị chặn.

Hoàn nguyên: revert commit B/C trên TEST về c9e3124; không đụng kho chính hoặc Backend.
