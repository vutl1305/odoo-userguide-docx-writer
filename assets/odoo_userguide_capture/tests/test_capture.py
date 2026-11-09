"""Temporary Odoo HttpCase example. See references/capture-workflow.md before running.

Copy screenshot_annotations.js into this tests/ directory as annotations.js.
Adapt depends, setUpClass, URL, selectors, and steps to the actual project.
Only run against a disposable ug_* DB explicitly named by UG_CAPTURE_DB.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import re
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
const paint = async () => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
'''

@tagged('post_install', '-at_install', 'userguide_capture')
class TestGuideCapture(HttpCase):
    browser_size = '1440x900'

    @classmethod
    def setUpClass(cls):
        expected = os.environ.get('UG_CAPTURE_DB', '')
        if not expected.startswith('ug_'):
            raise AssertionError('UG_CAPTURE_DB must name the disposable ug_* database created for this run')
        super().setUpClass()
        if cls.env.cr.dbname != expected:
            raise AssertionError('Refusing to seed a database other than UG_CAPTURE_DB')
        cls.env.ref('base.user_admin').write({
            'name': 'Nguyễn Minh Anh', 'lang': 'vi_VN', 'tz': 'Asia/Ho_Chi_Minh',
        })
        # Add only the realistic records required by the guide, via ORM, in this DB.

    def capture_steps(self, flow, url, frames, finish_js='', login='admin'):
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

        def run(browser, *args, **kwargs):
            browser._websocket_request('Emulation.setDeviceMetricsOverride', params={
                'width': 1440, 'height': 900, 'deviceScaleFactor': 1, 'mobile': False,
            })
            evaluate(browser, "await el('.o_web_client');" if login else "await el('input[name=login]');")
            browser._websocket_request('Runtime.evaluate', params={'expression': annotations})
            for frame in frames:
                step = frame['id']
                try:
                    setup = frame.get('prepare', '') + '\n'
                    setup += 'const target = await el(' + json.dumps(frame['target']) + ');'
                    setup += 'const context = ' + ('await el(' + json.dumps(frame['context']) + ')' if frame.get('context') else "target.closest('.modal-content')") + ';'
                    setup += 'await paint(); const shot = OdooUserGuide.annotate(target, {step:' + json.dumps(step) + ',context});'
                    setup += "document.getElementById('odoo-userguide-annotation').style.visibility='hidden';"
                    setup += 'await paint(); return {...shot,url:location.href,targetText:target.innerText||target.title||target.getAttribute("aria-label")||target.name||""};'
                    shot = evaluate(browser, setup)
                    raw, marked = output/'raw'/f'{step}.png', output/'annotated'/f'{step}.png'
                    raw_sha = png(browser, shot['clip'], raw)
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

    def test_preferences(self):
        # These are example selectors from the web client; verify them for the target version.
        self.capture_steps('preferences', '/odoo', [
            {'id': 's001', 'section': 'Tùy chọn cá nhân', 'phase': 'before',
             'instruction': 'Người dùng mở menu cá nhân.', 'target': '.o_user_menu'},
            {'id': 's002', 'section': 'Tùy chọn cá nhân', 'phase': 'before',
             'instruction': 'Người dùng chọn Tùy chọn của tôi.',
             'prepare': "await click('.o_user_menu');", 'target': '[data-menu=preferences]'},
            {'id': 's003', 'section': 'Tùy chọn cá nhân', 'phase': 'after',
             'instruction': 'Người dùng kiểm tra ngôn ngữ hiển thị.',
             'prepare': "await click('[data-menu=preferences]');await el('.modal .o_form_view');",
             'target': '.modal .o_field_widget[name=lang]'},
        ], finish_js="await click('.modal-header .btn-close');await until(()=>!document.querySelector('.modal'),'preferences closed');")
