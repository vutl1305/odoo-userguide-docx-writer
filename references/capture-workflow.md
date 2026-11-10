# Quy trình chụp ảnh Odoo có thể chạy

Dùng khi cần ảnh thật cho tài liệu. Đây là phần **điều khiển và chụp ảnh**, bổ sung cho helper vẽ mũi tên; không yêu cầu có skill chụp ảnh khác.

## 1. Chọn cách truy cập và kiểm tra đầu vào

- Có mã nguồn và quyền tạo DB thử: dùng **add-on HttpCase + Chrome headless** dưới đây. Đây là cách mặc định cho dự án Odoo chạy cục bộ.
- Chỉ có hệ thống thử đang chạy: dùng công cụ trình duyệt được cấp để đăng nhập, điều hướng và chụp. Vẫn thực hiện đủ chu trình sạch → đánh dấu → chụp → lưu manifest bên dưới; không tự thay DB, cài mô-đun hoặc tạo dữ liệu trên hệ thống vận hành.
- Chưa có trình duyệt/môi trường/đăng nhập phù hợp: tiếp tục phần tài liệu độc lập, giữ vị trí ảnh nháp và ghi thiếu sót nội bộ. Không thay bằng giao diện AI hoặc tuyên bố đã chụp.

Xác định phiên bản Odoo, Python tương thích, đường dẫn addons (chuẩn, Enterprise và tùy biến), cấu hình kết nối PostgreSQL, ngôn ngữ, tài khoản được phép dùng và cổng HTTP còn trống. Đọc mã/giao diện thực tế trước khi chọn selector. Không mặc định Python hệ thống chạy được Odoo của dự án.

Từ thư mục mã nguồn Odoo, preflight với Python của Odoo: `python -c "import odoo, psycopg2, websocket"`; kiểm tra Chrome bằng `google-chrome --version` hoặc binary Chrome/Chromium Odoo đang dùng. Thiếu `websocket-client` có thể khiến browser test bị bỏ qua: dùng môi trường sẵn có hoặc thư viện trong thư mục tạm/PYTHONPATH, không tự sửa môi trường vận hành. Không xem exit code 0 là bằng chứng đã có ảnh.

## 2. Chuẩn bị add-on và cấu hình riêng

Mẫu có sẵn tại `assets/odoo_userguide_capture/`. Các đường dẫn ở khối đầu phải thay bằng giá trị đã xác định, không chạy nguyên đường dẫn mẫu:

```bash
export UG_SKILL="/duong-dan/toi/odoo-userguide-docx-writer"
export UG_ODOO_ROOT="/duong-dan/toi/ma-nguon-odoo"
export UG_PY="/duong-dan/toi/python-tuong-thich-odoo"
export UG_SOURCE_CONFIG="/duong-dan/toi/cau-hinh-ket-noi.conf"
export UG_ADDONS_PATH="/duong-dan/addons-chuan,/duong-dan/enterprise,/duong-dan/customaddons"
export UG_WORK="$(mktemp -d /tmp/ug-capture.XXXXXX)"
export UG_CAPTURE_DB="ug_$(python3 -c 'import uuid; print(uuid.uuid4().hex[:12])')"
export UG_CAPTURE_OUTPUT="$UG_WORK/shots"
export UG_HTTP_PORT="8099"
mkdir -p "$UG_WORK/addons"
cp -R "$UG_SKILL/assets/odoo_userguide_capture" "$UG_WORK/addons/"
cp "$UG_SKILL/scripts/screenshot_annotations.js" "$UG_WORK/addons/odoo_userguide_capture/tests/annotations.js"
```

Chỉ lấy thông tin kết nối DB từ cấu hình hiện có; tạo cấu hình mới để tránh trỏ nhầm DB, filestore, cron hoặc máy chủ gửi thư:

```bash
python3 - <<'PY'
import configparser, os
from pathlib import Path
source = configparser.ConfigParser(interpolation=None)
assert source.read(os.environ['UG_SOURCE_CONFIG']), 'Không đọc được cấu hình nguồn'
work = Path(os.environ['UG_WORK'])
name = os.environ['UG_CAPTURE_DB']
assert name.startswith('ug_')
connection = {k: source['options'][k] for k in
              ('db_host', 'db_port', 'db_user', 'db_password', 'db_sslmode')
              if k in source['options']}
config = configparser.ConfigParser(interpolation=None)
config['options'] = dict(connection, db_name=name, dbfilter='^' + name + '$',
    addons_path=os.environ['UG_ADDONS_PATH'] + ',' + str(work/'addons'),
    data_dir=str(work/'data'), logfile=str(work/'odoo.log'),
    http_interface='127.0.0.1', http_port=os.environ['UG_HTTP_PORT'],
    max_cron_threads='0', workers='0', list_db='False')
path = work/'odoo.conf'
with path.open('w') as stream:
    config.write(stream)
path.chmod(0o600)
print('Cấu hình tạm đã tạo; không in thông tin kết nối.')
PY
```

`UG_CAPTURE_DB` phải là DB tạm mới của lượt chạy. Runner kiểm tra tên DB này trước khi tạo dữ liệu. Không đưa tên DB vận hành vào ví dụ rồi bỏ kiểm tra để chạy cho nhanh.

## 3. Viết dữ liệu và chuỗi màn hình cần chụp

Sửa **bản sao** trong `$UG_WORK/addons`, không sửa mã lõi Odoo:

1. `__manifest__.py`: thêm đúng mô-đun nghiệp vụ/tùy biến vào `depends` **trước khi khởi tạo DB**, để ảnh phản ánh hệ thống cần viết. Mặc định `base,web` chỉ phục vụ ba bước tùy chọn cá nhân trong ví dụ.
2. `tests/test_capture.py`, `setUpClass`: tạo khách hàng, người phụ trách, sản phẩm và chứng từ bằng ORM, dùng tên tự nhiên. Điền đủ trường bắt buộc và thiết lập đúng giai đoạn, quyền, tiền tệ. Không sửa DOM để giả dữ liệu đã có trong hệ thống.
3. `capture_steps(flow, url, frames, ...)`: mỗi `frame` là **một bước tài liệu**, có ID duy nhất, mục, câu hướng dẫn, `phase` (`before`/`after`), selector `target`, và `prepare` khi cần đưa UI tới trạng thái đó. `context` tùy chọn là selector vùng cần giữ đủ nhãn.

Ví dụ đã chạy trong mẫu: mở `/odoo` bằng `login='admin'`, chụp nút menu cá nhân → bấm mở menu và chụp “Tùy chọn của tôi” → bấm mở hộp thoại và chụp trường ngôn ngữ. Sửa URL/selector theo phiên bản, không coi ví dụ là đúng cho mọi phiên bản.

Với mỗi đoạn “Kết quả”, khai báo thêm frame riêng có `phase='after'`, ID rõ ràng (ví dụ `result-create-record`), điều kiện chờ dấu hiệu hoàn thành và câu mô tả kết quả. Khi đưa vào Word, chọn trường **`raw`** cho ảnh sạch. Chỉ chọn **`annotated`** nếu cần chỉ một chi tiết cụ thể. Runner vẫn có thể lưu cả hai bản; việc sinh bản đánh dấu không có nghĩa phải chèn bản đó vào tài liệu.

Khi hướng dẫn “chọn Lưu”, ảnh **before** phải thấy nút Lưu và dữ liệu hợp lệ trước khi bấm. Khi hướng dẫn “kiểm tra đã lưu”, thực hiện lưu thật trong `prepare`, chờ dấu hiệu lưu xong rồi chụp **after**. Không chụp cùng một trạng thái tổng quan rồi gán cho hàng loạt hành động khác nhau.

`prepare` chạy thao tác thật: bấm menu, điền trường, chọn giá trị. Dùng `await el(selector)`/`await until(predicate, mô_tả)` chờ phần tử và kết quả; `paint()` chờ hai khung hình cho trình duyệt vẽ. Không chỉ ngủ một khoảng cố định rồi chụp khi dữ liệu còn tải.

Với luồng tạo/sửa, truyền `finish_js` để lưu hoặc bỏ thay đổi **qua UI thật**. Kiểm tra kết quả lưu bằng UI hoặc ORM nếu tài liệu khẳng định đã lưu. Runner kiểm tra dấu hiệu dirty và new-record của web client trước khi báo thành công; đối chiếu cơ chế này khi đổi phiên bản. Kiểm tra DOM không thay thế bằng chứng lưu thực tế. Không gửi email/thông báo ra ngoài để tạo ảnh.

Với thao tác tải lại toàn trang như lưu tùy chọn/đổi ngôn ngữ/đăng xuất, JavaScript và overlay cũ có thể bị hủy. Tách ảnh trước/sau thành luồng hoặc lần mở trang riêng, chờ trang mới sẵn sàng và nạp lại helper. Nếu cần bấm thật qua reload, điều chỉnh bản sao runner theo sự kiện navigation của Chrome/Odoo, kiểm tra kết quả sau tải lại; không bắt lỗi `Execution context was destroyed` rồi tự coi là thành công. Mẫu ba bước hiện tại không bấm lưu tùy chọn và không yêu cầu vượt qua reload.

## 4. Chạy Odoo và chụp

Chạy từ thư mục mã nguồn Odoo. Ví dụ flag dưới đây đã thử trên Odoo 20; đối chiếu `odoo-bin --help` nếu dùng phiên bản khác:

```bash
cd "$UG_ODOO_ROOT"
"$UG_PY" odoo-bin -c "$UG_WORK/odoo.conf" \
  -i odoo_userguide_capture --without-demo=True --load-language=vi_VN \
  --stop-after-init --no-http
"$UG_PY" odoo-bin -c "$UG_WORK/odoo.conf" \
  --test-enable --test-tags /odoo_userguide_capture:TestGuideCapture \
  --screenshots="$UG_WORK/debug" --stop-after-init
```

Lệnh đầu tạo DB và cài dependencies đã khai báo. Lệnh chụp thứ hai **có HTTP**: `HttpCase.browser_js` cần máy chủ Odoo để đăng nhập và mở trang. Không mang `--no-http` sang lệnh thứ hai. Không cần biết/in mật khẩu admin: dùng cơ chế đăng nhập của HttpCase trên DB thử.

Runner sử dụng API Chrome của Odoo (`ChromeBrowser._wait_code_ok`, `_websocket_request`). Nếu API khác trong phiên bản mục tiêu, đọc `odoo/tests/common.py` và sửa bản sao runner; không sửa framework Odoo để ép mẫu chạy.

## 5. Ảnh được chụp cụ thể thế nào

Runner thực hiện cho từng bước:

1. Đăng nhập admin bằng `browser_js`, mở URL, đặt viewport **1440 × 900**, scale 1.
2. Chạy `prepare`, chờ target thật hiển thị, chờ trình duyệt vẽ.
3. Nạp `annotations.js`, xác định target và context, tính clip. Lớp mũi tên không tương tác, không thay giá trị/nút của Odoo.
4. Ẩn lớp đánh dấu, gọi **`Page.captureScreenshot`** với `format='png'`, `clip=shot['clip']`, giải mã base64 và ghi ảnh sạch.
5. Hiện lớp đánh dấu, chờ vẽ rồi gọi cùng API/cùng clip, ghi ảnh có mũi tên nhỏ. Đây là ảnh chụp mới từ trình duyệt, không phải ảnh UI do AI tạo hoặc tô sửa chữ nền.
6. Lưu metadata/tọa độ/URL và SHA256 của cả hai ảnh; xóa overlay trước bước tiếp theo.
7. Hoàn tất lưu/bỏ thay đổi theo luồng, kiểm tra lỗi trình duyệt rồi mới ghi manifest thành công. Nếu một frame lỗi, lưu ảnh toàn màn hình trong `debug/` và để phép thử lỗi.

Lời gọi chụp nằm sẵn trong `tests/test_capture.py`, không phải comment yêu cầu agent tự viết tiếp:

```python
encoded = browser._websocket_request('Page.captureScreenshot', params={
    'format': 'png', 'clip': shot['clip'], 'captureBeyondViewport': False,
})['data']
path.write_bytes(base64.b64decode(encoded))
```

Mũi tên dùng thân 2px, đầu 10 × 8px với `markerUnits="userSpaceOnUse"`. Chỉ đích đúng nút/trường, không chỉ vào khoảng trống. Không cắt mất nhãn hoặc mũi tên. Giữ một vùng hộp thoại/nhóm trường vừa đủ; không để phần lớn ảnh là nền trắng làm chữ nhỏ đi khi chèn Word.

## 6. Kiểm tra đầu ra và gắn ảnh vào Word

Mặc định ba bước tạo các file sau. Mỗi flow có thư mục riêng để không ghi đè ảnh của flow khác, ngay cả khi trùng mã bước; vẫn nên dùng mã bước duy nhất khi ghép cả tài liệu:

```text
shots/
  preferences/
    raw/s001.png ... s003.png
    annotated/s001.png ... s003.png
    metadata/s001.json ... s003.json
    debug/                       # Có ảnh lỗi khi một bước thất bại
  manifest-preferences.json
```

Kiểm tra ví dụ trước khi ghép Word:

```bash
python3 - <<'PY'
import json, os
from pathlib import Path
out = Path(os.environ['UG_CAPTURE_OUTPUT'])
rows = json.loads((out/'manifest-preferences.json').read_text())
assert len(rows) == 3
for row in rows:
    assert row['raw_sha256'] != row['annotated_sha256']
    for key in ('raw', 'annotated'):
        assert Path(row[key]).read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
print('Đủ 3 ảnh sạch, 3 ảnh đánh dấu và manifest.')
PY
```

Đổi số lượng/manifest khi thêm luồng. Khi sửa helper annotation, mở `tests/annotations.html` bằng Chrome headless/trình duyệt cục bộ và kiểm tra kết quả `PASS`, cùng các kiểm thử Python của skill. Rà soát đủ ảnh cho cả bước thao tác lẫn đoạn “Kết quả”. Xem từng ảnh và đối chiếu với nội dung tương ứng: đúng màn hình, dữ liệu, trạng thái, nhãn, đích mũi tên; không spinner/lỗi/che chữ. Ảnh sạch cho phép chụp lại chú thích mà không tô xóa UI. Không xóa DB khi còn cần sửa ảnh.

Sao chép ảnh và manifest vào thư mục tài liệu cần giữ lâu dài. Trong DOCX, lấy ảnh theo **ID bước hoặc ID kết quả**: chọn **`raw`** khi ảnh đã rõ hoặc đang minh họa kết quả; chỉ chọn **`annotated`** khi có vị trí khó nhận biết cần chỉ dẫn. Chèn ngay sau đúng bước hoặc đoạn “Kết quả”, thêm chú thích và alt text, giữ tỷ lệ. Không chọn “ảnh PNG mới nhất” hoặc chỉ dựa vào số thứ tự ảnh trong ZIP Word. Thêm viền ngoài 1px bằng `scripts/style_docx_images.py`, rồi chạy `scripts/check_docx.py --require-step-images` như hướng dẫn Word.

## 7. Dọn môi trường thử khi đã xong

Chờ Odoo và Chrome của lượt chụp thoát. Giữ ảnh/manifest đã dùng; không xóa đầu ra trước khi bảo đảm DOCX nhúng đủ ảnh. Chỉ xóa đúng DB tạm do lượt này tạo; ví dụ đọc lại cấu hình tạm, không gõ thông tin kết nối ra log:

```bash
"$UG_PY" - <<'PY'
import configparser, os
from pathlib import Path
import psycopg2
from psycopg2 import sql
c = configparser.ConfigParser(interpolation=None)
c.read(Path(os.environ['UG_WORK'])/'odoo.conf')
o = c['options']
name = os.environ['UG_CAPTURE_DB']
assert name.startswith('ug_') and o['db_name'] == name
params = {'dbname': 'postgres'}
for key in ('host', 'port', 'user', 'password', 'sslmode'):
    value = o.get('db_' + key)
    if value and value.lower() not in ('false', 'none'):
        params[key] = value
conn = psycopg2.connect(**params)
conn.autocommit = True
with conn.cursor() as cur:
    cur.execute('SELECT pid FROM pg_stat_activity WHERE datname=%s', (name,))
    assert not cur.fetchall(), 'Còn kết nối đến DB thử; dừng máy chủ trước'
    cur.execute(sql.SQL('DROP DATABASE {}').format(sql.Identifier(name)))
conn.close()
PY
```

## Lỗi thường gặp

| Biểu hiện | Cách kiểm tra/xử lý |
| --- | --- |
| Trang chọn DB thay vì màn hình Odoo | `db_name` và `dbfilter` phải cùng DB tạm; kiểm tra cổng và URL. |
| Test kết thúc mà không có ảnh | Kiểm tra Chrome, websocket-client, test tags, số frame và manifest; test bị skip không phải chụp thành công. |
| Không thấy nút hoặc timeout selector | Kiểm tra mô-đun, vai trò, ngôn ngữ, phiên bản, trạng thái hồ sơ và DOM thật; sửa selector, không bịa nút. |
| Nhãn đúng nhưng chụp nhầm biểu tượng | Dùng selector cụ thể cho bảng/biểu mẫu; tránh class chung đồng thời thuộc nút chuyển view. |
| Ảnh có spinner hoặc giá trị cũ | Chờ phản hồi/biến đổi UI bằng điều kiện, sau đó chờ paint trước khi chụp. |
| Bị báo form chưa lưu | Lưu hoặc bỏ thay đổi qua UI trong `finish_js`; chỉ khẳng định lưu khi kiểm tra được kết quả. |
| Mũi tên/nhãn bị cắt, chữ nhỏ | Điều chỉnh context/clip, kiểm tra ảnh gốc; không kéo giãn ảnh nhỏ để che việc cắt sai. |
| Muốn thu nhỏ mũi tên cũ | Dùng ảnh sạch và tạo lại annotation/chụp lại; không tô trắng vùng cũ làm mất chữ hoặc UI bên dưới. |
