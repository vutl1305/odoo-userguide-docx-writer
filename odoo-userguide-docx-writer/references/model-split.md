# Lead and capture worker responsibilities

Use when capture work is delegated. Reduce repeated reading, reruns and reporting;
never reduce the capture specification or visual review to save tokens.

| Work | Owner | Output |
|---|---|---|
| Scoped source lookup (SRS passages, code flow, current DOCX content) when the reading is large | Research worker (optional) | `briefs/<section>.research.md` evidence table |
| Verify decisive behaviour, write the capture brief (frames + seed-data spec with required checks), write prose | Lead | `briefs/<section>.capture-brief.md`, section Markdown |
| Write the capture script from the brief, run it, fix failing frames | Capture worker | `test_capture_<section>.py`, PNGs, manifest, brief result message |
| Render the review page (`scripts/review_html.py`) and open it for the user | Lead (one command) | `review_image/review-<section>.html` |
| Approve text and images on the review page; flag image IDs to fix | **User** (when they accept this split) | List of IDs + short reason |
| Export after approval, check layout and replace working DOCX | Lead | One stable customer DOCX |

Model size follows the kind of work:

| Work | Model tier | Why |
|---|---|---|
| Source research (reading code, SRS, tracing flows) | **Medium** (e.g. gpt-6.1-terra, Sonnet) | Needs real comprehension; a small model misreads flows or stops early. Still far cheaper than the lead. |
| Capture script + fixing failing frames (read debug shots, change selectors/waits/crops) | **Medium with vision** (e.g. Sonnet) | Must read the UI state from screenshots and Odoo's DOM; a weak model guesses, loops or weakens checks. |
| Re-run with known selectors (timing/crop only) | Small | Mechanical once the frame is solved. |
| Decisions, prose, image acceptance, final DOCX | **Lead** (strong) | Owns correctness and quality. |

Whatever the tier, the dispatch carries **full context and detail**: the worker cannot see the
conversation. State the goal and why, the end user's task, exact sources/paths/commands, what
is already known or ruled out, the expected output format, bounds and the stop condition. A
short vague hand-off costs more in retries than a complete one.

## Other work the lead can delegate

Delegate only mechanical work whose result the lead can check cheaply; keep decisions,
business explanations and final acceptance with the lead.

| Work | Tier | Lead keeps |
|---|---|---|
| Clone DB + filestore, runner/test scripts, ports for a new worker | Small | Smoke-run one test |
| Capture script from the capture brief **plus a passing script to copy from** (done by the capture worker) | Medium | Review seed data, required checks and `until` conditions |
| Markdown for task sections (steps, image lines, captions, “Kết quả” from brief + manifest) | Medium | Explanatory text (rules, journal entries, “Lưu ý”, comparisons, field tables); read the whole file |
| Image pre-review against §6 (crop, marks over text, numbers vs brief, error dialogs): a list of flagged IDs with reasons | Medium with vision | §6 acceptance unchanged; it only catches rework earlier. Reduce the lead's own pass to flagged + decisive images (journal entries, stock values) only when the user accepts sampled review to save tokens |
| Consistency check of numbers and references across Markdown, brief, capture report (document numbers, amounts, “mục X.Y”) | Medium | Decide each fix |
| Run the export script and report its three checks | Small | Only worth it bundled with the two checks above |

Keep with the lead: scope and conventions, the example data chain, explanatory prose,
diagram content, decisive image acceptance and the handover. Sections with **fewer than 5 shots**, or whose seed data hides business traps (dates reset on
confirm, states reached only by a cron or time shift), the lead writes and runs the script itself.
The first run of a script is the real capture, not a rehearsal: passing frames are done; a
worker gets only the frames that failed, with debug paths. Failures caused by seed data,
business logic or the environment (wrong totals, a state that never appears, a module error)
are not selector work: the worker stops and returns them to the lead, who reads the code and
fixes the seed.

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
  searched; no code/DB changes (SELECT only), no Odoo run, no guessing from field names;
- output file `briefs/<section>.research.md`, in two parts so the lead reads less without
  losing nuance:
  - **Part A (lead reads all):** per question **Fact** (short) · **Trap / exception** (no length
    limit: edge cases, what a field does *not* mean, what is missing vs SRS; this is what makes
    the prose correct) · **Evidence** (`file:line`, SRS heading or query); then SRS–code gaps
    and open points.
  - **Part B (lead looks up when needed):** DB facts with queries, IDs/values for the seed,
    exact UI labels EN→VI, verbatim system messages, status labels.
  - No filler: state the scope/limits once at the top; no repeated disclaimers or generic
    hedges per answer; no long seed code (list records, IDs and functions to call; the lead
    writes the seed); do not restate the same fact in several sections.

Execution rules learned in practice:
- Smoke-test tools first in the dispatch ("run `pwd && ls <dir>` then continue"). A worker
  that reports "no tools" or ends a turn without reading anything gets one explicit retry;
  then switch its model (keep the worker and brief) instead of re-prompting.
- **DB inspection belongs to the research worker**, not the lead: existing config rows,
  templates/IDs, menus, record counts, labels. The brief says "SELECT only on `<db>`; write
  what you found as section 0 of the result", and asks for the IDs/values the seed will need.
  The lead does not explore the DB before writing the brief: each lead tool call resends the
  whole long context, and guessed column names turn one lookup into many failed calls.
- If the worker's sandbox blocks `localhost` DB connections, ask the user to allow the
  worker DB access; only if refused, the lead runs the SELECTs in one batched script.
- Demand completion in one turn: "work until the file is written; no interim report; every
  question answered or marked unverified". Partial files still happen: send one gap list,
  then stop the worker and finish the remaining points directly.
- The lead re-reads the decisive code (rights, approvals, money, records created/changed,
  stage changes) before writing; worker answers are leads, not citations to copy blindly.
- Sections that explain relationships or rules still get a screenshot when the text names
  on-screen entry points (smart buttons, menus): one framed shot per form, labels taken from
  that shot.

## Prepare once, run in batches

1. The lead supplies a capture brief (or, for sections under 5 shots / tricky seed data, the
   script itself): source/seed data, real UI paths and translated
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
- a **self-check before reporting**: the worker opens every PNG it produced and checks the
  known defects — frame around a whole form/sheet, arrow pointing into empty space, half-cut
  button or text at the crop edge, search facets combined with "or" when one filter was meant,
  sample names clashing with the demo user, test/placeholder data visible (e.g. another
  feature's SMS text), error dialogs, untranslated labels (report only). It fixes what it can
  within the retry limit and lists the rest; the lead then reviews each image once.

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
