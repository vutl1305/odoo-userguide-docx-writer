# odoo-userguide-docx-writer

Agent skill (Claude Code / Codex) for writing **Vietnamese, customer-facing Odoo user guides as editable Word (.docx) files**, illustrated with real screenshots captured from a disposable Odoo database.

The agent reads `SKILL.md`; this README is for people.

## What it does

- Plans the outline, then writes task guides from an SRS: numbered steps, an image after every step and every “Kết quả” (result), field tables at the create/edit step.
- Captures real screenshots through Odoo `HttpCase` + headless Chrome: clean and annotated PNGs (small arrow or thin frame), real login/logout across page loads, manifest per flow.
- Writes each section as Markdown with the screenshots for review; the companion skill `odoo-userguide-docx-export` turns it into the customer's Word file locally (Times New Roman, 1px image borders, clickable “mục X.Y” references, TOC page numbers, structural checks).
- Revises customer-edited DOCX files without losing manual edits.

## Install

```bash
# per project
git clone git@github.com:vutl1305/odoo-userguide-docx-writer.git .claude/skills/odoo-userguide-docx-writer
# or for all projects
git clone git@github.com:vutl1305/odoo-userguide-docx-writer.git ~/.claude/skills/odoo-userguide-docx-writer
```

Then ask the agent, e.g. “Dùng skill odoo-userguide-docx-writer viết mục 2.2 trong Huong_dan_v0.10.docx”.

## Requirements

- Python 3 with `python-docx` and `lxml` (DOCX scripts and tests).
- For screenshots: Odoo source with a compatible Python, PostgreSQL rights to create a temporary `ug_*` database, Google Chrome, `websocket-client` (can live in a temp `PYTHONPATH`). Verified on Odoo 20.
- LibreOffice (optional) to render PDF and check layout/TOC/links.

## Layout

| Path | Purpose |
| --- | --- |
| `SKILL.md` | Entry point and defaults for the agent. |
| `references/customer-guide.md` | Outline, writing and revision conventions. |
| `references/screenshots-and-docx.md` | Image choice (clean vs annotated), Word technique. |
| `references/capture-workflow.md` | Step-by-step capture runbook. |
| `assets/odoo_userguide_capture/` | Template add-on (`HttpCase`) that captures the images. |
| `scripts/screenshot_annotations.js` | Draws the small arrow/frame and computes the crop. |
| `tests/` | Unit tests and the browser test page for the annotation helper. |

## Tests

```bash
python3 -m unittest discover -s tests
google-chrome --headless --dump-dom "file://$PWD/tests/annotations.html" | grep -o '<pre id="result">[^<]*'
```
