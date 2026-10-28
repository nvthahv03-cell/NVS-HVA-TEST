# Điều hành — bản kiểm tra giao diện kế thừa Cuộc họp

Mở https://nvthahv03-cell.github.io/NVS-HVA-TEST/DieuHanh.html bằng tài khoản BGH hiện có. GV, NV và TTCM không được mở menu BGH theo chính sách UI hiện hành; chưa kiểm thử quyền máy chủ. Không yêu cầu cài phần mềm.

## 14 menu và nguồn

- Cuộc họp — giữ nguyên trang nguồn
- Thông báo – Phát hành — giữ nguyên trang nguồn
- Giao nhiệm vụ — chuẩn bị / xem trước; chưa phát hành
- Lịch công tác HVA — chuẩn bị / xem trước; chưa phát hành
- Bình chọn — giữ nguyên trang nguồn
- Khảo sát — chuẩn bị / xem trước; chưa phát hành
- Phân công chuyên môn — chuẩn bị / xem trước; chưa phát hành
- Phân công dạy thay — chuẩn bị / xem trước; chưa phát hành
- Phân công khác — chuẩn bị / xem trước; chưa phát hành
- Điều phối công việc — chuẩn bị / xem trước; chưa phát hành
- Quản trị nghiệp vụ điều hành — giữ nguyên trang nguồn
- Quản trị nghiệp vụ số — giữ nguyên trang nguồn
- Kiểm tra nội bộ — chuẩn bị / xem trước; chưa phát hành
- Bảo đảm chất lượng — chuẩn bị / xem trước; chưa phát hành

Chín menu có 26 lựa chọn nội dung. Bốn menu trước đây mở trang khung (Giao nhiệm vụ, Lịch công tác, Dạy thay, Khảo sát) nay mở luồng chuẩn bị ngay trong Điều hành; có liên kết mở trang nguồn cũ. Hai menu quản trị vẫn giữ nguyên tuyến NVS_QuanTri#modules/#records. Các tuyến MODULE_LINKS và NVS_SUBMENU_ROUTES không đổi.

## Cách thử

1. Chọn menu, chọn loại nội dung. Điền trường bắt buộc, kiểm tra họ tên người chuẩn bị không cho sửa.
2. Nếu có người liên quan: bấm Tải Nhân sự HVA, mở nhóm, tìm kiếm, chọn từng người / cả nhóm. Người xuất hiện ở nhiều nhóm chỉ tính một tài khoản. Nhân sự chỉ dùng bộ HVAPersonnel.normalize/buildGroups đang dùng trong Cuộc họp; không tạo danh sách mẫu trên app.
3. Bấm Kiểm tra và xem trước. Quay lại chỉnh sửa; thay đổi form sẽ ẩn bản xem trước cũ. Khảo sát lựa chọn yêu cầu ít nhất hai phương án khác nhau; bản chuẩn bị khảo sát hiện hỗ trợ một câu hỏi mỗi đợt.
4. Bấm Trợ lý NVS trong cửa sổ; kiểm tra đúng menu và loại nội dung. Escape đóng riêng Trợ lý, vẫn giữ cửa sổ Điều hành. Dịch vụ AI thật chưa kiểm thử tích hợp.
5. Thử lỗi thời gian, liên kết Drive, tải nhân sự không thành công và tải lại. Nút × ở đầu cửa sổ luôn dễ tiếp cận; Tab giữ tiêu điểm trong biểu mẫu. Không nhập dữ liệu thật nhạy cảm.

## Kế thừa và giới hạn

Kế thừa core nhân sự, định danh tài khoản, nhóm / tìm kiếm / lựa chọn loại trùng và quy trình kiểm tra → xem trước → chỉnh sửa của Cuộc họp. Không sao chép endpoint tạo cuộc họp, QR/điểm danh, mã MEETING hoặc objectType MEETING sang nghiệp vụ khác. Không ghi các khóa HVA_MEETING_DRAFT / TTDHS_CURRENT_DOC. Không tạo cơ chế ký mới.

Lưu nháp, ký/xác nhận, phát hành, tiếp nhận, phản hồi và lịch sử mới đều khóa Đang phát triển. Chưa có action, dữ liệu, người nhận và ACL được phê duyệt cho nghiệp vụ mới. Không thể coi fixture nhân sự hoặc việc mở trang cũ là PASS tích hợp.

Gia cố guard giao diện: kiểm tra phiên cho cả menu chưa có tuyến, từ chối expiry không hữu hạn và yêu cầu tải lại khi đổi tài khoản. Không mở rộng quyền TTCM; các vai trò quản trị sẵn có vẫn theo mã hiện hành. Đây không phải xác thực server. Không thay đổi Backend hoặc hệ thống chính thức.

Bảo toàn 19 tệp nguồn theo DIEUHANH_PRESERVED.json. Các luồng PASS thật chưa kiểm thử lại với Google; không gắn PASS hồi quy chỉ từ hash.

Thay đổi: DieuHanh.html và định tuyến ngữ cảnh trong NVS_A1.assistant.js; thêm NVS_DieuHanh.js/css/schemas.json, tests/a1-pages/dieuhanh.py và tài liệu. Core/UI Trợ lý hiện hành không viết lại.

Bằng chứng: DIEUHANH_TEST_RESULTS.json; DIEUHANH_CHECKLIST.csv (11 cột). Chromium chạy dưới /NVS-HVA-TEST/, mọi API ngoài được chặn/intercept. Điều hướng về index trong test guard được chặn tĩnh để không kích hoạt API nền của trang chủ; không coi đây là kiểm thử tích hợp đăng nhập. Pages được kiểm tra qua build GitHub, chưa mở trực tiếp được từ môi trường do proxy 403.

Hoàn nguyên: revert commit Điều hành trên TEST về 3778eb5. Chưa nghiệm thu.
