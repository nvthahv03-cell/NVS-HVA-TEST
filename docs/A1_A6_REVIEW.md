# Kiểm thử tổng thể A.1–A.6

Mở https://nvthahv03-cell.github.io/NVS-HVA-TEST/NghiepVu.html sau khi GitHub Pages build xong. Đăng nhập bằng cơ chế NVS hiện có, mở nhóm rồi chọn nghiệp vụ. Không cần cài phần mềm.

## Thao tác

1. Chọn biểu mẫu. Kiểm tra người lập, tổ/bộ phận, chức vụ từ phiên NVS hiện có; không cho tự sửa danh tính.
2. Điền các trường có dấu *, liên kết Google Drive/Docs ở mục yêu cầu. Không dùng dữ liệu thật nhạy cảm, tên học sinh hoặc đề chưa công bố để thử.
3. Bấm Kiểm tra và xem trước; kiểm tra nội dung rồi quay lại chỉnh sửa. Ở A.2–A.6 có ô đánh dấu đã đọc bản xem trước: đây KHÔNG phải chữ ký.
4. Bấm Trợ lý ở thanh điều hướng: ngữ cảnh gồm NVS, mã mục và biểu mẫu. Dịch vụ AI chỉ hoạt động nếu máy chủ chấp nhận phiên; chưa kiểm thử tích hợp trong phiên này.
5. Lưu/gửi/ký, tiếp nhận, phân công, phản hồi và lịch sử mới ghi Đang phát triển, không tạo báo cáo mẫu hoặc thành công giả. Nội dung chỉ tồn tại trong trang, rời trang sẽ mất.

## 24 mục

- A.1.1 — Thực hiện nhiệm vụ – Báo cáo khác
- A.1.2 — Công tác chủ nhiệm và giáo dục hòa nhập
- A.1.3 — Sinh hoạt chuyên môn, sinh hoạt cụm
- A.1.4 — Bồi dưỡng HSG, phụ đạo, ôn thi và dạy thêm, học thêm
- A.2.1 — Xem nhiệm vụ kiểm tra, đánh giá được phân công
- A.2.2 — Nộp ma trận, bản đặc tả và đề kiểm tra
- A.2.3 — Nộp đề kiểm tra bổ sung, đề kiểm tra lại
- A.2.4 — Báo cáo, đề nghị về kiểm tra, đánh giá
- A.3.1 — Nộp liên kết kế hoạch bài dạy
- A.3.2 — Báo cáo tiến độ thực hiện chương trình
- A.3.3 — Nộp minh chứng chuyên môn theo yêu cầu
- A.3.4 — Nộp hồ sơ dạy học khác theo yêu cầu
- A.4.1 — Nghiên cứu khoa học, kỹ thuật và sáng kiến
- A.4.2 — Giáo viên tham gia và hướng dẫn học sinh tham gia các cuộc thi
- A.4.3 — Chuyên đề, tham luận và sản phẩm chuyên môn khác
- A.4.4 — Học liệu số và tài nguyên dạy học
- A.5.1 — Xin phép nghỉ dạy, nghỉ làm việc, ra ngoài
- A.5.2 — Đề nghị đổi tiết, điều chỉnh lịch
- A.5.3 — Đề nghị công tác, công vụ
- A.5.4 — Đơn, đề nghị khác
- A.6.1 — Đăng ký, đề xuất sử dụng thiết bị, đồ dùng dạy học
- A.6.2 — Đăng ký, đề xuất sử dụng phòng bộ môn, phòng Tin học, phòng chức năng
- A.6.3 — Báo cáo sử dụng thiết bị và phòng học chức năng
- A.6.4 — Báo hỏng, đề nghị sửa chữa, bổ sung thiết bị

A.1 có 9 biểu mẫu mới đã kiểm tra từ bản trước; A.1.2 giữ nguyên báo cáo chủ nhiệm và khóa sáu nhóm nội dung chưa đủ điều kiện dữ liệu. A.1.4 giữ nguyên liên kết DTHT. A.2.1 giữ nguyên trang nhiệm vụ kiểm tra. A.2.2–A.6.4: 19 mục mới với 39 lựa chọn biểu mẫu. Tên mục lấy nguyên từ danh mục hiện hành; A.4.2 bao gồm cả giáo viên tham gia và hướng dẫn học sinh, không rút gọn thành một hoạt động.

## Tiếp nhận thống nhất

Dùng chung NVS_ReportRouting.js trên các trang biểu mẫu mới A.1–A.6. Đây chỉ là thông báo và trạng thái khóa; KHÔNG phân phối trên trình duyệt. Danh sách BGH, CC, quyền đọc và phân quyền phải được máy chủ quyết định. Chưa có Backend lưu/phân phối được cấp phép nên không thể kiểm chứng năm kịch bản phân phối đầu cuối. Không thay đổi luồng đã PASS để ghép cơ chế chưa kiểm chứng.

Backend cần được phê duyệt trước khi triển khai: xác thực phiên phía server; tra cứu người gửi từ nhân sự có hiệu lực; resolve BGH và quản lý trực tiếp bằng cấu hình chính thức, gồm ngoại lệ nhân viên/Tổ trưởng; từ chối thiếu quy tắc; bỏ qua người nhận/danh tính tự gửi từ client; một ID báo cáo và danh sách ACL/CC tham chiếu cùng ID; ghi thời gian server và lịch sử xử lý; chỉ thành công khi đã lưu và phân phối nguyên tử, chống gửi trùng khi retry; kiểm tra quyền từng lần đọc/xử lý; TTCM không tự có quyền duyệt; không gửi email. Chưa tự tạo action, Sheets hoặc chữ ký mới. Cần nối cơ chế ký DTHT đã được xác minh trước khi mở ký cho biểu mẫu mới.

## Giới hạn và bảo toàn

Không sửa index, helper nhân sự/Trợ lý, chủ nhiệm, DTHT, Phân công KTĐG hoặc Cuộc họp. Bảo toàn byte không phải bằng chứng kiểm thử hồi quy tích hợp. Chưa gọi API sản xuất. URL Pages bị proxy môi trường chặn 403 nên chỉ kiểm tra Chromium dưới đúng đường dẫn /NVS-HVA-TEST/; chưa xác minh bản triển khai trực tiếp.

Bằng chứng: 31 nhóm kiểm tra trình duyệt cho 19 mục / 39 lựa chọn biểu mẫu; 17 kiểm tra A.1; 8 nhóm kiểm tra Trợ lý; 4 ca vai trò giao diện. A1_A6_TEST_RESULTS.json và A1_A6_CHECKLIST.csv. Các kết quả mock không được coi là PASS tích hợp. Hoàn nguyên: revert commit giao diện này trên TEST; không tác động kho chính. Chưa nghiệm thu.
