# Runnable Odoo capture workflow

Use when the guide needs real images. This covers **driving the browser and capturing**; the arrow helper alone produces no image. No other skill is required.

## 1. Choose the access path and check inputs

- Source code and permission to create a test DB: use the **HttpCase + headless Chrome add-on** below (default for a local Odoo project).
- Only a running test system: use the browser tool you were given to log in, navigate and capture. Still follow clean → annotate → capture → manifest; never swap DBs, install modules or create data on a production system.
- No suitable browser/environment/login: keep writing the parts that need no image, leave draft image placeholders and log the gap. Never substitute AI-made UI or claim images were captured.

Determine the Odoo version, compatible Python, addons paths (standard, Enterprise, custom), PostgreSQL connection config, language, the account you may use and a free HTTP port. Read the real code/UI before choosing selectors. Do not assume the system Python can run the project's Odoo.

From the Odoo source dir, preflight with Odoo's Python: `python -c "import odoo, psycopg2, websocket"`; check Chrome with `google-chrome --version`. Missing `websocket-client` makes browser tests skip silently: install it into a temp dir (`python -m pip install --target "$UG_WORK/pylib" websocket-client`) and add it to `PYTHONPATH` instead of modifying the Odoo environment. Exit code 0 is not proof that images exist.

## 2. Prepare the add-on and a private config

The template is `assets/odoo_userguide_capture/`. Replace the paths in the first block with the values you determined:

```bash
export UG_SKILL="/path/to/odoo-userguide-docx-writer"
export UG_ODOO_ROOT="/path/to/odoo-source"
export UG_PY="/path/to/odoo-compatible-python"
export UG_SOURCE_CONFIG="/path/to/existing-odoo.conf"
export UG_ADDONS_PATH="/path/addons,/path/enterprise,/path/customaddons"
export UG_WORK="$(mktemp -d /tmp/ug-capture.XXXXXX)"
export UG_CAPTURE_DB="ug_$(python3 -c 'import uuid; print(uuid.uuid4().hex[:12])')"
export UG_CAPTURE_OUTPUT="$UG_WORK/shots"
export UG_HTTP_PORT="8099"
mkdir -p "$UG_WORK/addons"
cp -R "$UG_SKILL/assets/odoo_userguide_capture" "$UG_WORK/addons/"
cp "$UG_SKILL/scripts/screenshot_annotations.js" "$UG_WORK/addons/odoo_userguide_capture/tests/annotations.js"
```

Take only the DB connection from the existing config; write a new config so nothing points at the real DB, filestore, cron or mail server:

```bash
python3 - <<'PY'
import configparser, os
from pathlib import Path
source = configparser.ConfigParser(interpolation=None)
assert source.read(os.environ['UG_SOURCE_CONFIG']), 'Cannot read source config'
work = Path(os.environ['UG_WORK'])
name = os.environ['UG_CAPTURE_DB']
assert name.startswith('ug_')
connection = {k: source['options'][k] for k in
              ('db_host', 'db_port', 'db_user', 'db_password', 'db_sslmode')
              if k in source['options']}
config = configparser.ConfigParser(interpolation=None)
config['options'] = dict(connection, db_name=name, dbfilter='^' + name + '$',
    addons_path=os.environ['UG_ADDONS_PATH'] + ',' + str(work/'addons'),
    data_dir=str(work/'data'), logfile=str(work/'odoo.log'),
    http_interface='127.0.0.1', http_port=os.environ['UG_HTTP_PORT'],
    max_cron_threads='0', workers='0', list_db='False')
path = work/'odoo.conf'
with path.open('w') as stream:
    config.write(stream)
path.chmod(0o600)
print('Temp config written; connection details not printed.')
PY
```

`UG_CAPTURE_DB` must be a fresh temp DB for this run. The runner refuses any other DB before seeding. Never put a production DB name here to save time.

## 3. Write the data and the frames

Edit the **copy** in `$UG_WORK/addons`, never Odoo core:

1. `__manifest__.py`: add the business/custom modules to `depends` **before creating the DB**, so images show the real system. The default `base, web` only serves the built-in examples.
2. `tests/test_capture.py`, `setUpClass`: it already renames admin to a natural name, sets `vi_VN`, sets login = password (required by `browser_js`) and hides the Enterprise trial-expiry banner on the temp DB. Add customers, owners, products and documents via ORM with natural names; fill required fields and set the right stage, rights and currency. Never edit the DOM to fake data.
3. `capture_steps(flow, url, frames, finish_js='', login=True)`: one **frame = one documented step or one “Kết quả” image**. `login=True` starts logged in as the seeded admin; `login=None` starts on the login page. Frame keys are documented at the top of `test_capture.py`:

| Key | Use |
| --- | --- |
| `id`, `section`, `instruction`, `phase` | Required; recorded in the manifest. Unique `id` per flow. |
| `target` | The element the step is about. |
| `prepare` | JS that reaches the state: click menus, fill fields. Use `await el(sel)`, `await until(fn, label)`, `await click(sel)`, `await paint()`; never a bare sleep while data loads. |
| `clip` + `pad` | Crop to the union of these selectors plus padding (card, menu, dialog). Widened automatically to include the arrow. |
| `no_union` | Keep the `clip` crop exactly (used with `box_only` or when the default crop would add half-cut neighbours). |
| `clean` | Only the clean image (overviews, “Kết quả”). |
| `box_only` | Thin frame, no arrow: target sits next to text. |
| `full` | Whole 1440×900 viewport. |
| `navigate` + `ready` | Action that loads a new page (login submit, logout, save-and-reload). The runner fires it, waits until `ready` exists on the new page, then reloads the helper. |

Built-in examples, verified on Odoo 20 with only `base, web`:

- `test_login_logout` (`login=None`): login page → fill Email → fill password → Đăng nhập → **real login** → home screen (result) → avatar → Đăng xuất → **real logout** → login page (result). 8 images.
- `test_preferences` (logged in): avatar → Tùy chọn của tôi → preferences dialog (result), closed through the UI.

Adapt URLs/selectors to the target version; do not assume they hold everywhere.

For each “Kết quả”, add a separate `phase='after'` frame with a clear ID (e.g. `result-create-record`), a wait for the completion sign and the result sentence. In Word use **`raw`** for clean images; use **`annotated`** only to point at a specific detail.

For “chọn Lưu”, the **before** image shows the Lưu button with valid data before the click. For “kiểm tra đã lưu”, really save in `prepare`, wait for the saved sign, then capture **after**. Never assign one overview capture to several different actions.

For create/edit flows, pass `finish_js` to save or discard **through the real UI**. Verify a claimed save via UI or ORM. The runner checks the web client's dirty/new-record markers before reporting success; re-check that mechanism on other versions. A DOM check is not proof of saving. Never send external email/notifications for an image.

Full page loads destroy the old JS context and overlay. Use `navigate` + `ready` instead of clicking inside `prepare`; never catch `Execution context was destroyed` and treat it as success.

## 4. Run Odoo and capture

Run from the Odoo source dir. Flags verified on Odoo 20; check `odoo-bin --help` for other versions:

```bash
cd "$UG_ODOO_ROOT"
PYTHONPATH="$UG_WORK/pylib" "$UG_PY" odoo-bin -c "$UG_WORK/odoo.conf" \
  -i odoo_userguide_capture --without-demo=True --load-language=vi_VN \
  --stop-after-init --no-http
UG_CAPTURE_DB="$UG_CAPTURE_DB" UG_CAPTURE_OUTPUT="$UG_CAPTURE_OUTPUT" \
PYTHONPATH="$UG_WORK/pylib" "$UG_PY" odoo-bin -c "$UG_WORK/odoo.conf" \
  --test-enable --test-tags /odoo_userguide_capture:TestGuideCapture \
  --screenshots="$UG_WORK/debug" --stop-after-init
grep -E "tests when loading|AssertionError" "$UG_WORK/odoo.log" | tail -3
```

The first command creates the DB and installs the declared dependencies (an "Importing test framework" ERROR line here is harmless). The second **needs HTTP**: `browser_js` logs in and opens pages through the server, so do not carry `--no-http` over. Success is `0 failed, 0 error(s)` plus the manifest, not the exit code.

Version-specific API: the runner uses `ChromeBrowser._wait_code_ok` and `_websocket_request`; Odoo 20 config params use `set_str` (older: `set_param`; the template handles both). If an API differs, read `odoo/tests/common.py` and adapt the runner copy; never patch the framework.

## 5. What the runner does per frame

1. Opens the URL (logged in or not), sets the viewport to **1440 × 900**, scale 1.
2. Runs `navigate` (wait for `ready`) or `prepare`, waits for the real target, waits for paint.
3. Loads `annotations.js`, computes the arrow and the crop (`clip`/`context`). The overlay is non-interactive and changes no Odoo value or button.
4. Hides the overlay and calls **`Page.captureScreenshot`** (`format='png'`, the crop) → clean PNG.
5. Unless `clean`, shows the overlay and captures the same crop → annotated PNG; a fresh browser capture, not an edited image.
6. Writes metadata, coordinates, URL and SHA256 of both images; clears the overlay.
7. Finishes the flow (`finish_js`), checks for unsaved forms and browser errors, then writes `manifest-<flow>.json`. On a failing frame it saves a full-viewport image in `debug/` and fails the test.

```python
encoded = browser._websocket_request('Page.captureScreenshot', params={
    'format': 'png', 'clip': shot['clip'], 'captureBeyondViewport': False,
})['data']
path.write_bytes(base64.b64decode(encoded))
```

Arrow: 2px shaft, 10 × 8px head, `markerUnits="userSpaceOnUse"`. Point at the exact button/field, never at empty space. Never cut labels or the arrow. Keep the crop to the relevant dialog/field group; mostly-empty images shrink the text in Word.

## 6. Check the output and put images into Word

```text
shots/
  login/
    raw/login-01-open.png ... logout-result.png
    annotated/<only non-clean frames>.png
    metadata/<id>.json
    debug/                       # failure images
  manifest-login.json
  preferences/ ...
  manifest-preferences.json
```

Each flow has its own folder, so equal IDs in different flows never overwrite; still use unique IDs across the whole document.

```bash
python3 - <<'PY'
import json, os
from pathlib import Path
out = Path(os.environ['UG_CAPTURE_OUTPUT'])
for manifest in sorted(out.glob('manifest-*.json')):
    rows = json.loads(manifest.read_text())
    for row in rows:
        for key in ('raw', 'annotated'):
            assert Path(row[key]).read_bytes().startswith(b'\x89PNG\r\n\x1a\n'), row['id']
    print(manifest.name, len(rows), 'frames OK')
PY
```

Then **look at every image** (full size or a sharp contact sheet) against its text: right screen, data, state, labels, arrow target; no spinner, error, banner or covered text. When changing the annotation helper, open `tests/annotations.html` in headless Chrome and expect `PASS`, plus the skill's Python tests. Keep the DB until images are final.

Copy images, manifest **and the adapted add-on** into a persistent project folder (e.g. `docs_local/user_guide_assets/<version>_<section>/`), so a later run can reuse the selectors instead of rediscovering them; `/tmp` does not survive reboots. In the DOCX pick images by **step/result ID**: `raw` when clear or for results, `annotated` only for hard-to-find targets. Insert right after the step or “Kết quả” paragraph with caption and alt text, keeping the scale rule from the Word reference. Never pick “the newest PNG” or rely on image order in the DOCX ZIP. Then run `link_section_refs.py`, `style_docx_images.py` and `check_docx.py` as in the Word reference.

## 7. Clean up

Wait for Odoo and Chrome to exit. Keep the used images/manifest until the DOCX embeds them. Drop only the temp DB created by this run, reading the temp config without printing connection details:

```bash
"$UG_PY" - <<'PY'
import configparser, os
from pathlib import Path
import psycopg2
from psycopg2 import sql
c = configparser.ConfigParser(interpolation=None)
c.read(Path(os.environ['UG_WORK'])/'odoo.conf')
o = c['options']
name = os.environ['UG_CAPTURE_DB']
assert name.startswith('ug_') and o['db_name'] == name
params = {'dbname': 'postgres'}
for key in ('host', 'port', 'user', 'password', 'sslmode'):
    value = o.get('db_' + key)
    if value and value.lower() not in ('false', 'none'):
        params[key] = value
conn = psycopg2.connect(**params)
conn.autocommit = True
with conn.cursor() as cur:
    cur.execute('SELECT pid FROM pg_stat_activity WHERE datname=%s', (name,))
    assert not cur.fetchall(), 'DB still in use; stop the server first'
    cur.execute(sql.SQL('DROP DATABASE {}').format(sql.Identifier(name)))
conn.close()
PY
```

## Common problems

| Symptom | Check / fix |
| --- | --- |
| DB selector page instead of Odoo | `db_name` and `dbfilter` must name the same temp DB; check port and URL. |
| Test ends without images | Chrome, websocket-client on `PYTHONPATH`, test tags, frame count, manifest; a skipped test is not a capture. |
| Button not found / selector timeout | Modules, role, language, version, record state, real DOM; fix the selector, never invent a button. |
| Right label, wrong element | Use a specific selector (e.g. `button.o_user_menu`, the table not the view switcher). |
| Spinner or stale values | Wait for the UI change with `until`, then `paint` before capturing. |
| “Database will expire” banner | Temp Enterprise DB only; the template sets `database.expiration_date`. Never show it in the guide. |
| `set_param` missing | Odoo 20 uses `set_str`; the template falls back automatically. |
| “Finish the flow by saving or discarding” | Save or discard through the UI in `finish_js`; claim a save only when verified. |
| Arrow tail or labels cut, tiny text | Adjust `clip`/`pad`; check the raw image; never stretch a small crop to hide a bad crop. |
| Arrow crosses neighbouring text | Use `box_only`, or a target/crop where the arrow has free space. |
| Want smaller arrows on old images | Recapture from clean images; never paint over the old arrow. |
