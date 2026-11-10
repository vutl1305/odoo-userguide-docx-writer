# Ảnh chụp thật và kỹ thuật DOCX

## Môi trường và dữ liệu

Khi có mã nguồn Odoo, dùng bộ mẫu tự chứa của skill tại `assets/odoo_userguide_capture/`: add-on tạm ngoài kho mã, `HttpCase.browser_js` và Chrome headless. Cách chuẩn bị và lệnh chạy ở [quy trình chụp](capture-workflow.md). Nếu chỉ có hệ thống thử đang chạy, dùng công cụ trình duyệt đã được cấp. Có thể tham khảo skill `odoo-app-store-listing`, nhưng không cần skill đó để chạy mẫu này và không lấy cấu trúc trang App Store làm cấu trúc tài liệu Word.

- Dùng đúng môi trường/phiên bản/ngôn ngữ của dự án. Chụp bằng admin khi được cho phép; giữ thông tin tài khoản/quyền trong kiểm tra nội bộ nếu khách hàng không muốn đoạn lưu ý đó.
- Các thao tác tạo/sửa/xóa phục vụ chụp ảnh thực hiện trên dữ liệu/môi trường thử được cho phép. Nếu tự tạo DB tạm, đặt tên riêng, cấu hình `db_name` **và `dbfilter`** khớp nhau, thư mục dữ liệu riêng, không bật cron hay gửi thư ra ngoài.
- Tạo tên hư cấu có vẻ tự nhiên, như “Công ty TNHH Dinh dưỡng An Phú”, “Nguyễn Minh Anh”, “An Phú – H-Meal tháng 11”. Không gắn chữ “minh họa”, “hướng dẫn”, “test” hoặc tiền tố “MH” vào tên hiển thị. Không cần tên thật/PII của khách hàng để đạt điều này.
- Tạo hồ sơ qua hệ thống/ORM trong môi trường thử; không sửa chữ, giá trị hoặc trạng thái trên ảnh để giả làm giao diện đã chạy.
- Không in bí mật cấu hình. Không dùng dữ liệu môi trường này để suy đoán quyền của vai trò khác. Không gửi email/chat ra ngoài chỉ để có ảnh.
- Dọn đúng DB tạm do tác vụ tạo sau khi xong; kiểm tra tên chính xác, tránh DB nguồn, không dùng mẫu tên chung để xóa hàng loạt.

## Ảnh của bước thao tác và phần Kết quả

Lập manifest tối thiểu: mã bước hoặc kết quả, mục, câu hướng dẫn/kết quả, ảnh, trạng thái trước/sau thao tác và lựa chọn ảnh sạch/ảnh đánh dấu; chỉ cần đích mũi tên khi chọn ảnh đánh dấu. Chụp đúng trạng thái trước khi bấm nút hoặc sau khi có kết quả, theo chú thích. Một ảnh tổng quan cho nhiều bước không đáp ứng mặc định “mỗi bước một ảnh”.

### Chọn ảnh sạch hay ảnh đánh dấu

| Mục đích ảnh | Cách trình bày |
| --- | --- |
| Chỉ nút nhỏ, biểu tượng, trường hoặc mục menu khó tìm | Có thể dùng mũi tên nhỏ/khung mảnh tại đúng đích. |
| Tổng quan ứng dụng, danh sách, biểu mẫu đã lưu, bảng/biểu đồ báo cáo | Ưu tiên ảnh sạch; chỉ đánh dấu khi có chi tiết cụ thể cần chỉ ra. |
| Phần “Kết quả” | Chụp sau thao tác, ưu tiên ảnh sạch thể hiện trạng thái/dữ liệu/đầu ra; đặt ngay sau đoạn kết quả. |

Ví dụ: tạo hồ sơ → ảnh biểu mẫu đã lưu và tên hồ sơ; ghi chú → ảnh nội dung đã xuất hiện trong lịch sử; lập hoạt động → ảnh công việc đã được thêm; xuất Excel → ảnh nội dung file đã xuất thật. Ảnh chỉ vào nút Lưu/Gửi/Xuất trước khi bấm không thay thế ảnh kết quả.

Ảnh sạch vẫn có **viền ngoài 1px khi chèn Word**. Viền này khác khoanh đỏ/mũi tên chỉ đích. Không đánh dấu chỉ để mọi ảnh trông giống nhau. Mẫu chụp có thể lưu cả hai bản để dùng lại, nhưng tài liệu không bắt buộc chọn bản có annotation.

Đọc và chạy [quy trình chụp ảnh](capture-workflow.md): có cấu hình DB tạm, add-on mẫu, đăng nhập admin, điều hướng, `Page.captureScreenshot`, ghi PNG sạch/đánh dấu và manifest. Không chỉ gọi helper rồi xóa overlay: như vậy chưa tạo ra ảnh. Bộ mẫu nằm ngay trong skill, không cần tìm template ở skill khác.

Hàm chỉ thêm lớp đánh dấu không tương tác; không chụp ảnh, đăng nhập hoặc bấm thay Người dùng. Nếu công cụ không hỗ trợ clip, chụp toàn trang rồi cắt vùng không cần bằng công cụ ảnh thông thường, giữ nguyên nội dung giao diện. Không dùng AI tạo/sửa ảnh giao diện hay xóa mũi tên cũ bằng cách tô trắng lên chữ nền; chụp lại ảnh sạch khi cần đổi chú thích.

Mặc định mũi tên: thân **2px**, dài khoảng **60px**, đầu **10 × 8px**, `markerUnits="userSpaceOnUse"`. Đơn vị này tránh đầu mũi tên bị phóng thành 40px khi SVG nhân theo độ dày thân. Khung chỉ đích 1,5px; đây là khung đánh dấu, khác viền ngoài của ảnh.

Giữ đủ nhãn nút/trường và ngữ cảnh để đối chiếu. Tránh chụp nhầm nút chuyển dạng xem khi muốn chụp bảng Pivot: selector `.o_pivot` có thể khớp nút; chọn phần tử bảng thực tế. Với menu, hộp thoại, trường dài hoặc vị trí sát mép, kiểm tra chữ và đầu mũi tên không bị cắt/che.

Hộp chọn tệp của hệ điều hành có thể không xuất hiện trong ảnh trình duyệt: khi dùng ảnh tệp đã tải lên, nói đúng đó là kết quả. Ảnh file Excel phải từ file đã xuất thật; nếu chỉ xem nội dung được chuyển đổi thì không giả mạo giao diện Excel/Calc. Không khẳng định gửi thư thành công khi chỉ chụp ô soạn thảo.

## Word

- Dùng công cụ Word/DOCX sẵn có; `python-docx` phù hợp khi đã cài. Không đổi mọi tài liệu sang một bộ script cũ làm mất sửa đổi thủ công.
- A4, lề và cỡ chữ nhất quán; Times New Roman cho nội dung, bảng, Heading, chú thích, mục lục, đầu/chân trang. Font giao diện bên trong ảnh giữ nguyên Odoo.
- Dùng Heading thật, giữ cấp tiêu đề và đánh số, mục lục tự động có số trang. Dùng cấp mục lục phù hợp để tìm đầu mục phân công. Cập nhật mục lục sau khi thay ảnh/font.
- Chèn ảnh trực tiếp để DOCX tự chứa; giữ tỷ lệ, không kéo giãn, không ép ảnh chữ nhỏ thành hình không đọc được. Gắn bước với ảnh và ảnh với chú thích để tránh tách rời qua trang. Thêm mô tả thay thế.
- Viền ngoài **1px = 0,75pt = 9525 EMU** ở 96dpi, màu xám mảnh. Công cụ `style_docx_images.py` đặt viền ở thuộc tính ảnh Word, không làm thay đổi pixel giao diện. Nếu đầu ra yêu cầu PNG có viền raster riêng thì thêm đúng 1 pixel ở mép ngoài, không đè lên ảnh, bằng công cụ ảnh được cho phép.
- Khi sửa DOCX dạng ZIP, giữ quan hệ ảnh và trường PAGE/NUMPAGES/TOC. Tránh gán lại text cho mọi run trong chân trang vì có thể xóa trường động. Không tạo trùng `docProps/core.xml` hoặc ID hình/bookmark khi ghép tài liệu.
- Kiểm tra lại bản PDF/Word đã kết xuất: chữ bị cắt, chú thích, thứ tự bước, trang trắng, đoạn rơi vài dòng, nhãn nhỏ và viền ảnh. Xem từng ảnh bằng ảnh gốc hoặc tấm tổng hợp đủ rõ; xem riêng ảnh có vấn đề.

## Kiểm tra có thể chạy lại

```bash
python3 scripts/style_docx_images.py source.docx revised.docx
python3 scripts/check_docx.py revised.docx --require-step-images
```

Các script Python dùng `lxml`; bộ kiểm thử dùng thêm `python-docx`. Tái sử dụng môi trường đã có các thư viện này, không cài lại vào môi trường Odoo một cách tùy tiện. Khi thay đổi công cụ, chạy `python3 -m unittest discover -s tests`.

Đây là kiểm tra cấu trúc, không chứng minh thao tác Odoo chính xác hay ảnh chỉ đúng nút. Bản khung không có bước chưa cần `--require-step-images`. Công cụ báo lỗi nếu font khác mặc định hoặc chưa có viền; sửa theo yêu cầu hiện tại, không dùng kết quả để ghi đè lựa chọn mới của Người dùng. Sau khi kết xuất bằng Word/LibreOffice, chạy lại nếu cần vì ứng dụng có thể chuẩn hóa XML.
