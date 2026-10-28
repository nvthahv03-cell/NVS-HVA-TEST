# Khôi phục Trợ lý A.1

Nguyên nhân: trang A.1 chỉ nạp API helper, không có cửa sổ và nút mở.

NVS_A1.assistant.js tái sử dụng markup/styles/handlers của Trợ lý index.html, kết nối qua HVA_Assistant_Shared.ask, giữ helper và index nguyên byte. Ngữ cảnh gửi gồm Cổng NVS, nhóm A.1 và biểu mẫu hiện tại; không tự gửi nội dung form. Chỉ yêu cầu tư vấn do người dùng bấm mới gọi API có sẵn; không đổi Backend.

Kiểm tra: node --check; Chromium 4 nhóm, menu danh mục, mở/đóng/Escape, ngữ cảnh, lỗi hết phiên, lỗi mạng và bật lại nút; 375/1200px; 17 kiểm tra hồi quy A.1 đạt. Mọi yêu cầu ngoài bị chặn trong kiểm thử. Không PASS tích hợp AI, không nghiệm thu.

Môi trường truy cập GitHub Pages bị proxy 403; chưa xác minh bản website từ môi trường này.

Hoàn nguyên: revert commit sửa trên kho TEST; không sửa kho chính hoặc Backend.
