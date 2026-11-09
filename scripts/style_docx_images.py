#!/usr/bin/env python3
"""Add a 1px Word picture outline without changing screenshot pixels or text."""
import argparse
from pathlib import Path
from zipfile import ZipFile
from lxml import etree

A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
PIC = 'http://schemas.openxmlformats.org/drawingml/2006/picture'

def style_images(source, output):
    source, output = Path(source), Path(output)
    if source.resolve() == output.resolve() or output.exists():
        raise ValueError('Choose a new output file; the source and existing files are preserved.')
    count = 0
    with ZipFile(source) as archive:
        if archive.testzip() is not None:
            raise ValueError('Invalid DOCX archive')
        if len(archive.namelist()) != len(set(archive.namelist())):
            raise ValueError('Duplicate DOCX parts; repair the source before editing.')
        parts = []
        for item in archive.infolist():
            data = archive.read(item.filename)
            if item.filename.startswith('word/') and item.filename.endswith('.xml'):
                root = etree.fromstring(data, etree.XMLParser(resolve_entities=False, no_network=True))
                shapes = root.findall('.//{%s}pic/{%s}spPr' % (PIC, PIC))
                for shape in shapes:
                    for line in shape.findall('{%s}ln' % A):
                        shape.remove(line)
                    line = etree.Element('{%s}ln' % A, w='9525')
                    fill = etree.SubElement(line, '{%s}solidFill' % A)
                    etree.SubElement(fill, '{%s}srgbClr' % A, val='B7BEC8')
                    etree.SubElement(line, '{%s}prstDash' % A, val='solid')
                    # The outline precedes effects/extensions in CT_ShapeProperties.
                    index = next((i for i, child in enumerate(shape)
                                  if etree.QName(child).localname in
                                  ('effectLst', 'effectDag', 'scene3d', 'sp3d', 'extLst')), len(shape))
                    shape.insert(index, line)
                    count += 1
                if shapes:
                    data = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
            parts.append((item, data))
    # Exclusive creation prevents overwriting a manually edited deliverable.
    with output.open('xb') as stream, ZipFile(stream, 'w') as archive:
        for item, data in parts:
            archive.writestr(item, data)
    return count

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('output')
    args = parser.parse_args()
    try:
        count = style_images(args.source, args.output)
    except (ValueError, OSError) as error:
        parser.exit(2, str(error) + '\n')
    print(f'{count} pictures styled: 0.75pt / 1px; screenshot pixels unchanged.')
