---
name: odoo-userguide-docx-writer
description: Use when creating or revising a Vietnamese customer-facing Odoo user guide in Word (.docx), including outline approval, task instructions from an SRS, annotated screenshots, or preserving a customer-edited DOCX.
---

# Odoo user guide DOCX writer

Soạn tài liệu để khách hàng không chuyên kỹ thuật thực hiện công việc trên Odoo. Đầu ra chính là **file Word có thể chỉnh sửa**, không yêu cầu khách hàng đọc Markdown. Các mặc định dưới đây ghi nhận phong cách khách hàng đã chọn; yêu cầu mới của Người dùng luôn ưu tiên.

## Chọn phạm vi trước khi viết

1. Xác định tài liệu nguồn, bản DOCX mới nhất, khung đã duyệt và phần được giao. Đọc các nguồn được cung cấp; báo nguồn thiếu trong ghi nhận nội bộ. Không mặc định phiên bản Odoo hay coi tùy biến là tính năng chuẩn.
2. **Chưa duyệt khung:** tạo DOCX khung có đủ đầu mục và phạm vi dự kiến, dừng ở khung để Người dùng đánh giá. **Đã duyệt hoặc được giao viết tiếp:** thực hiện ngay phần đã giao, không hỏi lại việc đã chốt. Không tự viết toàn bộ các chương còn lại.
3. **Sửa tài liệu:** lấy DOCX Người dùng vừa cập nhật làm bản gốc. Giữ nội dung, thứ tự và phần đã xóa; không dựng lại từ Markdown hoặc script cũ. Tạo bản mới, giữ bản gốc. Khi chỉ yêu cầu ghép khung, chép đủ cả tiêu đề con từ khung được duyệt.

Đọc [quy ước biên soạn](references/customer-guide.md) khi chọn khung hoặc viết nội dung. Khung hiện có được ưu tiên hơn khung mặc định. Nếu có `authoring-user-guide`, `reviewing-user-guide` hoặc `content-template-gateway`, dùng phần phù hợp; không để cấu trúc mặc định của chúng khôi phục nội dung khách hàng đã bỏ.

## Các mặc định cần giữ

- Tiếng Việt, xưng **“Người dùng”**, câu ngắn, tên chương nghiêm túc. Font tài liệu **Times New Roman**, gồm bảng, chú thích, đầu/chân trang và mục lục.
- Có giới thiệu tài liệu, tổng quan hệ thống và **hướng dẫn thao tác chung mặc định của Odoo**, ngoài phần nghiệp vụ riêng. Không chép cấu trúc SRS thành cấu trúc tài liệu.
- Mỗi mục tiêu nghiệp vụ có một hướng dẫn chính. **Mô tả trường và quy tắc ngay tại bước tạo/sửa**, không đẩy hết sang danh mục tra cứu riêng. Không thêm chương thực hành tình huống mẫu hoặc bảng tham chiếu lặp lại nếu không được yêu cầu.
- Không thêm phụ lục giả định/cần xác nhận vào bản khách hàng. Giữ các điểm chưa rõ trong ghi nhận nội bộ; không biến chúng thành hành vi đã xác nhận. Tránh lời nhắc dài về tài khoản admin, dữ liệu mẫu, môi trường thử hoặc cách đọc tài liệu nếu Người dùng đã bỏ.
- Mỗi **bước thao tác đã viết** có ảnh ngay sau, với mũi tên nhỏ chỉ đúng nút/trường hoặc điểm cần kiểm tra. Ảnh có **viền 1px**, chú thích và mô tả thay thế. Chưa có ảnh thật thì dùng `[ẢNH: màn hình, vị trí và thao tác cần minh họa]` trong bản nháp; không tuyên bố đủ ảnh.
- Tên doanh nghiệp, người phụ trách, sản phẩm và hồ sơ tự nhiên như dữ liệu vận hành; không đặt tên “Khách hàng minh họa”, “Cơ hội hướng dẫn”, “MH…”. Chưa có dữ liệu thật được phép dùng thì tạo dữ liệu hư cấu hợp lý.

## Chụp và định dạng

Đọc [ảnh và kỹ thuật Word](references/screenshots-and-docx.md) trước khi chụp ảnh hoặc sửa bố cục. Chỉ dùng giao diện thật; không dùng AI tạo/sửa ảnh giao diện. Dùng admin khi được cấp và cho phép, không suy diễn quyền admin sang vai trò khác. Tôn trọng yêu cầu không web search; truy cập Odoo cục bộ không phải tìm kiếm web.

Khi cần chụp, thực hiện theo [quy trình chụp chạy được](references/capture-workflow.md): kiểm tra môi trường → sao chép add-on mẫu → tạo DB/dữ liệu thử → khai báo từng bước/selector → đăng nhập và chờ UI → lưu ảnh sạch + ảnh đánh dấu + manifest → xem ảnh → chèn Word → dọn DB thử. Mẫu tự chứa nằm ở `assets/odoo_userguide_capture/`, dùng `HttpCase.browser_js` và `Page.captureScreenshot`; không phụ thuộc một skill chụp ảnh khác.

- `scripts/screenshot_annotations.js`: chỉ gắn mũi tên nhỏ và tính vùng chụp; add-on mẫu mới là phần điều khiển trình duyệt, chụp PNG và ghi manifest.
- `scripts/style_docx_images.py INPUT.docx OUTPUT.docx`: thêm viền Word 0,75pt, tương đương 1px ở 96dpi; giữ nội dung và dữ liệu ảnh.
- `scripts/check_docx.py FILE.docx --require-step-images`: kiểm tra cấu trúc, font, viền và ảnh theo bước. Bản khung dùng lệnh không có `--require-step-images`.

## Trước khi bàn giao

Đối chiếu phạm vi và bản gốc: không mất chỉnh sửa thủ công, không thêm lại phần đã xóa, không viết vượt phần được giao. Xem từng ảnh, kiểm tra mũi tên không che chữ và viền đủ mảnh. Kết xuất Word/PDF bằng công cụ sẵn có để kiểm tra bố cục và cập nhật mục lục; kiểm tra tự động không thay thế xem bản kết xuất. Ghi rõ kiểm tra nào chưa thực hiện trong ghi nhận nội bộ và nêu giới hạn ảnh hưởng trực tiếp tới bàn giao.

Trả liên kết **DOCX**, tóm tắt ngắn thay đổi và phần chưa viết. Không gửi Markdown thay cho Word, không công bố/commit/push tài liệu hoặc skill nếu chưa được giao.
