#!/usr/bin/env python3
"""Render section Markdown files into one HTML page for the user to review before DOCX export.

usage: review_html.py OUT.html guide/4.11.5-x.md [guide/4.11.6-y.md ...]
Shows text, tables and images exactly as written in the Markdown (stdlib only, no export).
"""
import html
import os
import re
import sys


def inline(text):
    text = html.escape(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    return text


def render(md_path, out_dir):
    base = os.path.dirname(os.path.abspath(md_path))
    lines = open(md_path, encoding='utf-8').read().split('\n')
    out, table = [], []

    def flush_table():
        if table:
            rows = [r for r in table if not re.match(r'^\|\s*-', r)]
            cells = [[c.strip() for c in r.strip('|').split('|')] for r in rows]
            body = ''.join('<tr>' + ''.join(f'<{"th" if i == 0 else "td"}>{inline(c)}</{"th" if i == 0 else "td"}>'
                                             for c in row) + '</tr>' for i, row in enumerate(cells))
            out.append(f'<table>{body}</table>')
            table.clear()

    for line in lines:
        if line.startswith('|'):
            table.append(line)
            continue
        flush_table()
        m = re.match(r'^!\[(.*?)\]\((.+?)\)', line)
        if m:
            src = os.path.relpath(os.path.join(base, m.group(2)), out_dir)
            out.append(f'<div class="img"><img src="{html.escape(src)}" alt="{html.escape(m.group(1))}">'
                       f'<div class="path">{html.escape(os.path.basename(m.group(2)))}</div></div>')
        elif re.match(r'^#{2,4} ', line):
            level = len(line.split(' ')[0])
            out.append(f'<h{level}>{inline(line[level + 1:])}</h{level}>')
        elif re.match(r'^\*[^*].*\*$', line):
            out.append(f'<p class="cap">{inline(line[1:-1])}</p>')
        elif re.match(r'^\d+\. ', line):
            out.append(f'<p class="step">{inline(line)}</p>')
        elif line.strip():
            out.append(f'<p>{inline(line)}</p>')
    flush_table()
    return '\n'.join(out)


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    out = os.path.abspath(sys.argv[1])
    out_dir = os.path.dirname(out)
    os.makedirs(out_dir, exist_ok=True)
    style = ('body{font-family:sans-serif;max-width:1100px;margin:20px auto;line-height:1.5}'
             'img{max-width:100%;border:1px solid #999}.img{margin:8px 0}.path{font-size:12px;color:#888}'
             '.cap{font-style:italic;color:#555;margin-top:0}.step{font-weight:500;margin-top:24px}'
             'table{border-collapse:collapse;margin:8px 0}td,th{border:1px solid #bbb;padding:4px 8px;vertical-align:top}'
             'section{border-bottom:2px solid #ccc;padding-bottom:30px}')
    parts = [f'<section>{render(p, out_dir)}</section>' for p in sys.argv[2:]]
    with open(out, 'w', encoding='utf-8') as f:
        f.write(f'<!doctype html><meta charset="utf-8"><title>Review</title><style>{style}</style>' + ''.join(parts))
    print(out)


if __name__ == '__main__':
    main()
