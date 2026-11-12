---
name: odoo-userguide-docx-export
description: Use when reviewed Markdown sections of a Vietnamese Odoo user guide must be turned into the customer's Word file (.docx), or when a guide DOCX needs its figures renumbered, section references linked, picture borders, TOC page numbers or structure checked. Runs locally with python-docx and LibreOffice; no AI writing.
---

# Odoo user guide DOCX export

Turn reviewed Markdown sections into the customer's DOCX with one local command. The writing and screenshots come from `odoo-userguide-docx-writer`; this skill only exports. Do not rewrite text while exporting: if the wording is wrong, fix the Markdown and export again.

## Export

```bash
python3 scripts/export_docx.py WORKING.docx /tmp/guide-staged.docx guide/3.1-*.md [guide/3.2-*.md ...] \
    --version 0.16 --date DD/MM/YYYY --note "Nội dung thay đổi"
```

- `SOURCE.docx` is the latest DOCX (the one the customer last edited). `OUTPUT.docx` is a temporary staging file, not another customer version. Keep the stable customer filename: after structural checks and visual review pass, replace the working DOCX with the staged file. Until then, keep the source intact; check Office locks before replacement.
- Each Markdown file replaces **only the headings it contains**: from its first heading up to the next heading of the same or higher level, or the first sub-heading not in the file. So a file with `3.2`, `3.2.1`, `3.2.2` rewrites those and keeps the outline of `3.2.3`... Everything else, including the customer's edits, stays as it is.
- Formatting is copied from paragraphs already in the source (Times New Roman, step, caption, “Kết quả”, “Lưu ý”, 2-column table, headings), so the output matches earlier versions.
- The script then, in order: renumbers every “Hình N.” and picture title in the whole document, updates “Phiên bản / ngày”, the history table, footer and properties, links “mục X.Y” references (`link_section_refs.py`), adds 1px picture borders (`style_docx_images.py`), writes the real TOC page numbers from a **temporary** PDF render (LibreOffice, deleted afterwards), and runs `check_docx.py`.
- Read its output: `figures: N captions, N pictures` must match, `TOC: ... not found` must be empty, `check: OK`. Fix the Markdown, not the DOCX, and export again.
- Deliver only the DOCX. Make a PDF only when the user asks.

## Pitfalls seen in real use

- **Renamed or renumbered headings keep stale content.** A section stops at "the first sub-heading the file does not contain", so after restructuring (e.g. `3.2 Mua hàng` → `3.2.1`) the old body survives below the new one (figure count jumps). Empty the old chapter body in a temp copy of the source first (keep its Heading 1), then export. Keep at least one chapter with steps, a picture and every heading level in the source, or add a temporary template paragraph (e.g. a Heading 4) and remove it afterwards: `find_templates` needs each kind.
- **`SOURCE` = `OUTPUT` is refused** ("Write to a new file"): export to a separate staging path, validate and visually review it, then replace the single working DOCX. Do not create `_v...` deliverables unless the user requests them.
- **TOC is a static list** inside a `w:sdt`; the script only refreshes page numbers of entries that already exist. After adding/removing level 1–2 headings, rebuild the entries (clone an existing entry per heading, text = heading, page `0`) and export again to fill the pages. LibreOffice UNO index update does not see this TOC and injects Calibri; do not use it.
- Export adds a history row every run: when re-running for the same version, keep only the last row.

## Google Drive / Google Docs compatibility

Word tolerates these, Drive shows "No preview available" or cannot convert. Check and fix after every export:

- Duplicate `wp:docPr id` (renumber sequentially) and duplicate bookmark names/ids (the export puts the same `_ug_sec_1` / `900000` bookmark on every Heading 1; remove the unused ones).
- Orphan images in `word/media` (left by replaced sections) and oversized PNGs: drop media no relationship uses, cap width at ~1500 px, quantize screenshots to 256 colours (`dither=0`); a 145-image guide went 15 MB → 3.6 MB with no visible loss.
- Zip packaging: `[Content_Types].xml` must be the first entry, no directory entries (`word/`, `word/_rels/`…), every `Override`/relationship target must exist.
- **If even a minimal fresh DOCX shows `Type: Unknown` on Drive, the file is not the problem**: the uploading machine sends a wrong MIME type. On Linux with WPS Office, `~/.local/share/mime/packages/Override.xml` maps `*.docx` → `application/wps-office.docx` (`xdg-mime query filetype x.docx` shows it). Fix with the user's consent: back up, remove the Office globs from that file (it is read-only, `chmod u+w` then restore), add a user package mapping `docx/xlsx/pptx/doc/xls/ppt/rtf` to the standard types with weight 100, run `update-mime-database ~/.local/share/mime`, restart the browser, delete and re-upload the files.

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
