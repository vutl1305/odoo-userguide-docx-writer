# Splitting work between a strong and a cheap model

Use when the user assigns different models to different steps. Most tokens go into the
capture loop (run, failing selector, read debug image, fix, rerun); quality depends on
analysis and prose. So split by **kind of work**, not by how hard a section looks.

| Step | Work | Model | Output |
|---|---|---|---|
| 1. Analyse | Read SRS + code, decide real behaviour, UI labels EN/VI, SRS gaps, plan shots and data; **write the `capture_parts.py` skeleton** | **strong** | `briefs/<section>.md` (section brief) + `<parts dir>/capture_parts.py` |
| 2. Capture | Run the skeleton, read debug images, fix selectors/waits/crops until pass | cheap | `shots/`, manifest, `briefs/<section>.capture.md` (capture report) |
| 3. Write | Section Markdown from the brief + images | **strong** | `guide/<section>.md` |
| 4. Export | `export_docx.py`, read its checks | cheap | DOCX + check output |
| 5. Review | Contact sheet vs text, SRS gaps for the user | **strong** | reply to the user |

Paths are relative to the guide assets dir (e.g. `docs_local/user_guide_assets/`).
Steps 1, 3, 5 may be one strong-model session; steps 2 and 4 are separate cheap-model runs.
If the brief is vague the cheap model guesses and the saving is lost: spend effort on step 1.

### Hand the cheap model a runnable skeleton, not a reading list
Lesson from v0.19–v0.20 (3.1/3.4 and 3.5–3.10): a cold worker that must read SKILL.md,
capture-workflow, capture_env, briefs and a 400-line sample, then write the script itself,
needed 30–60 min before the first image and wandered into source digging (OWL code, tours —
the capture harness uses neither). Most fixes after that were one run each.
- In step 1 the strong model writes `<parts dir>/capture_parts.py` itself: seed data, menu
  path (`data-menu-xmlid`), every frame id from the brief with selector, clip and wait.
  Copy from the last passing parts file; selectors were already looked up for the brief.
- Handoff = brief + skeleton + the run command + the rules below. No other reading list.
  Tell the worker explicitly: do not read Odoo/web source; fix only from debug images.
- Start the worker in **Default** (approval) mode so drift is visible from the permission
  stream; in YOLO mode check its files/progress yourself before trusting the report.
- Very small sections (≤ ~8 shots) may be cheaper for the strong model to capture directly.

## Rules for the cheap model (steps 2 and 4)

1. **The brief is the spec.** Do not decide business behaviour, do not edit the brief,
   do not write guide prose. If Odoo behaves differently from the brief (other button,
   other status, unexpected dialog), stop that shot and record it under “Bất thường”.
2. **Retry limit:** at most 3 capture attempts per shot. Still failing → mark it
   `bỏ` with the last error and debug image path, move on to the next shot.
3. **Report in the fixed format below.** The strong model reads only the report and the
   contact sheet, not logs.
4. All rules in SKILL.md still apply (own DB/port, no selector fallbacks, stop on UI errors).

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

## Capture report template (written by the cheap model)

```markdown
# Báo cáo chụp <số>

| id | Trạng thái | File | Ghi chú |
|---|---|---|---|
| s41-01-menu | ok | shots/sec_4_1/annotated/s41-01-menu.png | |
| s41-05-save | bỏ | shots/sec_4_1/debug/s41-05-save-failure.png | selector .o_x không thấy sau 3 lần |

## Bất thường (khác phiếu)
- <id>: phiếu ghi ..., hệ thống hiện ... (ảnh: <path>)

Contact sheet: shots/<flow>/contact.png
```

## Contact sheet (end of step 2, read in step 5)

One image per flow so the reviewer opens one file instead of every PNG:

```bash
python3 - shots/<flow> <<'E'
import sys, glob
from PIL import Image, ImageDraw
d = sys.argv[1]; W = 600
files = sorted(glob.glob(f'{d}/annotated/*.png') + glob.glob(f'{d}/raw/*result*.png'))
ims = [Image.open(f).convert('RGB') for f in files]
ims = [i.resize((W, int(i.height * W / i.width))) for i in ims]
cols = 3; rows = [ims[k:k + cols] for k in range(0, len(ims), cols)]
H = sum(max(i.height for i in r) + 24 for r in rows)
sheet = Image.new('RGB', (W * cols, H), 'white'); y = 0; dr = ImageDraw.Draw(sheet)
for r, names in zip(rows, [files[k:k + cols] for k in range(0, len(files), cols)]):
    for c, (im, n) in enumerate(zip(r, names)):
        dr.text((c * W + 4, y + 4), n.rsplit('/', 1)[1], fill='black'); sheet.paste(im, (c * W, y + 24))
    y += max(i.height for i in r) + 24
sheet.save(f'{d}/contact.png')
E
```

The sheet checks marks and crops; wide form/list crops become too small to read text. Open a single image when its text must be checked or the mark or crop looks doubtful.
