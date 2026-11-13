# Writing and revision conventions

The guide is Vietnamese. Quoted Vietnamese text below is the exact wording or heading to use.

## Sources and evidence

- Read the assigned SRS, business flows, screenshots or print templates. If both Markdown and DOCX exist, read both and identify the versions; do not assume a file exists because it was mentioned.
- Consult the project knowledge base if any; check source code and the running UI when needed. Keep technical evidence in internal notes; the customer guide contains no model names, methods, SQL or source paths.
- The SRS sets scope; the UI/code confirms how it actually works. When they conflict, record the gap; never silently invent a button or pick one rule and present it as agreed.
- Verify the actual version, language and modules. A customized Odoo is not the standard app of the same name.

**Settle conventions before the first capture.** Changing them later means recapturing every affected image:
- Local accounting: Vietnamese chart of accounts and VAT (e.g. 1561/632/5111/1311/3311/1331/33311, GTGT 10%) when the readers are Vietnamese accountants; a test DB on Odoo's generic chart (110100, 600000, 15% tax) looks wrong to them. Recode accounts and add the local tax (with its own tax group label) on the capture DB if the customer's DB is not set up yet.
- Configuration branches the reader must tell apart (e.g. inventory valuation Automatic vs Periodic, costing methods): decide which branches get worked examples, then give each chapter the same parallel structure with the branch named in the heading (“X.2. Khi dùng định giá Tự động”, “X.3. Khi dùng định giá Định kỳ”). A chapter that only mentions the other branch in passing confuses readers.
- Whether the customer's name may appear in the text (cover only, or nowhere).

## Default outline when none is approved

Starting point; adapt to the business in the sources:

1. Giới thiệu tài liệu và tổng quan hệ thống.
2. Hướng dẫn sử dụng giao diện và thao tác chung trên Odoo.
3. Thiết lập hệ thống trước khi sử dụng.
4. Hướng dẫn thực hiện nghiệp vụ.
5. Giải thích thuật ngữ.
6. Lịch sử cập nhật tài liệu.

Chapter 3 opens with one sentence on its audience (administrators, Sale Admin; end users may skip it). Skip chapter 3 when nothing needs configuring before use.

Do not turn each SRS business group into a top-level chapter; organise them inside chapter 4 by task. Do not add “Bắt đầu từ đâu”, “Bắt đầu nhanh”, “Hiểu cách hệ thống vận hành”, a separate “Quy trình và nguyên tắc nghiệp vụ” rules chapter, a troubleshooting chapter, a worked-example chapter, a repeated business reference list or an assumptions chapter. A separate rules chapter mostly repeats chapter 4 and drifts out of sync when code changes.

Rules the steps do not show (automatic status/stage changes, approver snapshot, what resets an approval, report gaps, data scope by role, things the system does not block yet) go as short **“Lưu ý:”** paragraphs or a 2-column table at the top of the matching chapter 3/4 section; the data scope by role goes with the role table of the account setup section. The overall business flow belongs in chapter 1.

Optional appendices, only when the customer asks, placed before the glossary:

| Appendix | Content |
|---|---|
| “Xử lý tình huống thường gặp” | Only errors actually met in testing or support: symptom → cause → fix → result or support contact. No invented cases. |
| “Bảng tra cứu nhanh” | For managers and internal support: data scope by role, approval flow summary. Tables only, each row linking to the detailed section; never re-explain the steps. |

The introduction states at least: what the guide covers, for whom, business limits, related apps and the overall flow. Optional sub-sections (access conditions, how to look things up, image conventions) only when useful and not removed by the user. Never restore them when revising a trimmed document.

## Scope of Odoo common operations

Confirm each function exists before writing it up:

| Group | Consider |
| --- | --- |
| Access | Login/logout; preferences, language, timezone; apps and menus. |
| Viewing and finding | List, Kanban, form; search, filter, group; save/reuse searches. |
| Data entry | Create, edit, save, discard; relational, date, number fields, detail lines, computed/read-only values. |
| Collaboration | Notes, messages, attachments, history; schedule/complete activities, notifications, related documents. |
| Reporting | Pivot, graph, measures, filters, currency, export when permitted/available. |

Do not assume “Sửa” or “Lưu” buttons exist: some versions edit inline, autosave and show a manual save icon. Use the labels actually shown; English labels that remain in the UI are kept and briefly explained in Vietnamese. Do not claim dashboards, pinning reports, calendar sync or approval buttons just because Odoo can support them.

## Structure of one business guide

- Goal, role and real preconditions for the task.
- How to open the screen, using the verified menu path.
- Numbered steps, one clear action each, each followed by its image. The image may show the action or its result; the caption must state exactly that state.
- At the create/edit part, a field table: **Tên trường | Ý nghĩa | Cách nhập/chọn | Bắt buộc/điều kiện | Mặc định/tự điền/chỉ đọc và quy tắc**. Confirm only properties with evidence. Explain codes, units, dates and currency where used.
- Rules affecting save/send/approve, edit locks and status changes go at the relevant step. Rules shared by many tasks are explained once, in the intro of the chapter 4 section they belong to, and referenced from the others, not copied as full field tables.
- **“Kết quả:”** describe the sign of completion, then insert an image right below showing the state after the action. Result images are clean by default; mark only a detail that is hard to spot. Choose a view with enough data/status instead of repeating the before-click image. If the result is not verified, keep a draft placeholder; never use a before-action image to claim success.

Cross-references to other sections:

| Case | How to write |
| --- | --- |
| Multi-step task with its own guide (open the opportunity list, mark an activity done) | “… theo mục 2.3”, as a clickable link. |
| Where a concept/status is explained in detail | “… được giải thích tại mục 4.4”. |
| Basic action (save, check filters, a button already shown above) | State the action directly, no reference. |
| Figure caption | Describe the image only, no reference. |
| Progress/structure notes (“mục 3–6 là khung”) | Internal drafts only; remove on release. |

Never write an automatic action as something the user must click. Never write a confirmation button the UI does not show; for conditional steps, describe the result image and the condition in text.

## Revising the customer copy

| Request | How |
| --- | --- |
| Outline only | DOCX with headings and planned scope; no full procedures yet. |
| Write up to a section | Stop exactly there; leave the rest as approved. |
| Merge outline to split work | Keep written content, add all sub-headings and scope from the approved outline; do not write details. |
| User just edited the DOCX | Snapshot the original and its version marks; revise a new file from that DOCX, never regenerate from old Markdown. |
| Images/fonts only | Keep content and remaining geometry where possible; no restructuring, new lead-ins or assumptions. |
| Notes/appendix removed | Keep them removed; log important gaps internally, do not re-insert default reminders. |

Distinguish document version from Odoo version. Update the history table with the actual changes. Do not hard-code one document's customer name, modules, paths or step counts as rules for every document.
