---
name: odoo-userguide-docx-export
description: Use when reviewed Markdown sections of a Vietnamese Odoo user guide must be turned into the customer's Word file (.docx), or when a guide DOCX needs its figures renumbered, section references linked, picture borders, TOC page numbers or structure checked. Runs locally with python-docx and LibreOffice; no AI writing.
---

# Odoo user guide DOCX export

Turn reviewed Markdown sections into the customer's DOCX with one local command. The writing and screenshots come from `odoo-userguide-docx-writer`; this skill only exports. Do not rewrite text while exporting: if the wording is wrong, fix the Markdown and export again.

## Export

```bash
python3 scripts/export_docx.py SOURCE.docx OUTPUT.docx guide/3.1-*.md [guide/3.2-*.md ...] \
    --version 0.16 --date DD/MM/YYYY --note "Nội dung thay đổi"
```

- `SOURCE.docx` is the latest DOCX (the one the customer last edited). `OUTPUT.docx` is a new version file; the source is never overwritten.
- Each Markdown file replaces **only the headings it contains**: from its first heading up to the next heading of the same or higher level, or the first sub-heading not in the file. So a file with `3.2`, `3.2.1`, `3.2.2` rewrites those and keeps the outline of `3.2.3`... Everything else, including the customer's edits, stays as it is.
- Formatting is copied from paragraphs already in the source (Times New Roman, step, caption, “Kết quả”, “Lưu ý”, 2-column table, headings), so the output matches earlier versions.
- The script then, in order: renumbers every “Hình N.” and picture title in the whole document, updates “Phiên bản / ngày”, the history table, footer and properties, links “mục X.Y” references (`link_section_refs.py`), adds 1px picture borders (`style_docx_images.py`), writes the real TOC page numbers from a **temporary** PDF render (LibreOffice, deleted afterwards), and runs `check_docx.py`.
- Read its output: `figures: N captions, N pictures` must match, `TOC: ... not found` must be empty, `check: OK`. Fix the Markdown, not the DOCX, and export again.
- Deliver only the DOCX. Make a PDF only when the user asks.

## Markdown format

One block per line, blank line between blocks:

| Markdown | Becomes |
| --- | --- |
| `## 3.1. Tên mục` (first line) | the section to replace; `#`..`####` = Heading 1..4, numbered |
| `**Mục đích:** ...` | purpose paragraph |
| `**Điều kiện:** ...`, `**Vai trò thực hiện:** ...` | condition paragraph |
| `1. Người dùng chọn **Lưu**.` | numbered step (number as written) |
| `![alt text](relative/path.png)` then `*Chú thích*` on the next line | picture + caption “Hình N. Chú thích” |
| `**Kết quả:** ...` / `**Lưu ý:** ...` | result / note, kept on the page with the next picture |
| `\| Trường \| Ý nghĩa \|` rows (first row = header) | 2-column field table |
| any other line | normal paragraph; `**bold**` for UI labels |

Image paths are relative to the Markdown file. Every picture needs a caption line and alt text.

## Other tools

- `scripts/link_section_refs.py IN OUT`, `scripts/style_docx_images.py IN OUT`: also usable alone.
- `scripts/check_docx.py FILE.docx --require-step-images`: fonts, borders, alt text, a picture after every step (TOC lines are ignored).
- Tests: `python3 -m unittest discover -s tests` from this folder.
