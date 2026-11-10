---
name: odoo-userguide-docx-writer
description: Use when creating or revising a Vietnamese customer-facing Odoo user guide in Word (.docx), including outline approval, task instructions from an SRS, real screenshots, clickable cross-references, or preserving a customer-edited DOCX.
---

# Odoo user guide DOCX writer

Write guides that let non-technical customers do their work in Odoo. The deliverable is an **editable Word file**; never hand the customer Markdown. The defaults below record the style this customer chose; a newer request from the user always wins. Instructions here are in English; **the document itself is Vietnamese**, and quoted phrases (“Người dùng”, “Kết quả:”) are the exact wording to use.

## Decide scope before writing

1. Identify the sources, the latest DOCX, the approved outline and the assigned part. Read what is provided; record missing sources in internal notes. Do not assume the Odoo version or treat customizations as standard features.
2. **Outline not approved:** produce an outline DOCX (all headings + planned scope) and stop for review. **Approved, or asked to continue:** write the assigned part now without re-asking settled questions. Do not write the remaining chapters on your own.
3. **Revising:** the DOCX the user last edited is the source. Keep its content, order and deletions; never rebuild from old Markdown or scripts. Write a new version file and keep the original. When asked only to merge the outline, copy every sub-heading from the approved outline.

Read [writing conventions](references/customer-guide.md) when choosing the outline or writing content. An existing outline beats the default one. If `authoring-user-guide`, `reviewing-user-guide` or `content-template-gateway` are available, use the relevant parts, but never let their default structure restore content the customer removed.

## Defaults to keep

- Vietnamese, address the reader as **“Người dùng”**, short sentences, formal chapter titles. Font **Times New Roman** everywhere: body, tables, captions, header/footer, TOC.
- Include a document introduction, system overview and **standard Odoo common operations**, besides the business chapters. Do not mirror the SRS structure.
- One main guide per business goal. **Describe fields and rules right at the create/edit step**, not in a separate reference list. No worked-example chapter or repeated reference tables unless asked.
- No assumptions/open-questions appendix in the customer copy; keep open points in internal notes and never present them as confirmed behaviour. Skip long reminders about the admin account, sample data, test environment or how to read the guide if the user removed them.
- Every **written step** has an image right after it. Every **“Kết quả”** paragraph has an image right after it showing the real state after the action; prefer a clean image so data, status or output can be checked.
- **Annotation is optional.** Mark only when the reader must find a specific button/field or a hard-to-spot detail. Overviews, saved records, report tables and clear outputs use clean images. When marking, use a small arrow or thin frame that covers no text. Every image still gets a **1px outer border**, a caption and alt text. Without a real image yet, draft `[ẢNH: màn hình, vị trí và thao tác hoặc kết quả cần minh họa]`; never claim images are complete.
- **Few, useful cross-references.** Write “… theo mục X.Y” only when the reader must perform a multi-step task documented elsewhere (open the right screen, mark done, where a status is explained). No references for basic actions such as saving or filtering, none in figure captions, and no sentences describing the document structure (“thao tác chung dẫn đến mục 2”) in the customer copy.
- **Cross-references must be clickable** and jump to the heading. Run `scripts/link_section_refs.py` after writing/merging and before adding image borders; resolve every number it reports as unresolved.
- Company, owner, product and record names look like real operating data; never “Khách hàng minh họa”, “Cơ hội hướng dẫn”, “MH…”. Without permitted real data, invent plausible fictional data.

## Screenshots and formatting

Read [screenshots and Word technique](references/screenshots-and-docx.md) before capturing or changing layout. Real UI only; never AI-generated or AI-edited UI images. Use admin when granted and allowed; do not infer other roles' rights from admin. Respect a no-web-search request; local Odoo access is not web search.

To capture, follow the [runnable capture workflow](references/capture-workflow.md): check environment → copy the template add-on → create temp DB and data → declare frames/selectors → log in and wait for UI → save clean + annotated images + manifest → review images → insert into Word → drop the temp DB. The self-contained template lives in `assets/odoo_userguide_capture/` and uses `HttpCase.browser_js` with `Page.captureScreenshot`; it does not depend on another skill.

- `scripts/screenshot_annotations.js`: only draws the small arrow/frame and computes the crop; the template add-on drives the browser, writes PNGs and the manifest.
- `scripts/style_docx_images.py INPUT.docx OUTPUT.docx`: adds a 0.75pt (1px at 96dpi) Word border; keeps text and image data.
- `scripts/link_section_refs.py INPUT.docx OUTPUT.docx`: turns “mục 2.7”, “mục 2.9–2.11”, “mục 4.4 và 4.5” into blue, underlined internal links to the heading; reports numbers with no heading.
- `scripts/check_docx.py FILE.docx --require-step-images`: checks structure, fonts, borders and per-step images. For an outline DOCX omit `--require-step-images`.

## Before handing over

Compare with scope and source: no lost manual edits, no restored deletions, nothing beyond the assigned part. Review images per step and per “Kết quả”: open each one, drop unnecessary marks, check arrows cover no text and borders are thin. Render to PDF with an available tool to check layout, TOC page numbers and that links land on the right page; automated checks do not replace looking at the render. Record skipped checks in internal notes and state limits that affect the handover.

Reply in Vietnamese with the **DOCX** link, a short change summary and what is not yet written. Do not send Markdown instead of Word. Do not publish, commit or push the document or the skill unless asked.
