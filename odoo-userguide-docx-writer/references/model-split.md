# Lead and capture worker responsibilities

Use when capture work is delegated. Reduce repeated reading, reruns and reporting;
never reduce the capture specification or visual review to save tokens.

| Work | Owner | Output |
|---|---|---|
| Analyse code/SRS, write prose, plan frames and seed data | Lead | Brief, runnable `capture_parts.py`, section Markdown |
| Execute capture and fix the assigned frames | Worker | PNGs, manifest, brief result message |
| Review every selected image, export, check layout and replace working DOCX | Lead | One stable customer DOCX |

Follow the user's current worker type and permission mode. Use the existing clone DB pool
with its own ports/filestores; reuse idle clones, one active capture per DB. Do not create
a DB for each new worker. Keep the clones for later sections unless removal is requested.

## Prepare once, run in batches

1. The lead supplies a runnable skeleton: source/seed data, real UI paths and translated
   labels, each frame ID, exact action/result, target, crop and wait condition. Read labels
   from the reused DB, not guesses or only `vi.po`; installed translations can override them.
2. If the user permits a lead dry-run, run all tests once in one command before handoff.
   Passing tests still require visual review. If the user delegates all capture to workers,
   let the worker do this batch; do not take over without authorization.
3. For a few failures (about 3 or fewer), the lead can diagnose/debug and supply exact fixes;
   execute them only within the user's division of work. For many failures, assign only the
   failing tests with error/debug paths; mark passing tests “do not rerun”.
4. The worker runs the entire assigned batch in one command first, then reruns only failed
   tests. At most **2 repair attempts per frame** after the initial batch; still failing means
   stop that frame and report the error/debug path, not invent success or loop indefinitely.

## Self-contained handoff

Keep dispatch concise but complete; no arbitrary line/token budget. Include:
- run command, exact test/frame IDs, passing tests not to rerun;
- DB/port, owned output directory and file boundaries;
- per-frame action, arrow target, crop, state to wait for, and known fixes;
- no changes to application code, no production writes or external sends;
- the retry limit and a short completion report (accepted/pending IDs, errors, abnormalities).

Do not require a cold worker to read a stack of skill/brief/sample files before running.
Necessary frame instructions stay in the skeleton/dispatch. Only the lead writes the guide
or changes the DOCX. Contact sheets and long worker reports are optional, never a prerequisite.

## Keep follow-ups out of the queue

- Worker replies/notifications may be written before queued messages are read. Match each
  report to the latest assigned frames and file timestamps; an old “done” is not acceptance
  of a new correction. Handle a stable inbox ID once.
- Do not stack status requests and repeated reminders behind a busy turn. Read available
  status/artifacts when the user asks; send one consolidated correction after review.
- A report task ends after reporting; the worker must not wait on a background job it has
  already observed finished. The lead can review available images before a long report arrives.
- If work appears stalled, inspect current task, output changes and relevant failed test.
  Stop/reassign or take over only under user authorization; preserve finished frames and
  avoid concurrent writers. Do not claim the worker received a queued message until confirmed.
- Give estimates as estimates based on observed progress, not promises. “Working” alone
  does not establish progress; report which images exist and which the lead has accepted.

## Acceptance, not just test success

Follow [capture workflow §6](capture-workflow.md): open every selected PNG at full size and
compare with the exact step/caption; inspect rendered Word-width pages too. Contact sheets
are optional navigation aids, never a substitute. A worker's “all images pass” is unverified
until lead review. Reject clipped columns, unreadable names, hidden inputs, misplaced arrows,
menus covering result data, irrelevant background, or insufficient report data.

Action steps must mark the exact named control/input even on report tables (e.g. Pivot
switch, Flip axis, Counted input); result images stay clean. Close dropdowns through the real
UI and wait for the intended state; never delete/hide DOM elements to fake completion.
Rejected images get a concrete reason/target fix; do not write around them or silently omit
an essential action. Report any unresolved gap before handover.

## Worker completion message

Return only completed/pending frame IDs and paths, the exact last error/debug path for a
pending frame, and unexpected labels/data. No repeated completion report for queued status
requests. The lead owns final acceptance and export.

## Section brief template (written by the strong model)

```markdown
# Phiếu mục <số>. <tiêu đề>

Nguồn: SRS <UC/mục>, code <file:line>, ...
Tài khoản chụp: <login> (chỉ để chụp; văn bản không nêu vai trò)

## Hành vi đã chốt
- <quy tắc> — <file:line>
## Lệch SRS (văn bản viết theo hệ thống)
- SRS: ... / Hệ thống: ... — <file:line>

## Dữ liệu mẫu
- <bản ghi, giá trị cụ thể, trạng thái ban đầu>

## Ảnh cần chụp
| id | Màn hình / URL | Thao tác trước khi chụp | Khoanh (selector hoặc nhãn) | Loại | Chờ trạng thái (until) |
|---|---|---|---|---|---|
| s41-01-menu | CRM > Pipeline | mở menu | menu **Pipeline** | step | — |
| s41-result | form cơ hội | bấm **Won** | không | result | ribbon "Đạt" hiện |

## Ý chính cho văn bản
- Bước 1: ... (nhãn **EN** (VI))
- Kết quả: ...
- Lưu ý: ...
```
