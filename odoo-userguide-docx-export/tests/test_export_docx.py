"""python3 -m unittest discover -s tests  (from the skill folder)"""
import struct, subprocess, sys, tempfile, unittest, zlib
from pathlib import Path

from docx import Document
from docx.shared import Inches

SKILL = Path(__file__).resolve().parents[1]


def png(path):
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0))
                     + chunk(b'IDAT', zlib.compress(b'\x00\xff\xff\xff')) + chunk(b'IEND', b''))


class ExportDocx(unittest.TestCase):
    def test_replaces_only_the_section_and_renumbers_figures(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            png(root / 'a.png')
            d = Document()
            d.add_heading('2. Thao tác chung', 1)
            d.add_heading('2.1. Đăng nhập', 2)
            d.add_heading('2.1.1. Mở trang', 3)
            d.add_paragraph('Đoạn văn mở đầu đủ dài để làm mẫu cho đoạn thường trong tài liệu.')
            for text in ('Mục đích: x', 'Điều kiện: y'):
                p = d.add_paragraph(); p.add_run(text.split(' ')[0] + ' ').bold = True; p.add_run(text.split(' ')[1])
            p = d.add_paragraph(); p.add_run('1. ').bold = True; p.add_run('Chọn Đăng nhập.')
            d.add_paragraph().add_run().add_picture(str(root / 'a.png'), width=Inches(1))
            d.add_paragraph('Hình 1. Màn hình đăng nhập.')
            t = d.add_table(rows=2, cols=2); t.cell(0, 0).text = 'Trường'; t.cell(1, 0).text = 'Tên'
            for label, text in (('Kết quả:', 'z'), ('Lưu ý:', 'w')):
                p = d.add_paragraph(); p.add_run(label + ' ').bold = True; p.add_run(text)
            d.add_heading('3. Nghiệp vụ', 1)
            d.add_heading('3.1. Khách hàng', 2)
            d.add_paragraph('Nội dung cũ sẽ bị thay.')
            d.add_heading('3.1.1. Tạo hồ sơ', 3)
            d.add_paragraph('Khung cũ 3.1.1.')
            d.add_heading('3.1.2. Cập nhật', 3)
            d.add_paragraph('Khung 3.1.2 chưa viết, phải giữ.')
            d.add_heading('3.2. Cơ hội', 2)
            d.add_paragraph('Giữ nguyên nội dung 3.2 của khách.')
            src = root / 'src.docx'; d.save(src)
            md = root / 'sec.md'
            md.write_text('## 3.1. Khách hàng\n\n**Mục đích:** Tạo hồ sơ.\n\n1. Người dùng chọn **Mới**.\n\n'
                          '![Nút Mới](a.png)\n*Người dùng chọn Mới.*\n\n| Trường | Ý nghĩa |\n|---|---|\n| Tên | **Bắt buộc**. |\n\n'
                          '### 3.1.1. Tạo hồ sơ\n\n**Kết quả:** đã lưu.\n\n![Hồ sơ](a.png)\n*Hồ sơ đã lưu.*\n')
            out = root / 'out.docx'
            r = subprocess.run([sys.executable, str(SKILL / 'scripts/export_docx.py'), src, out, md, '--no-toc'],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            texts = [p.text for p in Document(out).paragraphs]
            self.assertNotIn('Nội dung cũ sẽ bị thay.', texts)
            self.assertIn('Giữ nguyên nội dung 3.2 của khách.', texts)
            self.assertIn('Khung 3.1.2 chưa viết, phải giữ.', texts)
            self.assertNotIn('Khung cũ 3.1.1.', texts)
            self.assertEqual(texts.count('3.1.1. Tạo hồ sơ'), 1)
            self.assertIn('1. Người dùng chọn Mới.', texts)
            self.assertIn('3.1.1. Tạo hồ sơ', texts)
            self.assertEqual([t for t in texts if t.startswith('Hình')],
                             ['Hình 1. Màn hình đăng nhập.', 'Hình 2. Người dùng chọn Mới.', 'Hình 3. Hồ sơ đã lưu.'])
            self.assertIn('figures: 3 captions, 3 pictures', r.stdout)


if __name__ == '__main__':
    unittest.main()
