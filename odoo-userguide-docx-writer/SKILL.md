---
name: odoo-userguide-docx-writer
description: Use when creating or revising a Vietnamese customer-facing Odoo user guide in Word (.docx), including outline approval, task instructions from an SRS, real screenshots, clickable cross-references, or preserving a customer-edited DOCX.
---

# Odoo user guide DOCX writer

Write guides that let non-technical customers do their work in Odoo. The deliverable is an **editable Word file**; never hand the customer Markdown. **Work Markdown-first:** capture images, write each section as a Markdown file with the images, review it (text and every image), and only then export to DOCX with the separate skill `odoo-userguide-docx-export` (local tools, no AI writing). Fixes go into the Markdown, then export again. The defaults below record the style this customer chose; a newer request from the user always wins. Instructions here are in English; **the document itself is Vietnamese**, and quoted phrases (“Người dùng”, “Kết quả:”) are the exact wording to use.

## Decide scope before writing

1. Identify the sources, the latest DOCX, the approved outline and the assigned part. Read what is provided; record missing sources in internal notes. Do not assume the Odoo version or treat customizations as standard features.
2. **Outline not approved:** produce an outline DOCX (all headings + planned scope) and stop for review. **Approved, or asked to continue:** write the assigned part now without re-asking settled questions. Do not write the remaining chapters on your own.
3. **Revising:** the DOCX the user last edited is the source. Keep its content, order and deletions; never rebuild the whole document from Markdown or scripts. Markdown covers only the sections being written now; the export inserts them into that DOCX and keeps everything else. Write a new version file and keep the original. When asked only to merge the outline, copy every sub-heading from the approved outline.

Read [writing conventions](references/customer-guide.md) when choosing the outline or writing content. An existing outline beats the default one. If `authoring-user-guide`, `reviewing-user-guide` or `content-template-gateway` are available, use the relevant parts, but never let their default structure restore content the customer removed.

## Defaults to keep

- Vietnamese, address the reader as **“Người dùng”**, short sentences, formal chapter titles. Font **Times New Roman** everywhere: body, tables, captions, header/footer, TOC.
- Include a document introduction, system overview and **standard Odoo common operations**, besides the business chapters. Do not mirror the SRS structure.
- One main guide per business goal. **Describe fields and rules right at the create/edit step**, not in a separate reference list. No worked-example chapter or repeated reference tables unless asked.
- No assumptions/open-questions appendix in the customer copy; keep open points in internal notes and never present them as confirmed behaviour. Skip long reminders about the admin account, sample data, test environment or how to read the guide if the user removed them.
- Every **written step** has an image right after it. Every **“Kết quả”** paragraph has an image right after it showing the real state after the action; prefer a clean image so data, status or output can be checked.
- **Annotation is optional.** Mark only when the reader must find a specific button/field or a hard-to-spot detail. Overviews, saved records, report tables and clear outputs use clean images. When marking, use a small arrow or thin frame that covers no text. Every image still gets a **1px outer border**, a caption and alt text. Without a real image yet, draft `[ẢNH: màn hình, vị trí và thao tác hoặc kết quả cần minh họa]`; never claim images are complete.
- **Few, useful cross-references.** Write “… theo mục X.Y” only when the reader must perform a multi-step task documented elsewhere (open the right screen, mark done, where a status is explained). No references for basic actions such as saving or filtering, none in figure captions, and no sentences describing the document structure (“thao tác chung dẫn đến mục 2”) in the customer copy.
- **Cross-references must be clickable** and jump to the heading. The export links them; resolve every number it reports as unresolved.
- Company, owner, product and record names look like real operating data; never “Khách hàng minh họa”, “Cơ hội hướng dẫn”, “MH…”. Without permitted real data, invent plausible fictional data.

## Screenshots and formatting

Read [screenshots and Word technique](references/screenshots-and-docx.md) before capturing or changing layout. Real UI only; never AI-generated or AI-edited UI images. Use admin when granted and allowed; do not infer other roles' rights from admin. Respect a no-web-search request; local Odoo access is not web search.

To capture, follow the [runnable capture workflow](references/capture-workflow.md): read the capture note or ask the user → preflight → copy the template add-on → seed data → declare frames/selectors → log in and wait for UI → save clean + annotated images + manifest → review images → write the section Markdown → export with `odoo-userguide-docx-export` → keep the DB and update the note. **Do not rebuild the environment each time:** before the first capture, ask the user in one message which DB to use (an existing dev/test DB, the previous capture DB, or let the agent create one) and which runtime (Python, config, addons path, port, or let the agent find or create them). Save the answer in the project's capture note and reuse it next time; a DB always goes with its own `data_dir`. Extend the template in this skill instead of forking `capture_steps` in the project. Frames use the version profile helpers (`fill`, `pick`, `saveForm`, `UG.*`): read [Odoo version profiles](references/odoo-versions.md) first; on a version without a profile, create and verify one before capturing. The self-contained template lives in `assets/odoo_userguide_capture/` and uses `HttpCase.browser_js` with `Page.captureScreenshot`; it does not depend on another skill.

- `scripts/screenshot_annotations.js`: only draws the small arrow/frame and computes the crop; the template add-on drives the browser, writes PNGs and the manifest.

## Markdown first, DOCX last

- One file per section, e.g. `<guide assets dir>/guide/3.2-co-hoi.md`, starting with its numbered heading (`## 3.2. ...`). Use the format in `odoo-userguide-docx-export` (steps `1. `, `![alt](path)` + `*caption*`, `**Kết quả:**`, `**Lưu ý:**`, 2-column tables). Image paths point to the captured `raw/` (clean, “Kết quả”) or `annotated/` (steps) PNGs; do not number figures, the export does.
- Review the Markdown and its images before exporting; tell the user the Markdown path when they want to review it.
- Export: `python3 <odoo-userguide-docx-export>/scripts/export_docx.py LATEST.docx NEW.docx guide/<section>.md --version X --date DD/MM/YYYY --note "..."`. It replaces only those sections, renumbers figures, links references, adds borders, updates TOC page numbers from a temporary PDF and checks the result. Never hand-write a per-version build script.
- **One working DOCX:** while writing, export over the same working file (`SOURCE` = `OUTPUT` is safe; still bump `--version`). Save a versioned copy (`..._vX.Y.docx`) only when sending it to the customer; a copy the customer returned with edits becomes the next source.

## Several agents on one guide

- Split by section; each agent owns only its section Markdown, its parts dir (`capture_parts.py`, `shots/`) and its own capture DB, work dir, port and log. No agent edits the DOCX, the skill or another section's files; skill changes go into the agent's report.
- Each agent's DB is a copy of the shared capture DB **with its filestore** (`pg_dump | pg_restore` works while a server is connected; `createdb -T` does not). Drop the copies and their filestores when done.
- The coordinator reviews all Markdown, then exports once with every section file in one command.
- **Strong vs cheap model:** when the user assigns models per step, follow [model split](references/model-split.md): the strong model writes the section brief, the prose and the final review; the cheap model only captures from the brief and exports, and reports deviations instead of deciding them.

## Stop and report on errors

An error seen while capturing or building is a finding for the user, never something to capture around.

- **Stop the capture only for errors visible in the UI:** an Odoo error/warning dialog (“Rất tiếc!”, “Oops”, UserError, access error), a selector that misses, or a step that reaches the wrong screen. Do not continue to the next frame, do not use earlier images and do not build the DOCX from that run.
- **Log and console errors do not stop the work** (user decision, for now): do not grep `odoo.log` after each run and do not fail a run on browser console errors. Open the log only to diagnose a failed frame.
- **Never hide UI failures:** keep the runner's `.o_error_dialog` check; no selector fallbacks (`|| el(...)`, `if(btn)`, `try { } catch {}` that continue silently). A missed target must fail the test. `expect_error: True` only for a frame that deliberately documents a business message. Look at the images before using them.
- **A “Kết quả” frame waits for the result:** every `phase: 'after'` frame has an `until(...)` on the exact state its “Kết quả:” sentence describes (card in the new column, status changed), and its crop must show the target whole; prefer `clip` to selectors over a fixed `clip_rect`.
- **Report to the user** (in Vietnamese): which step, the exact message or log line, the likely cause with evidence, and whether it is a temp-environment problem (missing filestore, module not installed, stale assets) or a real system/customization bug. Fix environment problems and recapture; for a possible system bug, stop and ask before going on, and never document the faulty behaviour as correct.
- The same applies to the export: a figure-count mismatch, TOC entries not found, a `check` issue or an unresolved reference stops the handover until fixed (in the Markdown) or reported.

## Safety in the user's repository

- Never use `git stash`, `git reset`, `git checkout -- <path>`, `git clean` or branch switches to test or compare something; copy the file to `/tmp` instead. `.claude/` and guide asset folders may be git-ignored, so `git stash` saves nothing and `git stash pop` then applies the user's **old** stash.
- If a git command changes the user's tracked files by mistake, stop, show `git status` and `git stash list`, and ask before restoring anything.
- Never delete Office lock files (`.~lock*`, `~$*`, `.~*`) or export over a DOCX that has one: the user has it open; ask them to close it.
- Write debug images only under the capture output (`<flow>/debug/`), never in the repo root. Never drop a DB the user provided.

## Before handing over

Compare with scope and source: no lost manual edits, no restored deletions, nothing beyond the assigned part. Review images per step and per “Kết quả”: open each one, drop unnecessary marks, check arrows cover no text and borders are thin. To look at the layout, render a PDF **in a temp dir (e.g. `/tmp`), never next to the DOCX**, view a few pages, then delete it; deliver a PDF only when the user asks for one. Record skipped checks in internal notes and state limits that affect the handover.

Reply in Vietnamese with the **DOCX** link, a short change summary and what is not yet written. Do not send Markdown instead of Word. Do not publish, commit or push the document or the skill unless asked.
