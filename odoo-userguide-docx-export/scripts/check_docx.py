#!/usr/bin/env python3
"""Check editable text font, picture outlines/alt text, and optional step images."""
import argparse
import json
import re
from zipfile import ZipFile
from lxml import etree

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture',
      'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}
W = '{%s}' % NS['w']

def check(path, expected_font='Times New Roman', require_step_images=False):
    issues, fonts, pictures, steps = [], set(), 0, 0
    parser = etree.XMLParser(resolve_entities=False, no_network=True)
    with ZipFile(path) as archive:
        if archive.testzip() is not None:
            issues.append('archive: invalid DOCX ZIP')
        if len(archive.namelist()) != len(set(archive.namelist())):
            issues.append('archive: duplicate parts')
        styles = etree.fromstring(archive.read('word/styles.xml'), parser)
        style_map = {s.get(W+'styleId'): s for s in styles.findall(W+'style')}
        default = next((s.get(W+'styleId') for s in style_map.values()
                        if s.get(W+'type') == 'paragraph' and s.get(W+'default') == '1'), 'Normal')
        def declared_font(element):
            if element is None:
                return None
            return element.get(W+'hAnsi') or element.get(W+'ascii')
        default_font = declared_font(styles.find('w:docDefaults/w:rPrDefault/w:rPr/w:rFonts', NS))
        def style_font(key):
            seen = set()
            while key and key not in seen:
                seen.add(key)
                style = style_map.get(key)
                if style is None:
                    break
                font = declared_font(style.find('w:rPr/w:rFonts', NS))
                if font:
                    return font
                parent = style.find(W+'basedOn')
                key = parent.get(W+'val') if parent is not None else None
            return default_font
        heading_ids = set()
        for key, style in style_map.items():
            name = style.find(W+'name')
            if style.find('w:pPr/w:outlineLvl', NS) is not None or re.match(
                    r'^heading\s*\d', name.get(W+'val', '') if name is not None else key, re.I):
                heading_ids.add(key)
        parts = [name for name in archive.namelist() if re.match(
            r'^word/(document|header\d+|footer\d+)\.xml$', name)]
        for part in parts:
            root = etree.fromstring(archive.read(part), parser)
            for paragraph in root.findall('.//'+W+'p'):
                style = paragraph.find('w:pPr/w:pStyle', NS)
                key = style.get(W+'val') if style is not None else default
                text = ''.join(paragraph.xpath('.//w:t/text()', namespaces=NS))
                for run in paragraph.findall(W+'r'):
                    run_text = ''.join(run.xpath('.//w:t/text()', namespaces=NS))
                    if not any(c.isalpha() for c in run_text):
                        continue
                    rstyle = run.find('w:rPr/w:rStyle', NS)
                    font = declared_font(run.find('w:rPr/w:rFonts', NS))
                    if not font and rstyle is not None:
                        font = style_font(rstyle.get(W+'val'))
                    font = font or style_font(key) or '(font not explicitly resolved)'
                    fonts.add(font)
                if (part == 'word/document.xml' and key not in heading_ids and re.match(r'^\d+[.)]\s', text)
                        and not paragraph.xpath('ancestor::w:sdt', namespaces=NS)):  # TOC lines are not steps
                    steps += 1
                    sibling = paragraph.getnext()
                    while sibling is not None and sibling.tag == W+'p' and not (
                            sibling.xpath('.//w:t|.//w:drawing', namespaces=NS)):
                        sibling = sibling.getnext()
                    if require_step_images and (sibling is None or not sibling.xpath('.//w:drawing', namespaces=NS)):
                        issues.append('step-image: ' + text[:100])
            for picture in root.xpath('//pic:pic', namespaces=NS):
                pictures += 1
                widths = picture.xpath('pic:spPr/a:ln/@w', namespaces=NS)
                if widths != ['9525']:
                    issues.append(f'border: {part}, picture {pictures}, expected 9525 EMU')
            for prop in root.xpath('//wp:docPr', namespaces=NS):
                if not prop.get('descr', '').strip():
                    issues.append(f'alt-text: {part}, picture {prop.get("id")}')
    for font in sorted(fonts):
        if font.casefold() != expected_font.casefold():
            issues.append('font: ' + font)
    return {'ok': not issues, 'steps': steps, 'pictures': pictures,
            'fonts': sorted(fonts), 'issues': issues}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('docx')
    parser.add_argument('--font', default='Times New Roman')
    parser.add_argument('--require-step-images', action='store_true')
    args = parser.parse_args()
    result = check(args.docx, args.font, args.require_step_images)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['ok'] else 1)
