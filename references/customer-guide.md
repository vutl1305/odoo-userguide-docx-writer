# Quy ước biên soạn và chỉnh sửa

## Nguồn và bằng chứng

- Đọc SRS, luồng nghiệp vụ, ảnh hoặc mẫu in được giao. Nếu cùng có Markdown và DOCX thì đọc cả hai, xác định phiên bản; không giả định một file tồn tại vì được nhắc tới.
- Tra tri thức dự án nếu có, đối chiếu mã nguồn và giao diện đang chạy khi cần. Lưu bằng chứng kỹ thuật ở ghi nhận nội bộ; tài liệu khách hàng không chứa tên model, phương thức, SQL hoặc đường dẫn mã nguồn.
- SRS xác định phạm vi; giao diện/mã nguồn xác nhận cách thao tác thực tế. Khi chúng mâu thuẫn, ghi điểm lệch để xử lý; không âm thầm bịa nút hoặc chọn một quy tắc rồi mô tả như đã thống nhất.
- Xác minh phiên bản, ngôn ngữ và mô-đun thực tế. Odoo có tùy biến không đồng nghĩa với Odoo chuẩn cùng tên ứng dụng.

## Khung mặc định khi chưa có khung được duyệt

Dùng làm điểm xuất phát, điều chỉnh theo nghiệp vụ trong nguồn:

1. Giới thiệu tài liệu và tổng quan hệ thống.
2. Hướng dẫn sử dụng giao diện và thao tác chung trên Odoo.
3. Hướng dẫn thực hiện nghiệp vụ.
4. Quy trình và nguyên tắc nghiệp vụ.
5. Hướng dẫn xử lý tình huống và hỗ trợ sử dụng.
6. Giải thích thuật ngữ.
7. Lịch sử cập nhật tài liệu.

Không tách từng nhóm nghiệp vụ thành một chương cấp cao chỉ vì SRS chia như vậy. Tổ chức chúng trong mục 3 theo công việc. Không tự thêm “Bắt đầu từ đâu”, “Bắt đầu nhanh”, “Hiểu cách hệ thống vận hành”, chương thực hành mẫu, danh mục tra cứu nghiệp vụ lặp lại hoặc chương giả định.

Phần giới thiệu tối thiểu nêu tài liệu hướng dẫn gì, dành cho ai, giới hạn nghiệp vụ, các ứng dụng liên quan và luồng xử lý tổng thể. Các mục phụ như điều kiện truy cập, cách tra cứu, quy ước ảnh chỉ thêm khi có ích và chưa bị Người dùng bỏ. Không khôi phục những mục này khi sửa tài liệu đã được rút gọn.

## Phạm vi thao tác chung của Odoo

Đối chiếu từng chức năng có thực tế trước khi viết chi tiết:

| Nhóm | Nội dung cần xem xét |
| --- | --- |
| Truy cập | Đăng nhập/đăng xuất; tùy chọn cá nhân, ngôn ngữ, múi giờ; ứng dụng và menu. |
| Hiển thị và tra cứu | Danh sách, Kanban, biểu mẫu; tìm kiếm, lọc, nhóm; lưu/sử dụng lại điều kiện tìm kiếm. |
| Nhập thông tin | Tạo, sửa, lưu, bỏ thay đổi; trường liên kết, ngày, số, dòng chi tiết, giá trị tự tính/chỉ đọc. |
| Phối hợp | Ghi chú, gửi trao đổi, tệp đính kèm, lịch sử; lập lịch/hoàn thành hoạt động, thông báo, chứng từ liên quan. |
| Báo cáo | Pivot, biểu đồ, chỉ số, điều kiện lọc, đơn vị tiền tệ, xuất dữ liệu khi có quyền/chức năng. |

Không giả định có nút “Sửa” hoặc “Lưu”: một số phiên bản cho sửa trực tiếp, tự lưu và có biểu tượng lưu thủ công. Dùng đúng nhãn đang thấy; nhãn tiếng Anh còn tồn tại được giữ và giải thích ngắn bằng tiếng Việt. Không khẳng định có bảng điều khiển, ghim báo cáo, tích hợp lịch hoặc nút duyệt chỉ vì Odoo có thể hỗ trợ.

## Cấu trúc một hướng dẫn nghiệp vụ

- Mục tiêu, vai trò và điều kiện thực tế cần để hoàn thành công việc.
- Cách mở màn hình, theo đúng menu đã kiểm tra.
- Bước đánh số, một hành động rõ ràng trong mỗi bước; sau mỗi bước có ảnh tương ứng. Ảnh có thể chỉ thao tác hoặc kết quả của bước, chú thích phải nói đúng trạng thái đó.
- Ngay tại phần tạo/sửa có bảng trường: **Tên trường | Ý nghĩa | Cách nhập/chọn | Bắt buộc/điều kiện | Mặc định/tự điền/chỉ đọc và quy tắc**. Chỉ xác nhận thuộc tính có bằng chứng. Giải thích mã, đơn vị, ngày và tiền tệ tại nơi dùng.
- Quy tắc ảnh hưởng tới lưu/gửi/duyệt, khóa sửa và thay đổi trạng thái được nêu tại bước liên quan. Quy tắc dùng chung cho nhiều công việc được giải thích ở mục 4 và dẫn chiếu, không chép lặp toàn bộ bảng trường.
- Kết quả nhìn thấy; liên kết tới đúng tình huống lỗi. Tình huống gồm biểu hiện → nguyên nhân đã biết → cách xử lý → kết quả/đầu mối hỗ trợ đã được cung cấp.

Không viết thao tác tự động thành việc Người dùng phải bấm. Không viết nút xác nhận nếu giao diện không hiện nó; với bước có điều kiện, mô tả ảnh kết quả và điều kiện bằng chữ.

## Chỉnh sửa bản khách hàng

| Yêu cầu | Cách thực hiện |
| --- | --- |
| Chỉ tạo khung | DOCX có đầu mục và phạm vi dự kiến; chưa viết đầy đủ thao tác. |
| Viết đến một mục | Hoàn thành đúng điểm dừng; giữ phần còn lại theo trạng thái đã được duyệt. |
| Ghép khung để chia việc | Giữ nội dung đã viết, bổ sung đủ đầu mục con và phạm vi từ khung đã duyệt; chưa tự viết chi tiết. |
| Người dùng vừa sửa DOCX | Chụp lại bản gốc và dấu vết phiên bản; sửa bản mới từ DOCX đó, không dùng bản Markdown cũ để tái tạo. |
| Chỉ sửa ảnh/font | Giữ nội dung và hình học còn lại khi có thể; không tự tái cấu trúc, thêm lời dẫn hoặc giả định. |
| Đã bỏ ghi chú/phụ lục | Giữ việc loại bỏ; lưu thiếu sót quan trọng trong ghi nhận nội bộ, không chèn lại lời nhắc mặc định. |

Phân biệt phiên bản tài liệu với phiên bản Odoo. Cập nhật lịch sử theo thay đổi thực tế. Không cố định tên khách hàng, mô-đun, đường dẫn hoặc số bước của một tài liệu cụ thể thành phạm vi mọi tài liệu.
