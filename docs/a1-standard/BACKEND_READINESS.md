# A.1 — điều kiện tích hợp thử nghiệm

Chưa có URL Backend TEST, mã phiên bản triển khai, Sheets TEST hoặc cấu hình quyền được cấp phép. reportService vẫn null. Không gọi API sản xuất. Các tên dưới đây mô tả chức năng cần có, không phải action đã tồn tại hoặc hợp đồng API đã được xác nhận.

| Chức năng cần có | Điều kiện / bằng chứng tích hợp cần kiểm tra |
|---|---|
| Xác thực phiên và nhân sự | Server xác minh phiên; không tin username/role/tổ do client tự khai; phiên hết hạn và giả danh bị từ chối |
| Lưu / đọc / sửa nháp | Chủ sở hữu hợp lệ; kiểm tra schema riêng từng nghiệp vụ, revision và quyền; không truy cập nháp người khác |
| Xác nhận / ký | Đối chiếu đúng cơ chế DTHT được duyệt; ràng buộc người ký và phiên bản nội dung; không ký chỉ bằng tên trên client |
| Gửi và phân phối | Server xác định BGH có hiệu lực và quản lý CC chính thức; thiếu cấu hình thì từ chối; một ID duy nhất; chống gửi lặp; chưa lưu và phân phối thì không trả thành công |
| Tiếp nhận / phân công | BGH trong phạm vi quyền; TTCM nhận CC không mặc nhiên được duyệt; cập nhật trạng thái có kiểm soát |
| Phản hồi / yêu cầu bổ sung | Chỉ người được giao quyền; người báo cáo chỉ sửa đúng hồ sơ và trạng thái được phép |
| Danh sách / chi tiết / lịch sử | Server lọc theo chủ sở hữu / BGH / CC thực tế; lịch sử lưu người, thời điểm, phiên bản và thao tác |
| Danh mục mẫu | Chỉ trả mẫu đã duyệt, còn hiệu lực, đúng phạm vi truy cập; không đổi quyền Drive |

Chuẩn bị kiểm thử: chốt mã triển khai và so sánh từng tệp với nguồn do quản trị xuất; lập tài khoản TEST GV, NV, TTCM, BGH, người ngoài quyền và dữ liệu nhân sự TEST. Kiểm tra GV→BGH+TTCM đúng tổ; NV→BGH+quản lý được cấu hình; TTCM gửi theo cấu hình; thiếu tổ/quản lý bị chặn; người ngoài quyền bị chặn. Kiểm tra thành công/lỗi từng thao tác, gửi lặp, xung đột revision, phiên hết hạn, phản hồi bổ sung và lịch sử cùng một ID. Không dùng fixture hoặc HTTP tĩnh để công nhận PASS tích hợp. Chỉ thực thi khi có môi trường và phạm vi cho phép; không triển khai Backend trong đợt này.

Hai tệp được gửi ngày 29/10 là nguồn Sổ HSG độc lập: server doGet phục vụ Index, giao diện gọi google.script.run.getInitial / saveEntry / deleteEntry. Không có URL /exec cố định; chưa chứng minh nguồn trùng phiên bản đang triển khai. Chúng không cung cấp dịch vụ báo cáo A.1, ký hoặc định tuyến BGH/CC; không tái sử dụng để lưu A.1. Không chạy setupOnce, không sửa hoặc công bố mã nguồn sổ trong gói/repository.

Mẫu HVA-A14-HSG-01: tiếp tục chờ Word được phê duyệt và nguồn Drive được xác minh. Sổ HSG12: chờ URL hiện hành, chỉ mở liên kết. Không dùng URL tự suy ra từ mã nguồn.
