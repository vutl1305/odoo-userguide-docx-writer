#!/usr/bin/env python3
"""Turn "mục 2.7" style cross-references into internal links to the heading.

Usage: link_section_refs.py INPUT.docx OUTPUT.docx
Each number after "mục" (also in ranges/lists: "mục 2.9–2.11", "mục 4.4 và 4.5")
becomes a blue, underlined w:hyperlink to the bookmark on the numbered heading. Headings without a
bookmark get one. Numbers with no matching heading are reported, not linked.
"""
import copy
import re
import sys
from pathlib import Path

from docx import Document

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
XML_SPACE = '{http://www.w3.org/XML/1998/namespace}space'
NUM = r'\d+(?:\.\d+)*'
REF = re.compile(r'[Mm]ục\s+' + NUM + r'(?:\s*(?:–|-|,|và)\s*' + NUM + r')*')


def heading_bookmarks(doc):
    marks, next_id = {}, 900000
    for p in doc.paragraphs:
        if not p.style.name.startswith('Heading') or not re.match(NUM, p.text):
            continue
        number = re.match(NUM, p.text)[0]
        start = p._p.find(W + 'bookmarkStart')
        if start is None:
            name = '_ug_sec_' + number.replace('.', '_')
            start = p._p.makeelement(W + 'bookmarkStart', {W + 'id': str(next_id), W + 'name': name})
            end = p._p.makeelement(W + 'bookmarkEnd', {W + 'id': str(next_id)})
            ppr = p._p.find(W + 'pPr')
            (ppr.addnext if ppr is not None else lambda e: p._p.insert(0, e))(start)
            p._p.append(end)
            next_id += 1
        marks.setdefault(number, start.get(W + 'name'))
    return marks


def link_run(run, spans):
    """Split run at spans [(start, end, anchor)] and wrap each span in a hyperlink."""
    text = run.find(W + 't').text
    pieces, pos = [], 0
    for start, end, anchor in spans:
        pieces += [(text[pos:start], None), (text[start:end], anchor)]
        pos = end
    pieces.append((text[pos:], None))
    for piece, anchor in pieces:
        if not piece:
            continue
        r = copy.deepcopy(run)
        t = r.find(W + 't')
        t.text = piece
        t.set(XML_SPACE, 'preserve')
        if anchor:
            rpr = r.find(W + 'rPr')
            if rpr is None:
                rpr = r.makeelement(W + 'rPr', {})
                r.insert(0, rpr)
            # Direct formatting: many generated DOCX files lack a Hyperlink style, so
            # a style-only link looks like plain text.
            for tag in ('color', 'u'):
                for old in rpr.findall(W + tag):
                    rpr.remove(old)
            rpr.append(rpr.makeelement(W + 'color', {W + 'val': '0563C1'}))
            rpr.append(rpr.makeelement(W + 'u', {W + 'val': 'single'}))
            link = run.makeelement(W + 'hyperlink', {W + 'anchor': anchor, W + 'history': '1'})
            link.append(r)
            r = link
        run.addprevious(r)
    run.getparent().remove(run)


def main(src, dst):
    if Path(dst).exists():
        sys.exit('Choose a new output file; the source and existing files are preserved.')
    doc = Document(src)
    marks = heading_bookmarks(doc)
    linked, missing = 0, []
    for p in doc.paragraphs:
        if p.style.name.startswith(('Heading', 'TOC', 'Contents')):
            continue
        ref = REF.search(p.text)
        if ref and not any(REF.search(t.text or '') for t in p._p.iter(W + 't')):
            missing.append('split-run: ' + ref[0])
        for run in list(p._p.findall(W + 'r')):  # direct runs only: skip existing links
            t = run.find(W + 't')
            if t is None or not t.text or 'ục' not in t.text:
                continue
            spans = []
            for ref in REF.finditer(t.text):
                for k, num in enumerate(re.finditer(NUM, ref[0])):
                    if num[0] in marks:  # first link covers "mục 2.7" for a bigger click target
                        spans.append((ref.start() + (0 if k == 0 else num.start()), ref.start() + num.end(), marks[num[0]]))
                    else:
                        missing.append(num[0])
            if spans:
                link_run(run, spans)
                linked += len(spans)
    doc.save(dst)
    print(f'{linked} references linked; unresolved: {missing or "none"}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(*sys.argv[1:])
