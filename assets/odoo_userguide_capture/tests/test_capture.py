"""Disposable Odoo HttpCase that captures real user-guide screenshots.

Read references/capture-workflow.md first. Copy scripts/screenshot_annotations.js
next to this file as annotations.js. Adapt depends, setUpClass, URLs, selectors
and frames to the target project. Runs only on the database named by UG_CAPTURE_DB
(the DB the user chose or allowed, never production); writes to UG_CAPTURE_OUTPUT/<flow>/{raw,annotated,metadata,debug}.

Frame keys (one frame = one documented step or one "Kết quả" image):
  id, section, instruction, phase ('before'|'after')  required, recorded in manifest
  target      CSS selector of the element the step is about (required unless target_js)
  target_js   JS expression resolving to the element, e.g. byText('.dropdown-item', 'xoa', 'delete')
  prepare     JS run first to reach the state (click, fill); use el/until/click/paint
  context     selector whose box must stay inside the default crop
  clip        list of selectors; crop = union of their boxes + pad (default 24px)
  pad         padding for clip
  clip_rect   fixed crop {x, y, width, height} instead of clip
  min_h/max_h/max_w  clamp the crop height/width in px
  no_union    with clip: do not widen the crop to the annotation (box-only shots)
  clean       capture only the unannotated image (overviews, "Kết quả")
  box_only    thin frame around target, no arrow (target next to text)
  full        crop = whole 1440x900 viewport
  navigate    JS that triggers a full page load (login submit, logout, reload)
  ready       selector that proves the new page is usable (required with navigate)
  expect_error  allow a visible Odoo error dialog (only when the guide documents that message)
Never add silent fallbacks (`|| el(...)`, `if (btn)`): a missed target must fail the test.
Add new frame keys here, in the skill template, not in a per-project copy of capture_steps.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import time
from unittest.mock import patch

from odoo.tests import HttpCase, tagged
from odoo.tests.common import ChromeBrowser

HELPERS = r'''
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
const visible = e => !!(e && e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden');
const until = async (check, description) => {
  for (let i = 0; i < 150; i++) { const value = check(); if (value) return value; await pause(100); }
  throw new Error('Timed out: ' + description);
};
const el = async selector => until(() => [...document.querySelectorAll(selector)].find(visible), selector);
const click = async selector => {
  const element = await el(selector);
  if (element.disabled) throw new Error('Disabled control: ' + selector);
  element.click();
};
// Match a visible element by its label, ignoring Vietnamese accents and case
// (Odoo writes "Xoá" while people type "Xóa"). Fails when nothing matches.
const fold = t => (t || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/gi, 'd').toLowerCase().replace(/\s+/g, ' ').trim();
const byText = async (selector, ...labels) => until(() => [...document.querySelectorAll(selector)].filter(visible)
  .find(e => labels.some(l => fold(e.innerText || e.title || e.getAttribute('aria-label')).includes(fold(l)))),
  selector + ' with label ' + labels.join(' / '));
const paint = async () => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
'''

@tagged('post_install', '-at_install', 'userguide_capture')
class TestGuideCapture(HttpCase):
    browser_size = '1440x900'

    @classmethod
    def setUpClass(cls):
        expected = os.environ.get('UG_CAPTURE_DB', '')
        if not expected:
            raise AssertionError('Set UG_CAPTURE_DB to the capture database the user chose or allowed')
        super().setUpClass()
        if cls.env.cr.dbname != expected:
            raise AssertionError('Refusing to seed a database other than UG_CAPTURE_DB')
        # HttpCase.browser_js(login=X) authenticates with password X, so keep them equal.
        cls.login = cls.password = 'minhanh@example.vn'
        admin = cls.env.ref('base.user_admin')
        admin.write({'name': 'Nguyễn Minh Anh', 'lang': 'vi_VN', 'tz': 'Asia/Ho_Chi_Minh',
                     'login': cls.login, 'email': cls.login})
        admin.password = cls.password
        # Temp DB only: Enterprise shows a trial-expiry banner production does not have.
        icp = cls.env['ir.config_parameter'].sudo()
        set_param = getattr(icp, 'set_str', None) or icp.set_param  # Odoo 20: set_str
        set_param('database.expiration_date', '2099-12-31 00:00:00')
        set_param('database.expiration_reason', 'renewal')
        # Add only the realistic records the guide needs, via ORM, in this DB.

    def capture_steps(self, flow, url, frames, finish_js='', login=True):
        """login=True: seeded admin; None: start logged out (login page); or a login name."""
        login = self.login if login is True else login
        self.assertTrue(re.fullmatch(r'[A-Za-z0-9_-]{1,80}', flow), 'Use a safe flow name')
        base_output = Path(os.environ['UG_CAPTURE_OUTPUT']).resolve()
        output = base_output / flow
        for directory in ('raw', 'annotated', 'metadata', 'debug'):
            (output / directory).mkdir(parents=True, exist_ok=True)
        annotations = Path(__file__).with_name('annotations.js').read_text()
        original = ChromeBrowser._wait_code_ok
        rows = []
        identifiers = [frame['id'] for frame in frames]
        self.assertEqual(len(identifiers), len(set(identifiers)), 'Duplicate step ids in this flow')
        self.assertTrue(all(re.fullmatch(r'[A-Za-z0-9_-]{1,80}', s) for s in identifiers))

        def evaluate(browser, code):
            result = browser._websocket_request('Runtime.evaluate', params={
                'expression': '(async()=>{' + HELPERS + code + '})()',
                'awaitPromise': True, 'returnByValue': True,
            }, timeout=60)
            if result.get('exceptionDetails'):
                raise AssertionError(result['exceptionDetails'])
            return result.get('result', {}).get('value')

        def png(browser, clip, path):
            encoded = browser._websocket_request('Page.captureScreenshot', params={
                'format': 'png', 'clip': clip, 'captureBeyondViewport': False,
            })['data']
            data = base64.b64decode(encoded)
            self.assertTrue(data.startswith(b'\x89PNG\r\n\x1a\n'))
            path.write_bytes(data)
            return hashlib.sha256(data).hexdigest()

        def assert_no_odoo_error(browser, step):
            # Odoo error/warning dialogs (Oops/Rất tiếc, UserError...) must stop the capture, never be shot.
            msg = evaluate(browser, "const d=[...document.querySelectorAll('.o_error_dialog')].find(visible);return d?d.innerText.trim().slice(0,500):'';")
            if msg:
                raise AssertionError(f'Odoo shows an error dialog at step {step} - fix it, do not capture:\n{msg}')

        def run(browser, *args, **kwargs):
            browser._websocket_request('Emulation.setDeviceMetricsOverride', params={
                'width': 1440, 'height': 900, 'deviceScaleFactor': 1, 'mobile': False,
            })
            evaluate(browser, "await el('.o_web_client');" if login else "await el('input[name=login]');")
            browser._websocket_request('Runtime.evaluate', params={'expression': annotations})
            for frame in frames:
                step = frame['id']
                try:
                    if frame.get('navigate'):
                        evaluate(browser, "document.body.classList.add('ug_old_page');setTimeout(async()=>{" + frame['navigate'] + "},50);return true;")
                        for _ in range(200):
                            try:
                                if evaluate(browser, 'return !document.body.classList.contains("ug_old_page") && !!document.querySelector(' + json.dumps(frame['ready']) + ');'):
                                    break
                            except Exception:
                                pass
                            time.sleep(0.2)
                        else:
                            raise AssertionError('Navigation not ready: ' + step)
                        evaluate(browser, "await new Promise(r=>setTimeout(r,1500));")
                        browser._websocket_request('Runtime.evaluate', params={'expression': annotations})
                    setup = frame.get('prepare', '') + '\n'
                    if frame.get('target_js'):
                        setup += 'const target = await (' + frame['target_js'] + ');if(!target)throw new Error("target_js found nothing");'
                    else:
                        setup += 'const target = await el(' + json.dumps(frame['target']) + ');'
                    setup += 'const context = ' + ('await el(' + json.dumps(frame['context']) + ')' if frame.get('context') else "target.closest('.modal-content')") + ';'
                    setup += 'await paint(); const shot = OdooUserGuide.annotate(target, {step:' + json.dumps(step) + ',context});'
                    setup += "document.getElementById('odoo-userguide-annotation').style.visibility='hidden';"
                    setup += 'await paint(); return {...shot,url:location.href,targetText:target.innerText||target.title||target.getAttribute("aria-label")||target.name||""};'
                    shot = evaluate(browser, setup)
                    raw, marked = output/'raw'/f'{step}.png', output/'annotated'/f'{step}.png'
                    shot['annotate_clip'] = shot['clip']
                    if frame.get('clip_rect'):
                        shot['clip'] = {**frame['clip_rect'], 'scale': 1}
                    elif frame.get('clip'):
                        shot['clip'] = evaluate(browser, 'const r=' + json.dumps(frame['clip']) + '.flatMap(q=>[...document.querySelectorAll(q)].filter(visible)).map(e=>e.getBoundingClientRect());'
                            'const p=' + str(frame.get('pad', 24)) + ';const x=Math.max(0,Math.min(...r.map(b=>b.left))-p),y=Math.max(0,Math.min(...r.map(b=>b.top))-p);'
                            'return {x,y,width:Math.min(innerWidth,Math.max(...r.map(b=>b.right))+p)-x,height:Math.min(innerHeight,Math.max(...r.map(b=>b.bottom))+p)-y,scale:1};')
                        if not frame.get('clean') and not frame.get('no_union'):
                            a, c = shot['annotate_clip'], shot['clip']
                            x, y = min(a['x'], c['x']), min(a['y'], c['y'])
                            shot['clip'] = {'x': x, 'y': y, 'scale': 1,
                                'width': max(a['x'] + a['width'], c['x'] + c['width']) - x,
                                'height': max(a['y'] + a['height'], c['y'] + c['height']) - y}
                    clip = shot['clip']
                    if frame.get('min_h'):
                        clip['height'] = min(900 - clip['y'], max(clip['height'], frame['min_h']))
                    if frame.get('max_h'):
                        clip['height'] = min(clip['height'], frame['max_h'])
                    if frame.get('max_w'):
                        clip['width'] = min(clip['width'], frame['max_w'])
                    if frame.get('box_only'):
                        evaluate(browser, "document.querySelectorAll('#odoo-userguide-annotation path').forEach(e=>e.remove());")
                    if frame.get('full'):
                        shot['clip'] = {'x': 0, 'y': 0, 'width': 1440, 'height': 900, 'scale': 1}
                    if not frame.get('expect_error'):
                        assert_no_odoo_error(browser, step)
                    raw_sha = png(browser, shot['clip'], raw)
                    if frame.get('clean'):
                        marked, marked_sha = raw, raw_sha
                    else:
                        evaluate(browser, "document.getElementById('odoo-userguide-annotation').style.visibility='visible';await paint();")
                        marked_sha = png(browser, shot['clip'], marked)
                        self.assertNotEqual(raw_sha, marked_sha, 'Annotation did not change the captured pixels')
                    evaluate(browser, 'OdooUserGuide.clear();')
                    row = {key: frame[key] for key in ('id', 'section', 'instruction', 'phase')}
                    row.update(raw=str(raw), annotated=str(marked), raw_sha256=raw_sha,
                               annotated_sha256=marked_sha, **shot)
                    (output/'metadata'/f'{step}.json').write_text(json.dumps(row, ensure_ascii=False, indent=2))
                    rows.append(row)
                except Exception:
                    png(browser, {'x': 0, 'y': 0, 'width': 1440, 'height': 900, 'scale': 1}, output/'debug'/f'{step}-failure.png')
                    raise
            evaluate(browser, finish_js + "\nif(document.querySelector('.o_form_dirty,.o_form_status_indicator_new_record'))throw Error('Finish the flow by saving or discarding through the real UI');")
            # HttpCase still performs its console/error checks; never log success after a failed frame.
            return original(browser, "console.log('test successful');", 60)

        with patch.object(ChromeBrowser, '_wait_code_ok', run):
            self.browser_js(url, "console.log('test successful');", login=login, timeout=180)
        self.assertEqual(len(rows), len(frames))
        (base_output/f'manifest-{flow}.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2))

    def test_login_logout(self):
        """Real login and logout across page loads; selectors verified on Odoo 20."""
        card = 'form.oe_login_form'
        submit = card + ' button[type=submit].btn-primary'
        fill = "const e=await el('input[name=%s]');e.value=%r;e.dispatchEvent(new Event('input',{bubbles:true}));"
        login_crop = {'clip': [card], 'pad': 40}
        self.capture_steps('login', '/web/login', [
            {**login_crop, 'id': 'login-01-open', 'section': 'Đăng nhập', 'phase': 'before', 'clean': True,
             'instruction': 'Mở địa chỉ hệ thống.', 'target': card},
            {**login_crop, 'id': 'login-02-email', 'section': 'Đăng nhập', 'phase': 'before',
             'instruction': 'Nhập Email.', 'prepare': fill % ('login', self.login), 'target': 'input[name=login]'},
            {**login_crop, 'id': 'login-03-password', 'section': 'Đăng nhập', 'phase': 'before',
             'instruction': 'Nhập Mật khẩu.', 'prepare': fill % ('password', self.password),
             'target': '.input-group:has(input[name=password])'},
            {**login_crop, 'id': 'login-04-submit', 'section': 'Đăng nhập', 'phase': 'before',
             'instruction': 'Chọn Đăng nhập.', 'target': submit},
            {'id': 'login-result', 'section': 'Đăng nhập', 'phase': 'after', 'clean': True, 'full': True,
             'instruction': 'Kết quả: màn hình chính.', 'navigate': f"document.querySelector('{submit}').click();",
             'ready': '.o_web_client .o_main_navbar', 'target': '.o_main_navbar'},
            {'id': 'logout-01-avatar', 'section': 'Đăng xuất', 'phase': 'before', 'box_only': True, 'no_union': True,
             'clip': ['.o_main_navbar .o_menu_systray'], 'pad': 30,
             'instruction': 'Chọn ảnh đại diện.', 'target': 'button.o_user_menu'},
            {'id': 'logout-02-menu', 'section': 'Đăng xuất', 'phase': 'before', 'no_union': True,
             'clip': ['.o_main_navbar .o_menu_systray', '.o-dropdown--menu'], 'pad': 75,
             'instruction': 'Chọn Đăng xuất.', 'prepare': "await click('button.o_user_menu');",
             'target': '[data-menu=logout]'},
            {**login_crop, 'id': 'logout-result', 'section': 'Đăng xuất', 'phase': 'after', 'clean': True,
             'instruction': 'Kết quả: màn hình đăng nhập.', 'navigate': "document.querySelector('[data-menu=logout]').click();",
             'ready': 'input[name=login]', 'target': card},
        ], login=None)

    def test_preferences(self):
        """Already logged in (default login=True); dialog closed through the real UI."""
        self.capture_steps('preferences', '/odoo', [
            {'id': 'pref-01-avatar', 'section': 'Tùy chọn cá nhân', 'phase': 'before', 'box_only': True, 'no_union': True,
             'clip': ['.o_main_navbar .o_menu_systray'], 'pad': 30,
             'instruction': 'Mở menu cá nhân.', 'target': 'button.o_user_menu'},
            {'id': 'pref-02-menu', 'section': 'Tùy chọn cá nhân', 'phase': 'before', 'no_union': True,
             'clip': ['.o_main_navbar .o_menu_systray', '.o-dropdown--menu'], 'pad': 75,
             'instruction': 'Chọn Tùy chọn của tôi.', 'prepare': "await click('button.o_user_menu');",
             'target': '[data-menu=preferences]'},
            {'id': 'pref-result', 'section': 'Tùy chọn cá nhân', 'phase': 'after', 'clean': True,
             'clip': ['.modal-content'], 'pad': 16,
             'instruction': 'Kết quả: hộp thoại tùy chọn.',
             'prepare': "await click('[data-menu=preferences]');await el('.modal .o_form_view');",
             'target': '.modal .o_field_widget[name=lang]'},
        ], finish_js="await click('.modal-header .btn-close');await until(()=>!document.querySelector('.modal'),'preferences closed');")
