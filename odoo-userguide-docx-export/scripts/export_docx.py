#!/usr/bin/env python3
"""Insert reviewed Markdown guide sections into an existing DOCX (local only, no AI).

Usage:
  export_docx.py SOURCE.docx OUTPUT.docx SECTION.md [SECTION.md ...]
                 [--version 0.16 --date 11/11/2026 --note "..."] [--no-toc] [--no-check]

Each SECTION.md starts with a numbered heading (e.g. "## 3.1. Quản lý thông tin khách hàng").
Everything under the heading with the same number in SOURCE, up to the next heading of the same
or a higher level or the first sub-heading the file does not contain, is replaced; the rest of the document (customer edits) is kept. Formatting is
cloned from SOURCE's own paragraphs, found by their text ("Mục đích:", "1. ", "Hình 1.", ...).

Markdown lines (blank line = paragraph break; one block per line):
  #, ##, ###, ####  heading level 1-4 (numbered text, e.g. "### 3.1.2. Cập nhật ...")
  **Mục đích:** ...      purpose paragraph        **Điều kiện:** / **Vai trò thực hiện:** ...  condition
  1. text                step (number kept as written)
  ![alt](path.png)       picture; the next line "*caption*" becomes "Hình N. caption"
  **Kết quả:** ...       result (kept with the next picture)
  **Lưu ý:** ...         note (kept with the next picture)
  | a | b |              2-column table; first row = header, a |---| row is skipped
  other text             normal paragraph; **bold** works everywhere
Then: figures renumbered in the whole document, version/history updated, section references linked,
1px picture borders, TOC page numbers taken from a temporary PDF render, structure check.
"""
import argparse
import copy
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from docx import Document
from docx.shared import Emu
from PIL import Image

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
XML_SPACE = '{http://www.w3.org/XML/1998/namespace}space'
DOCPR = '{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}docPr'
HERE = Path(__file__).resolve().parent
MAX_WIDTH = 5975985                 # EMU, text width of the guide
EMU_PER_PX = MAX_WIDTH / 750        # same scale as earlier versions
NUM = re.compile(r'\d+(?:\.\d+)*')
CAPTION = re.compile(r'^Hình \d+\.\s*')


# ---------- template detection ----------
def find_templates(doc):
    """Clone formatting from paragraphs already in the guide, found by their text."""
    found = {}
    body = list(doc.element.body.iterchildren())
    for p in doc.paragraphs:
        t, first = p.text, (p.runs[0].text if p.runs else '')
        el = p._p
        checks = {
            'purpose': t.startswith('Mục đích:'),
            'cond': t.startswith('Điều kiện:'),
            'result': t.startswith('Kết quả:'),
            'note': t.startswith('Lưu ý:'),
            'caption': bool(CAPTION.match(t)),
            'step': bool(re.fullmatch(r'\d+\. ', first)) and len(p.runs) > 1,
            'image': el.find('.//' + W + 'drawing') is not None,
            'normal': p.style.name == 'Normal' and len(t) > 40 and not p.runs[0].bold
                      and el.find('.//' + W + 'drawing') is None and not CAPTION.match(t),
        }
        for k, ok in checks.items():
            if ok and k not in found:
                found[k] = el
        m = re.match(r'Heading (\d)', p.style.name)
        if m and f'h{m[1]}' not in found:
            found[f'h{m[1]}'] = el
    step_at = body.index(found['step']) if 'step' in found else 0
    for el in body[step_at:]:
        if el.tag == W + 'tbl' and len(el.findall(W + 'tr')[0].findall(W + 'tc')) == 2 and len(el.findall(W + 'tr')) > 1:
            found['table'] = el
            break
    missing = {'purpose', 'cond', 'result', 'note', 'caption', 'step', 'image', 'normal', 'table'} - set(found)
    if missing:
        sys.exit(f'Template paragraphs not found in source DOCX: {sorted(missing)}')
    return {k: copy.deepcopy(v) for k, v in found.items()}


# ---------- building blocks ----------
def md_bold(text):
    return [(s, i % 2 == 1) for i, s in enumerate(text.split('**')) if s]


def set_runs(p, parts, base=None):
    rs = p.findall(W + 'r')
    if base is None:
        base = rs[0] if rs else p.makeelement(W + 'r', {})   # empty cell/paragraph has no run to copy
    for r in rs:
        p.remove(r)
    for tag in ('bookmarkStart', 'bookmarkEnd', 'hyperlink'):
        for e in p.findall(W + tag):
            p.remove(e)
    for text, bold in parts:
        r = copy.deepcopy(base)
        for e in r.findall(W + 'drawing'):
            r.remove(e)
        rpr = r.find(W + 'rPr')
        if rpr is None:
            rpr = r.makeelement(W + 'rPr', {})
            r.insert(0, rpr)
        b = rpr.find(W + 'b')
        if bold and b is None:
            rpr.append(rpr.makeelement(W + 'b', {}))
        if not bold and b is not None:
            rpr.remove(b)
        t = r.find(W + 't')
        if t is None:
            t = r.makeelement(W + 't', {})
            r.append(t)
        t.text = text
        t.set(XML_SPACE, 'preserve')
        p.append(r)
    return p


def keep_next(p):
    ppr = p.find(W + 'pPr')
    if ppr is None:
        ppr = p.makeelement(W + 'pPr', {})
        p.insert(0, ppr)
    if ppr.find(W + 'keepNext') is None:
        ppr.insert(1 if ppr.find(W + 'pStyle') is not None else 0, ppr.makeelement(W + 'keepNext', {}))
    return p


class Builder:
    def __init__(self, doc, tpl):
        self.doc, self.tpl = doc, tpl

    def par(self, key, text):
        return set_runs(copy.deepcopy(self.tpl[key]), md_bold(text))

    def heading(self, level, text):
        key = f'h{level}'
        if key not in self.tpl:
            sys.exit(f'No Heading {level} in source DOCX to copy formatting from')
        return set_runs(copy.deepcopy(self.tpl[key]), [(text, False)])

    def step(self, number, text):
        p = copy.deepcopy(self.tpl['step'])
        rs = p.findall(W + 'r')
        num, body = copy.deepcopy(rs[0]), copy.deepcopy(rs[1])
        set_runs(p, md_bold(text), base=body)
        num.find(W + 't').text = f'{number}. '
        p.findall(W + 'r')[0].addprevious(num)
        return p

    def image(self, path, alt):
        width = min(MAX_WIDTH, int(Image.open(path).width * EMU_PER_PX))
        tmp = self.doc.add_paragraph()
        tmp.add_run().add_picture(str(path), width=Emu(width))
        drawing = tmp._p.find('.//' + W + 'drawing')
        tmp._p.getparent().remove(tmp._p)
        drawing.find('.//' + DOCPR).set('descr', alt)
        p = copy.deepcopy(self.tpl['image'])
        run = p.find('.//' + W + 'drawing').getparent()
        run.remove(run.find(W + 'drawing'))
        run.append(drawing)
        return p

    def caption(self, text):
        p = copy.deepcopy(self.tpl['caption'])
        ts = p.findall('.//' + W + 't')
        ts[0].text = 'Hình 0. ' + text      # renumbered later
        for t in ts[1:]:
            t.text = ''
        return p

    def table(self, rows):
        tbl = copy.deepcopy(self.tpl['table'])
        trs = tbl.findall(W + 'tr')
        head, row_tpl = trs[0], copy.deepcopy(trs[1])
        for tr in trs:
            tbl.remove(tr)
        for i, cells in enumerate(rows):
            if len(cells) != 2:
                sys.exit(f'Only 2-column tables are supported: {cells}')
            tr = head if i == 0 else copy.deepcopy(row_tpl)
            for tc, text in zip(tr.findall(W + 'tc'), cells):
                parts = [(text.replace('**', ''), True)] if i == 0 or tc is tr.findall(W + 'tc')[0] else md_bold(text)
                set_runs(tc.find(W + 'p'), parts)
            tbl.append(tr)
        return tbl


# ---------- Markdown ----------
def parse_md(path, b):
    lines = path.read_text(encoding='utf-8').splitlines()
    out, i = [], 0
    first_heading, numbers = None, set()
    while i < len(lines):
        line = lines[i].rstrip()
        i += 1
        if not line.strip() or line.startswith('<!--'):
            continue
        if m := re.match(r'^(#{1,4})\s+(.*)$', line):
            level, text = len(m[1]), m[2].strip()
            if first_heading is None:
                first_heading = (level, text)
                continue
            out.append(b.heading(level, text))
            numbers.add(NUM.match(text)[0] if NUM.match(text) else text)
        elif m := re.match(r'^!\[(.*)\]\((.+)\)$', line):
            img = (path.parent / m[2]).resolve()
            if not img.exists():
                sys.exit(f'{path.name}: image not found: {m[2]}')
            out.append(b.image(img, m[1]))
            cap = lines[i].strip() if i < len(lines) else ''
            if not re.fullmatch(r'\*[^*].*\*', cap):
                sys.exit(f'{path.name}: picture {m[2]} needs a caption line "*...*" right after it')
            out.append(b.caption(cap[1:-1].strip()))
            i += 1
        elif line.startswith('|'):
            rows = []
            while line.startswith('|'):
                cells = [c.strip() for c in line.strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-{3,}:?', c) for c in cells):
                    rows.append(cells)
                line = lines[i].rstrip() if i < len(lines) else ''
                i += 1
            i -= 1
            out.append(b.table(rows))
        elif m := re.match(r'^(\d+)\.\s+(.*)$', line):
            out.append(b.step(m[1], m[2]))
        elif line.startswith('**Mục đích:**'):
            out.append(b.par('purpose', line))
        elif line.startswith(('**Điều kiện:**', '**Vai trò thực hiện:**')):
            out.append(b.par('cond', line))
        elif line.startswith('**Kết quả:**'):
            out.append(keep_next(b.par('result', line)))
        elif line.startswith('**Lưu ý:**'):
            out.append(keep_next(b.par('note', line)))
        else:
            p = b.par('normal', line)
            if line.endswith(':'):      # table lead-in
                keep_next(p)
            out.append(p)
    if first_heading is None:
        sys.exit(f'{path.name}: must start with a numbered heading')
    return first_heading, out, numbers


def replace_section(doc, heading, new_elements, md_numbers=()):
    """Replace from the heading to the next heading of the same/higher level, or to the first
    sub-heading the Markdown does not contain (so "3.2 + 3.2.1 + 3.2.2" keeps 3.2.3...)."""
    level, text = heading
    number = NUM.match(text)
    if not number:
        sys.exit(f'Heading must start with its number: {text}')
    number = number[0]
    paras = {p._p: p for p in doc.paragraphs}
    body = doc.element.body
    start = None
    for el in body.iterchildren():
        p = paras.get(el)
        if p is not None and p.style.name == f'Heading {level}' and NUM.match(p.text) and NUM.match(p.text)[0] == number:
            start = el
            break
    if start is None:
        sys.exit(f'Heading {number} (level {level}) not found in source DOCX')
    el = start.getnext()
    while el is not None and el.tag != W + 'sectPr':
        p = paras.get(el)
        m = re.match(r'Heading (\d)', p.style.name) if p is not None else None
        if m and (int(m[1]) <= level or (NUM.match(p.text) and NUM.match(p.text)[0] not in md_numbers)):
            break
        nxt = el.getnext()
        if el.tag != W + 'sdt':
            body.remove(el)
        el = nxt
    for e in reversed(new_elements):
        start.addnext(e)


# ---------- whole-document passes ----------
def renumber_figures(doc):
    n = 0
    for p in doc.paragraphs:
        if CAPTION.match(p.text):
            n += 1
            ts = p._p.findall('.//' + W + 't')
            ts[0].text = CAPTION.sub(f'Hình {n}. ', ts[0].text, count=1)
    k = 0
    for pr in doc.element.body.iter(DOCPR):
        k += 1
        pr.set('title', f'Hình {k}')
    return n, k


def update_version(doc, version, date, note):
    old = None
    for t in doc.tables:
        for r in t.rows:
            if r.cells[0].text.strip() == 'Phiên bản / ngày' and len(r.cells) > 1:
                old = r.cells[1].text.split('/')[0].strip()
                set_runs(r.cells[1].paragraphs[0]._p, [(f'{version} / {date}', False)])
    for t in doc.tables:
        if t.rows[0].cells[0].text.strip() == 'Phiên bản':
            t._tbl.append(copy.deepcopy(t.rows[-1]._tr))
            for c, v in zip(t.rows[-1].cells, (version, date, note)):
                set_runs(c.paragraphs[0]._p, [(v, False)])
            break
    return old


def replace_in_parts(path, old, new):
    tmp = path.with_suffix('.tmp')
    with zipfile.ZipFile(path) as zi, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
        for it in zi.infolist():
            data = zi.read(it.filename)
            if it.filename.startswith('word/footer') or it.filename == 'docProps/core.xml':
                data = data.decode().replace(old, new).encode()
            zo.writestr(it, data)
    tmp.replace(path)


def update_toc_pages(path):
    """Write real page numbers into the TOC from a temporary PDF render (LibreOffice)."""
    import pypdf
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', tmp, str(path)],
                       check=True, capture_output=True)
        pages = [' '.join(pg.extract_text().split()) for pg in pypdf.PdfReader(Path(tmp) / (path.stem + '.pdf')).pages]
    doc = Document(path)
    entries = []
    for sdt in doc.element.body.findall(W + 'sdt'):
        for p in sdt.findall('.//' + W + 'p'):
            ts = [t for t in p.findall('.//' + W + 't') if t.text and t.text.strip()]
            if len(ts) >= 2 and NUM.match(ts[0].text.strip()):
                entries.append((' '.join(ts[0].text.split()), ts[-1]))
    if not entries:
        return 0, []
    last = entries[-1][0]
    toc_end = next(i for i, pg in enumerate(pages) if last in pg)   # the TOC itself holds the first copy of its last entry
    missing = []
    for title, t in entries:
        page = next((i + 1 for i in range(toc_end + 1, len(pages)) if title in pages[i]), None)
        if page is None:
            missing.append(title)
        else:
            t.text = str(page)
    doc.save(path)
    return len(entries) - len(missing), missing


def run_tool(name, *args):
    r = subprocess.run([sys.executable, str(HERE / name), *map(str, args)], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f'{name} failed:\n{r.stdout}{r.stderr}')
    return r.stdout.strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('source', type=Path)
    ap.add_argument('output', type=Path)
    ap.add_argument('sections', type=Path, nargs='+')
    ap.add_argument('--version')
    ap.add_argument('--date')
    ap.add_argument('--note', default='')
    ap.add_argument('--no-toc', action='store_true')
    ap.add_argument('--no-check', action='store_true')
    a = ap.parse_args()
    if a.source.resolve() == a.output.resolve():
        sys.exit('Write to a new file; keep the source version')

    doc = Document(a.source)
    b = Builder(doc, find_templates(doc))
    for md in a.sections:
        heading, elements, numbers = parse_md(md, b)
        replace_section(doc, heading, elements, numbers)
        print(f'{md.name}: replaced section {heading[1]} ({len(elements)} blocks)')
    captions, pictures = renumber_figures(doc)
    old = update_version(doc, a.version, a.date, a.note) if a.version else None
    doc.save(a.output)
    if old and old != a.version:
        replace_in_parts(a.output, old, a.version)

    with tempfile.TemporaryDirectory() as tmp:
        linked = Path(tmp) / 'linked.docx'
        print(run_tool('link_section_refs.py', a.output, linked))
        print(run_tool('style_docx_images.py', linked, Path(tmp) / 'styled.docx'))
        shutil.copy(Path(tmp) / 'styled.docx', a.output)
    print(f'figures: {captions} captions, {pictures} pictures' + ('' if captions == pictures else '  <-- MISMATCH'))
    if not a.no_toc:
        ok, missing = update_toc_pages(a.output)
        print(f'TOC: {ok} page numbers updated' + (f'; not found: {missing}' if missing else ''))
    if not a.no_check:
        r = subprocess.run([sys.executable, str(HERE / 'check_docx.py'), str(a.output), '--require-step-images'],
                           capture_output=True, text=True)
        issues = json.loads(r.stdout)['issues']
        print('check: OK' if not issues else 'check issues:\n  ' + '\n  '.join(issues))


if __name__ == '__main__':
    main()
