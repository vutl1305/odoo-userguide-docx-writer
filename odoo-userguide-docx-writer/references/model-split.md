# Lead and capture worker responsibilities

Use when capture work is delegated. Reduce repeated reading, reruns and reporting;
never reduce the capture specification or visual review to save tokens.

| Work | Owner | Output |
|---|---|---|
| Scoped source lookup (SRS passages, code flow, current DOCX content) when the reading is large | Research worker (optional) | `briefs/<section>.research.md` evidence table |
| Verify decisive behaviour, write prose, plan frames and seed data | Lead | Brief, runnable `capture_parts.py`, section Markdown |
| Execute capture and fix the assigned frames | Worker | PNGs, manifest, brief result message |
| Review every selected image, export, check layout and replace working DOCX | Lead | One stable customer DOCX |

Model size follows the kind of work:

| Work | Model tier | Why |
|---|---|---|
| Source research (reading code, SRS, tracing flows) | **Medium** (e.g. gpt-6.1-terra, Sonnet) | Needs real comprehension; a small model misreads flows or stops early. Still far cheaper than the lead. |
| Capture execution (run tests, fix selectors from debug shots) | **Small** | Manual work on a fully specified skeleton. |
| Decisions, prose, image acceptance, final DOCX | **Lead** (strong) | Owns correctness and quality. |

Whatever the tier, the dispatch carries **full context and detail**: the worker cannot see the
conversation. State the goal and why, the end user's task, exact sources/paths/commands, what
is already known or ruled out, the expected output format, bounds and the stop condition. A
short vague hand-off costs more in retries than a complete one.

Follow the user's current worker type and permission mode. Use the existing clone DB pool
with its own ports/filestores; reuse idle clones, one active capture per DB. Do not create
a DB for each new worker. Keep the clones for later sections unless removal is requested.

## Source research worker (optional)

Use it only when the reading is large (about 5+ source files, long SRS passages, or a whole
existing chapter). For a small section the lead reads directly: the hand-off plus
verification costs more than the reading saved.

The lead's research brief must be narrow, because a vague brief returns vague evidence:
- goal: which section, what the end user must be able to do;
- exact sources: model/view files, named Odoo standard files, SRS headings, DOCX headings;
- numbered questions (screen path, required fields, button visibility, rights, state before/
  after, records created, error messages), each answered with `file:line`, SRS heading/table
  or the query used, and typed as SRS / code / DB; unverified stays "chưa xác minh";
- bounds: follow only directly called functions; anything outside the list is asked, not
  searched; no code/DB changes, no Odoo run, no guessing from field names;
- output file `briefs/<section>.research.md`: Q table, EN→VI labels, SRS–code gaps, open points.

Execution rules learned in practice:
- Smoke-test tools first in the dispatch ("run `pwd && ls <dir>` then continue"). A worker
  that reports "no tools" or ends a turn without reading anything gets one explicit retry;
  then switch its model (keep the worker and brief) instead of re-prompting.
- Codex sandbox modes may block `localhost` DB connections. The lead runs the few SELECTs for
  labels/module state itself, or pastes their output into the brief; do not raise the worker
  to full access just for this.
- Demand completion in one turn: "work until the file is written; no interim report; every
  question answered or marked unverified". Partial files still happen: send one gap list,
  then stop the worker and finish the remaining points directly.
- The lead re-reads the decisive code (rights, approvals, money, records created/changed,
  stage changes) before writing; worker answers are leads, not citations to copy blindly.
- Sections that explain relationships or rules still get a screenshot when the text names
  on-screen entry points (smart buttons, menus): one framed shot per form, labels taken from
  that shot.

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
