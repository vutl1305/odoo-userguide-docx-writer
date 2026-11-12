# Real screenshots and DOCX technique

## Environment and data

With Odoo source available, use the skill's self-contained template in `assets/odoo_userguide_capture/`: a temporary add-on outside the repo, `HttpCase.browser_js` and headless Chrome. Setup and commands are in the [capture workflow](capture-workflow.md). If only a running test system is available, use the browser tool you were given. `odoo-app-store-listing` may be consulted but is not required, and its App Store page structure is not a Word guide structure.

- Use the project's environment, version and language. Capture as admin when allowed; keep account/rights details in internal checks if the customer does not want that note in the guide.
- Create/edit/delete for screenshots only on permitted test data. A self-made temp DB gets its own name, matching `db_name` **and `dbfilter`**, its own data dir, no cron, no outgoing mail.
- Use natural fictional names such as “Công ty TNHH Dinh dưỡng An Phú”, “Nguyễn Minh Anh”, “An Phú – H-Meal tháng 11”. Never put “minh họa”, “hướng dẫn”, “test” or an “MH” prefix in displayed names. Real customer names/PII are not needed for this.
- Create records through the system/ORM in the test environment; never alter text, values or states on an image to fake a working UI.
- Do not print config secrets. Do not infer other roles' rights from this environment. Do not send external email/chat just to get an image.
- Keep the capture DB with its `data_dir` for the next part and record it in the capture note. Drop only a DB the agent created, only when the user asks or the guide is done; check the exact name, never the source DB, never mass-delete by name pattern.

## Images for steps and for “Kết quả”

Keep a manifest with at least: step or result ID, section, instruction/result text, image, before/after state, and clean vs annotated choice (arrow target only when annotated). Capture the state before the click or after the result, as the caption says. One overview image for several steps does not satisfy “one image per step”.

### Clean or annotated

| Purpose | Presentation |
| --- | --- |
| Action step: click/select/switch/type | Small arrow or thin frame on the exact button, menu item or input named in the step. |
| Target sits right next to text (e.g. avatar beside the company name) | Thin frame only (`box_only`), so no arrow crosses the text. |
| Overview, saved form, report table/chart with no action to locate | Clean. If the accompanying step asks for an action, the action rule above takes precedence. |
| “Kết quả” | Captured after the action, clean, showing state/data/output; placed right after the result paragraph. |

Examples: create record → saved form with its name; note → the note in the history; schedule activity → the activity added; export Excel → the content of the really exported file; login → home screen; logout → login screen. A before-click image pointing at Lưu/Gửi/Xuất never replaces the result image.

Clean images still get the **1px outer border in Word**; that border is not a red mark. Do not mark images just to make them look alike. The template may save both versions; the document need not use the annotated one.

Read and run the [capture workflow](capture-workflow.md): temp DB config, template add-on, admin login, navigation, `Page.captureScreenshot`, clean/annotated PNGs and manifest. Calling the helper and clearing the overlay produces no image. The template is inside this skill; do not look for one in another skill.

The helper only adds a non-interactive overlay; it never captures, logs in or clicks for the user. If the tool cannot clip, capture the full page and crop with a normal image tool, leaving UI content untouched. Never use AI to create/edit UI images, and never remove an old arrow by painting over text; recapture a clean image to change the marks.

Arrow defaults: **2px** shaft, about **60px** long, **10 × 8px** head, `markerUnits="userSpaceOnUse"` (otherwise SVG scales the head by stroke width up to ~40px). Target frame 1.5px; that is a marker, not the image border.

Crop: keep enough labels and context to compare, but not mostly empty background. Crop to the relevant card/menu with a `clip` of selectors plus padding; widen to include the arrow, never cut its tail. Avoid capturing a view-switch button when you want the Pivot table: `.o_pivot` can match the button; pick the real table element. For menus, dialogs, long fields or edge positions, check text and arrowhead are not cut or covered.

The OS file picker may not appear in browser screenshots: when showing an uploaded file, say it is the result. Excel images must come from the actually exported file; if only a converted view is available, do not fake an Excel/Calc window. Never claim an email was sent when only the composer was captured.

## Word

- Use the available Word/DOCX tooling; `python-docx` when installed. Do not force every document through an old script that drops manual edits.
- A4, consistent margins and sizes; Times New Roman for body, tables, headings, captions, TOC, header/footer. Fonts inside screenshots stay Odoo's.
- “mục X.Y” references are internal links (`w:hyperlink w:anchor`) to the heading bookmark, with **direct blue colour and underline**. Do not rely on the Hyperlink style alone: many generated DOCX files do not define it and the link then looks like plain text. The clickable area is the whole “mục X.Y”. Word needs Ctrl+click by default; PDF is a direct click. Verify in the rendered PDF that links land on the right page.
- Real headings, kept levels and numbering, automatic TOC with page numbers. Update the TOC after changing images/fonts.
- Insert images directly so the DOCX is self-contained. Keep aspect ratio and **one scale for all screenshots** (e.g. 750px → full text width, about 0.022 cm/px), capped at text width; never blow a small crop up to full width. Set keep-with-next on step → image and on the “Kết quả” paragraph → its image so they do not split across pages. Add alt text.
- Outer border **1px = 0.75pt = 9525 EMU** at 96dpi, thin grey. `style_docx_images.py` sets it on the Word picture, not on the pixels. If a PNG with a raster border is required, add exactly 1 pixel outside the image with an allowed image tool.
- When editing the DOCX ZIP, keep image relationships and PAGE/NUMPAGES/TOC fields. Do not reassign text to every footer run (it can delete dynamic fields). Do not duplicate `docProps/core.xml` or picture/bookmark IDs when merging.
- Check the rendered PDF/Word: cut text, captions, step order, blank pages, stranded lines, tiny labels, image borders. Open every chosen image at full size against its step/caption, then inspect representative rendered pages at Word width. A contact sheet is an optional index, not acceptance evidence.

## Repeatable checks

The DOCX tools (export, reference links, borders, checker and their tests) live in the skill `odoo-userguide-docx-export`. Export Markdown sections with its `scripts/export_docx.py`; it runs the link, border, TOC and structure steps. These are structural checks; they do not prove the Odoo procedure or that an arrow hits the right button. Re-run after Word/LibreOffice saves the file, since they may normalise the XML.
