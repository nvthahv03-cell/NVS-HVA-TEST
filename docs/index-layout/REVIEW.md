# Phạm vi: chỉ sửa Index, chờ chủ dự án nghiệm thu

## Bản nền và thay đổi

TEST main xác minh là `7f30deb9745f1014a87f68a51c1a5018b7bbd09c`. Nhánh sửa `fix/index-layout`. Chỉ một tệp ứng dụng thay đổi: index.html. Không sửa A/B/C, Điều hành, Cuộc họp, đăng nhập, API, dữ liệu hoặc quyền. Không đổi main của kho chính thức / PR #1.

## Lỗi gốc có số đo

Ở 1366 px, thư viện cao 85 px so với 112 px của ba nút còn lại. Nút thư viện dùng các lớp legacy khác, nằm trong wrapper riêng, chịu reset all:unset và các selector ID/min-height/padding riêng. Quy tắc `.nvs-quick #nvsQuickRoleSlot>#nvsOpenLibrary` trong hva-edos-v1 ấn định 85 px; lớp v16 của ba nút áp dụng 112 px. Ảnh và matched CSS đã lưu.

Hai cổng cùng cao 120 px nhưng icon desktop lệch Y 12.281 px. Selector `.nvs-chooser .nvs-gate-icon` quy định 94 px thắng quy tắc `.nvs-gate-icon` 38 px, icon bị co thực tế còn 68 px. Nhãn BGH hai dòng còn giữ margin-top 5 px trên em; nhóm flex căn giữa theo tổng chiều cao nội dung nên hai icon không thẳng hàng. Trên 375 px lệch 9.391 px dù chiều cao hai khối đều 104 px. Thanh tiện ích fixed desktop còn che cổng trong viewport.

## Sửa tại cơ chế gốc

Giữ nguyên node nút thư viện và listener, chuẩn hóa class như các ô khác, thay wrapper bằng chính nút gốc để bốn nút là bốn phần tử ngang hàng. Hợp nhất các quy tắc riêng lẻ của bốn ô thành một block tại vị trí stylesheet thành phần cũ; loại khai báo cạnh tranh, không nối CSS ở cuối file. Vai trò ẩn/hiện vẫn giữ nguyên.

Hai cổng dùng chung chiều cao, vùng icon cố định và vùng nhãn hai dòng, em không còn margin riêng; giữ nguyên chữ và href. Giữ mô tả cổng ẩn như bản nền. Dùng một cơ chế đặt thanh tiện ích trong khung ở mọi chiều rộng, giữ nguyên nút và listener, ngăn che cổng. Không dựng lại Index.

Static check xác nhận mọi script nghiệp vụ khác nguyên byte; chỉ hai script bố cục đổi thao tác DOM: nvs-v14-role-slot-script và nvs-mobile-unified-v4-script. HTML ngoài style/script không đổi (trừ chú thích). preserved.json ghi hash các tệp được bảo vệ; hash không thay cho hồi quy tích hợp.

## Bằng chứng và giới hạn

BEFORE_AFTER.md: ảnh cặp cùng viewport/role. measurements.csv: chiều cao, độ lệch icon, overlay. before/after/metrics.json: DOM rect và CSS computed của từng nút/nhãn/icon. Các API thật bị chặn trong kiểm thử. interactions.json đối chiếu các nút trước/sau trên bốn vai trò ở 375/1366 px: kết quả thao tác Index giữ nguyên. Cổng Điều hành ở Index giữ hành vi điều hướng cũ; kiểm tra quyền ở trang đích không nằm trong phép thử điều hướng chặn tĩnh. Chưa kiểm thử Backend đăng nhập, thông báo, khảo sát, nhắc nhở hoặc nghiệp vụ PASS với dữ liệu thật.

Proxy chặn tên miền Pages và Google Fonts. Bộ font biểu tượng là bản Bootstrap Icons hiện hành; Inter dùng Arial dự phòng nhất quán trước/sau. Chủ dự án cần kiểm tra thêm với Inter thực trên Windows/trình duyệt đang dùng. Không tuyên bố Index đã nghiệm thu hoặc an toàn hệ thống.

## Mở bản thử và hoàn nguyên

https://nvthahv03-cell.github.io/NVS-HVA-TEST/ — đăng nhập như hiện hành; kiểm tra bốn ô đầu trang, hai cổng, các nút và đổi chiều rộng. Không nhập dữ liệu thử vào nghiệp vụ đang nối nguồn thật.

Hoàn nguyên: revert commit Index trên TEST về 7f30deb; không cần thay Sheets hoặc Backend.

Dừng tại Index. Chỉ tiếp tục chuẩn hóa A.1 sau khi chủ dự án xác nhận PASS Index.
