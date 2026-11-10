import unittest,subprocess,tempfile,zipfile,json,struct,zlib
from pathlib import Path
from docx import Document
from docx.shared import Inches
from lxml import etree as E
SKILL=Path(__file__).resolve().parents[1]
class Tools(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
  png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1,1,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b'\x00\xff\xff\xff'))+chunk(b'IEND',b'')
  image=self.root/'pixel.png';image.write_bytes(png)
  d=Document();d.styles['Normal'].font.name='Times New Roman';d.styles['Heading 1'].font.name='Times New Roman';d.add_heading('2. Thao tác chung',1);d.add_paragraph('1. Người dùng chọn Đăng nhập.')
  pic=d.add_paragraph().add_run().add_picture(str(image),width=Inches(4));pic._inline.docPr.set('descr','Nút Đăng nhập')
  self.source=self.root/'source.docx';d.save(self.source)
 def tearDown(self):self.tmp.cleanup()
 def run_script(self,name,*args):return subprocess.run(['python3',str(SKILL/'scripts'/name),*map(str,args)],text=True,capture_output=True)
 def test_border_preserves_source_text_images_and_geometry(self):
  before=self.source.read_bytes();out=self.root/'bordered.docx';r=self.run_script('style_docx_images.py',self.source,out);self.assertEqual(r.returncode,0,r.stderr)
  self.assertEqual(before,self.source.read_bytes())
  with zipfile.ZipFile(self.source) as a,zipfile.ZipFile(out) as b:
   for n in a.namelist():
    if n.startswith('word/media/'):self.assertEqual(a.read(n),b.read(n))
   ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing','pic':'http://schemas.openxmlformats.org/drawingml/2006/picture'}
   x=E.fromstring(a.read('word/document.xml'));y=E.fromstring(b.read('word/document.xml'))
   self.assertEqual(x.xpath('//w:t/text()',namespaces=ns),y.xpath('//w:t/text()',namespaces=ns));self.assertEqual(x.xpath('//wp:extent/@cx',namespaces=ns),y.xpath('//wp:extent/@cx',namespaces=ns))
   self.assertEqual(y.xpath('//pic:spPr/a:ln/@w',namespaces=ns),['9525'])
  r=self.run_script('check_docx.py',out,'--require-step-images');self.assertEqual(r.returncode,0,r.stdout+r.stderr)
 def test_cannot_overwrite_source(self):
  before=self.source.read_bytes();r=self.run_script('style_docx_images.py',self.source,self.source);self.assertNotEqual(r.returncode,0);self.assertEqual(before,self.source.read_bytes())
 def test_checker_finds_missing_step_image(self):
  d=Document(self.source);d.add_paragraph('2. Người dùng nhập mật khẩu.');d.save(self.source);out=self.root/'bordered.docx';self.run_script('style_docx_images.py',self.source,out)
  r=self.run_script('check_docx.py',out,'--require-step-images');self.assertEqual(r.returncode,1,r.stdout+r.stderr);self.assertTrue(any('step-image' in s for s in json.loads(r.stdout)['issues']))
 def test_checker_finds_wrong_font(self):
  d=Document(self.source);d.paragraphs[1].runs[0].font.name='Arial';d.save(self.source);out=self.root/'bordered.docx';self.run_script('style_docx_images.py',self.source,out)
  r=self.run_script('check_docx.py',out);self.assertEqual(r.returncode,1,r.stdout+r.stderr);self.assertTrue(any('font' in s for s in json.loads(r.stdout)['issues']))
 def test_links_section_references_to_headings(self):
  d=Document(self.source);d.add_heading('2.7. Lưu thông tin',2);d.add_paragraph('Trước khi đăng xuất, lưu theo mục 2.7 và mục 9.9.');d.save(self.source)
  out=self.root/'linked.docx';r=self.run_script('link_section_refs.py',self.source,out);self.assertEqual(r.returncode,0,r.stderr);self.assertIn("unresolved: ['9.9']",r.stdout)
  W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}';d=Document(out)
  marks={e.get(W+'name'):p.text for p in d.paragraphs for e in p._p.iter(W+'bookmarkStart')}
  links=[(''.join(t.text for t in h.iter(W+'t')),marks[h.get(W+'anchor')]) for h in d.paragraphs[-1]._p.iter(W+'hyperlink')]
  self.assertEqual(links,[('mục 2.7','2.7. Lưu thông tin')]);self.assertTrue(next(d.paragraphs[-1]._p.iter(W+'hyperlink')).findall('.//'+W+'u'));self.assertEqual(d.paragraphs[-1].text,'Trước khi đăng xuất, lưu theo mục 2.7 và mục 9.9.')
if __name__=='__main__':unittest.main()
