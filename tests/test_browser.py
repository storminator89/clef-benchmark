"""Opt-in genuine Chromium regression and screenshot capture; no model inference.

Not a unittest.TestCase: ordinary unittest discovery never launches a browser.
Run only where sandboxed Chromium and loopback access are already permitted.
See docs/BROWSER_GALLERY.md. Never retry a security denial with weaker settings.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
import re
import struct
import subprocess
import sys
import threading
from urllib.parse import urlsplit, urlencode

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = 'http://127.0.0.1:8765'
PLAYWRIGHT_VERSION = '1.62.0'
SUITES = {
    'insurance': ('insurance', 60, 10, False),
    'bank-support': ('bank-support', 80, 12, False),
    'general': ('benchmark', 120, 4, True),
    'finance': ('finance', 80, 4, True),
    'clean72': ('clean72', 72, 11, False),
    'clarification': ('clarification', 72, 8, False),
}
GALLERY = (
    ('insurance-workbench-light.png', 'Versicherungsdokument: Originaltext, Goldreferenz und gespeicherte Modellantwort'),
    ('bank-dashboard-light.png', 'Bank-Support: eigenständige Nenner für Anliegen, Priorität und nächsten Schritt'),
    ('custom-import-light.png', 'Privater Import: ausschließlich das mitgelieferte synthetische Beispiel, noch ohne Modellantwort'),
    ('custom-editor-light.png', 'Eigene Tests: Eingabe und optionale Goldlabels bearbeiten, keine simulierte Inferenz'),
    ('insurance-workbench-dark.png', 'Dieselbe echte Workbench im dunklen Design'),
    ('insurance-result-390.png', 'Smartphone mit 390 CSS-Pixeln: eigener Prüfbereich'),
)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def request_allowed(method, url):
    parsed = urlsplit(url)
    return (parsed.scheme == 'http' and parsed.netloc == '127.0.0.1:8765'
            and method in ('GET', 'HEAD') and parsed.path != '/api/infer')


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hashes(root=ROOT):
    paths = sorted(p for p in (root / 'web').rglob('*') if p.is_file())
    paths += [root / 'examples/custom_cases/support.json', root / 'tests/test_browser.py']
    return {p.relative_to(root).as_posix(): sha256(p) for p in paths}


def png_size(path):
    raw = path.read_bytes()
    require(raw[:8] == b'\x89PNG\r\n\x1a\n' and raw[12:16] == b'IHDR', f'Not a PNG: {path.name}')
    require(len(raw) > 32, f'Incomplete PNG: {path.name}')
    return struct.unpack('>II', raw[16:24])


def verify_artifact(output, root=ROOT):
    manifest = json.loads((output / 'manifest.json').read_text(encoding='utf-8'))
    require(manifest.get('status') == 'pass', 'This browser run did not pass; do not publish its images.')
    require(manifest.get('real_browser_rendering') is True, 'No successful genuine browser capture recorded.')
    require(manifest.get('model_inference_executed') is False, 'Gallery must not run new inference.')
    require(manifest.get('synthetic_inputs_only') is True, 'Gallery must contain only public synthetic inputs.')
    require(manifest.get('chromium_sandbox') is True, 'Sandbox-preserving capture required.')
    require(manifest.get('browser_channel') == 'chrome', 'Use the supported installed stable Chrome channel.')
    require(manifest.get('source_sha256') == source_hashes(root), 'Sources changed since capture. Run a new capture.')
    for field in ('page_errors', 'console_errors', 'blocked_requests', 'request_failures', 'http_errors'):
        require(manifest.get(field) == [], f'Run has unclean browser diagnostics: {field}')
    entries = {item['file']: item for item in manifest.get('screenshots', [])}
    require(len(entries) == len(manifest.get('screenshots', [])), 'Duplicate screenshot filenames.')
    require(all(name in entries for name, _ in GALLERY), 'Required gallery capture is missing.')
    for name, item in entries.items():
        require(Path(name).name == name and name.endswith('.png'), 'Unsafe screenshot filename.')
        path = output / 'screenshots' / name
        require(path.is_file() and not path.is_symlink(), f'Missing screenshot: {name}')
        require(sha256(path) == item['sha256'], f'Screenshot hash mismatch: {name}')
        require(list(png_size(path)) == item['image_pixels'], f'Screenshot dimensions changed: {name}')
    return manifest


def write_gallery_fragment(output):
    manifest = verify_artifact(output)
    lines = [
        '## Ein Blick in die Workbench', '',
        'Echte Google-Chrome-Screenshots (Chromium) aus dem modellfreien Browserlauf. Gezeigt werden ausschließlich',
        'synthetische Testdaten und bereits aufgezeichnete Benchmarkantworten. Der private Editor',
        'zeigt keine neue oder simulierte Modellinferenz.', '',
    ]
    for name, caption in GALLERY:
        lines.extend((f'### {caption}', '', f'![{caption}](docs/screenshots/{name})', ''))
    lines.extend((
        f"Aufnahme: {manifest['completed_utc']} · Chromium {manifest['chromium_version']} · Playwright {manifest['playwright_version']}.",
        'Quell- und Bildhashes sowie Viewport, Theme und Fall-ID stehen im',
        '[Aufnahmenachweis](docs/screenshots/manifest.json). Browserchecks sind keine neue Modellmessung.', '',
    ))
    # A .txt fragment cannot introduce broken Markdown links before its PNGs are copied.
    (output / 'README-GALLERY.txt').write_text('\n'.join(lines), encoding='utf-8')


@contextmanager
def local_server(start):
    """Own only the server created here. Never stop or reconfigure an existing one."""
    if not start:
        yield
        return
    sys.path.insert(0, str(ROOT))
    from server import Workbench, make_server
    server = make_server(8765, Workbench(False), ROOT / 'web')
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        yield
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)


class BrowserChecks:
    def __init__(self, page, output, manifest, expect):
        self.page, self.output, self.manifest, self.expect = page, output, manifest, expect
        self.datasets = {key: json.loads((ROOT / f'web/data/{spec[0]}.json').read_text()) for key, spec in SUITES.items()}
        self.example = json.loads((ROOT / 'examples/custom_cases/support.json').read_text())

    def check(self, description):
        self.manifest['checks'].append(description)
        print(f'PASS: {description}', flush=True)

    def nav(self, name):
        self.page.locator(f'[data-nav="{name}"]').click()
        self.expect(self.page.locator('#' + name)).to_be_visible()

    def suite(self, name):
        self.nav('explorer')
        self.page.locator('#suite-select').select_option(name)
        self.expect(self.page.locator('#suite-select')).to_have_value(name)
        self.expect(self.page.locator('.case-item')).to_have_count(SUITES[name][1])

    def overflow(self, label):
        result = self.page.evaluate('''() => {
          const width = document.documentElement.clientWidth;
          return {width, scrollWidth: document.documentElement.scrollWidth,
            offenders: [...document.querySelectorAll('body *')].filter(el => {
              const r = el.getBoundingClientRect(), s = getComputedStyle(el);
              return r.width && r.height && s.visibility !== 'hidden' &&
                (r.right > width + 1 || r.left < -1) && !el.closest('pre, textarea, .case-list');
            }).slice(0, 12).map(el => ({tag: el.tagName, id: el.id, class: el.className}))};
        }''')
        require(result['scrollWidth'] <= result['width'] + 1, f'{label}: viewport overflow: {result}')

    def capture(self, name, caption, *, full_page=True):
        page = self.page
        self.overflow(name)
        page.evaluate('document.fonts.ready')
        page.evaluate('() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))')
        page.evaluate('window.scrollTo({top: 0, left: 0, behavior: "instant"})')
        path = self.output / 'screenshots' / name
        # This call, not a mockup/image generator, is the only writer of gallery PNGs.
        page.screenshot(path=str(path), full_page=full_page, animations='disabled', caret='hide')
        self.manifest['real_browser_rendering'] = True
        self.manifest['screenshots'].append({
            'file': name, 'caption': caption, 'sha256': sha256(path),
            'image_pixels': list(png_size(path)), 'viewport_css_pixels': page.viewport_size,
            'device_scale_factor': 1, 'full_page': full_page,
            'route': urlsplit(page.url).fragment,
            'theme': page.locator('html').get_attribute('data-theme'),
            'selected_case': page.locator('[data-case][aria-pressed="true"]').get_attribute('data-case')
                if page.locator('[data-case][aria-pressed="true"]').count() else None,
            'custom_case': page.locator('#custom-case-id').text_content(),
            'content_kind': 'synthetic_private_input_without_inference' if page.locator('#custom').is_visible() else 'public_synthetic_benchmark_or_results_only_editor',
            'new_inference': False,
        })

    def initial_and_insurance(self):
        page, expect = self.page, self.expect
        page.goto(BASE_URL, wait_until='networkidle')
        expect(page.locator('.case-item')).to_have_count(60)
        expect(page.locator('#app-error')).to_be_hidden()
        expect(page.locator('#suite-select')).to_have_value('insurance')
        expect(page.locator('[data-field]')).to_have_count(2)
        require(page.locator('.document-section').count() > 0, 'Insurance document missing.')
        self.capture('insurance-workbench-light.png', 'Insurance document, independently recorded answers, light theme')
        page.locator('#theme-toggle').click()
        expect(page.locator('html')).to_have_attribute('data-theme', 'dark')
        page.reload(wait_until='networkidle')
        expect(page.locator('.case-item')).to_have_count(60)
        expect(page.locator('html')).to_have_attribute('data-theme', 'dark')
        self.capture('insurance-workbench-dark.png', 'Same insurance workbench in persisted dark theme')
        page.locator('#theme-toggle').click()
        page.locator('[data-case="fall_002"]').click()
        page.locator('[data-field="evidence"]').click()
        page.locator('[data-evidence="gold"]').click()
        require(page.locator('.highlight-gold').count() > 0, 'Gold evidence did not highlight.')
        page.locator('#highlight-select').select_option('none')
        expect(page.locator('.highlight-gold,.highlight-model,.highlight-both')).to_have_count(0)
        page.locator('#search').fill('not-a-real-case-xyz')
        expect(page.locator('.case-item')).to_have_count(0)
        expect(page.locator('.document-section')).to_have_count(0)
        expect(page.locator('#open-playground')).to_be_disabled()
        page.locator('#reset-filters').click()
        expect(page.locator('.case-item')).to_have_count(60)
        self.check('Insurance document, evidence navigation, empty-filter clearing/reset, persisted dark theme')

    def replay(self, suite, case_id, fields):
        page, expect = self.page, self.expect
        self.suite(suite)
        page.locator(f'[data-case="{case_id}"]').click()
        page.locator('#open-playground').click()
        expect(page.locator('#playground')).to_be_visible()
        expect(page.locator('#run-live')).to_be_disabled()
        expect(page.locator('#show-saved')).to_be_enabled()
        page.locator('#show-saved').click()
        expect(page.locator('[data-output-field]')).to_have_count(fields)
        expect(page.locator('#output-kind')).to_have_text('Gespeicherte Inferenz')
        original = page.locator('#input-state').input_value()
        schema_text = page.locator('#input-schema').input_value()
        page.locator('#input-state').fill(original + ' Bearbeitet.')
        expect(page.locator('#show-saved')).to_be_disabled()
        expect(page.locator('[data-output-field]')).to_have_count(0)
        page.locator('#input-state').fill(original)
        expect(page.locator('#show-saved')).to_be_enabled()
        questions = json.loads(schema_text)
        page.locator('#input-schema').fill(json.dumps(dict(reversed(list(questions.items()))), ensure_ascii=False))
        expect(page.locator('#show-saved')).to_be_disabled()
        page.locator('#input-schema').fill('{')
        expect(page.locator('#show-saved')).to_be_disabled()
        page.locator('#input-schema').fill(schema_text)
        expect(page.locator('#show-saved')).to_be_enabled()
        page.locator('#new-request').click()
        expect(page.locator('#show-saved')).to_be_disabled()
        expect(page.locator('[data-output-field]')).to_have_count(0)
        self.check(f'{suite}: recorded {fields}-field replay; text, question-order and malformed-schema invalidation')

    def all_suites_and_navigation(self):
        page, expect = self.page, self.expect
        self.nav('explorer')
        page.locator('#suite-catalog > summary').click()
        expect(page.locator('[data-suite]')).to_have_count(6)
        page.locator('[data-suite="bank-support"]').click()
        expect(page.locator('#suite-select')).to_have_value('bank-support')
        expect(page.locator('#suite-catalog')).not_to_have_attribute('open', '')
        for suite, (_, count, errors, paired) in SUITES.items():
            self.suite(suite)
            expect(page.locator('.case-item')).to_have_count(count)
            page.locator('#filter-outcome').select_option('errors')
            expect(page.locator('.case-item')).to_have_count(errors)
            page.locator('#reset-filters').click()
            page.locator('#filter-split').select_option('')
            expect(page.locator('.case-item')).to_have_count(len(self.datasets[suite]['cases']))
            page.locator('#reset-filters').click()
            self.nav('overview')
            expect(page.locator('#study-count')).to_have_text(str(count))
            require(page.locator('#paired-panel').is_visible() == paired, f'{suite}: incorrect paired comparison visibility')
        self.suite('bank-support')
        expect(page.locator('[data-field]')).to_have_count(3)
        self.capture('bank-workbench-light.png', 'Bank support: synthetic message and three recorded response fields')
        self.nav('overview')
        for metric in ('76 / 80', '77 / 80', '75 / 80', '68 / 80'):
            expect(page.locator('#stats')).to_contain_text(metric)
        self.capture('bank-dashboard-light.png', 'Separate bank-support denominators and honest recorded results')
        page.goto(BASE_URL + '/#explorer?suite=general&case=en_it_routing_003&field=decision', wait_until='networkidle')
        expect(page.locator('#filter-split')).to_have_value('english_control')
        expect(page.locator('[data-case="en_it_routing_003"]')).to_have_attribute('aria-pressed', 'true')
        self.nav('playground')
        self.nav('method')
        page.go_back()
        expect(page.locator('#playground')).to_be_visible()
        page.go_forward()
        expect(page.locator('#method')).to_be_visible()
        self.suite('insurance')
        first = page.locator('[data-case]').nth(0)
        second_id = page.locator('[data-case]').nth(1).get_attribute('data-case')
        first.focus()
        page.keyboard.press('ArrowDown')
        expect(page.locator(f'[data-case="{second_id}"]')).to_be_focused()
        expect(page.locator(f'[data-case="{second_id}"]')).to_have_attribute('aria-pressed', 'true')
        page.keyboard.press('ArrowUp')
        expect(first).to_be_focused()
        page.keyboard.press('/')
        expect(page.locator('#search')).to_be_focused()
        page.locator('#theme-toggle').focus()
        prior = page.locator('html').get_attribute('data-theme')
        page.keyboard.press('Enter')
        require(page.locator('html').get_attribute('data-theme') != prior, 'Theme button is not keyboard-operable.')
        page.keyboard.press('Enter')
        self.check('All six suite denominators/errors, language controls, three bank fields, deep links, Back/Forward and keyboard')

    def clarification(self):
        page, expect = self.page, self.expect
        self.suite('clarification')
        case = self.datasets['clarification']['cases'][0]
        for text in (case['rule'], case['message'], case['question']):
            expect(page.locator('#document-content')).to_contain_text(text)
        expect(page.locator('[data-field]')).to_have_count(2)
        expect(page.locator('#inspection-header')).to_contain_text('Inkonsistente Felder')
        expect(page.locator('.question-title')).to_have_text('Welcher nächste Schritt ist angemessen?')
        expect(page.locator('.field-schema pre')).to_contain_text(case['questions']['action']['instructions'])
        self.capture('clarification-workbench-light.png', 'Clarification72: complete fictional rule, question and preserved inconsistent model fields')
        for choice, count in [('action', 7), ('determination', 6), ('diagnostic:missed_required_clarifications', 4), ('diagnostic:excess_clarifications', 2), ('diagnostic:inconsistent_fields', 3), ('diagnostic:risky_wrong_answers', 4)]:
            page.locator('#filter-outcome').select_option(choice)
            expect(page.locator('.case-item')).to_have_count(count)
        page.locator('#reset-filters').click()
        self.nav('overview')
        for metric in ('65 / 72', '66 / 72', '64 / 72', '72 / 72'):
            expect(page.locator('#stats')).to_contain_text(metric)
        for metric in ('4 / 36', '2 / 36', '3 / 72', '4 / 37', 'nur 5'):
            expect(page.locator('#diagnosis-content')).to_contain_text(metric)
        self.capture('clarification-dashboard-light.png', 'Clarification72: separate scores, balanced denominators and confidence limitations')
        for width in (320, 390):
            page.set_viewport_size({'width': width, 'height': 844})
            self.nav('overview')
            self.overflow(f'clarification overview {width}')
            self.suite('clarification')
            for pane in ('cases', 'document', 'result'):
                page.locator(f'[data-pane="{pane}"]').click()
                self.overflow(f'clarification {pane} {width}')
            self.capture(f'clarification-result-{width}.png', f'Clarification72 recorded inconsistent response at {width} CSS pixels', full_page=False)
        page.set_viewport_size({'width': 1440, 'height': 1000})
        self.check('clarification72: complete source context, two native fields, error subtypes, honest denominators, 320/390px panels')

    def minimal_pairs(self):
        page, expect = self.page, self.expect
        self.nav('pairs')
        expect(page.locator('[data-pair]')).to_have_count(24)
        expect(page.locator('.pair-endpoint')).to_have_count(2)
        expect(page.locator('.pair-message mark')).to_have_count(2)
        expect(page.locator('.context-bar')).to_be_hidden()
        expect(page.locator('#pairs')).to_contain_text('17')
        expect(page.locator('#pair-detail')).to_contain_text('Laufende Überweisungsnummer 3 → 4')
        self.capture('minimal-pairs-comparison-light.png', 'Minimal pair: exactly one changed span, shared fictional rule and both native responses')
        page.locator('#pair-outcome').select_option('errors')
        expect(page.locator('[data-pair]')).to_have_count(7)
        page.locator('#pair-outcome').select_option('stable-wrong')
        expect(page.locator('[data-pair]')).to_have_count(2)
        page.locator('[data-pair="pair_report_delivery_target"]').click()
        expect(page.locator('#pair-detail')).to_contain_text('zweimal falsch')
        expect(page.locator('[data-pair="pair_report_delivery_target"]')).to_be_focused()
        expect(page.locator('.pair-field.bad')).to_have_count(4)
        self.capture('minimal-pairs-stable-wrong-light.png', 'Invariant report-title edit: two high-scoring wrong native endpoints remain visible')
        page.locator('#pair-search').fill('no-existing-pair-matches-xyz')
        expect(page.locator('[data-pair]')).to_have_count(0)
        expect(page.locator('.pair-endpoint')).to_have_count(0)
        page.locator('#pair-reset').click()
        expect(page.locator('[data-pair]')).to_have_count(24)
        page.locator('#pair-outcome').select_option('unjustified')
        expect(page.locator('[data-pair]')).to_have_count(1)
        expect(page.locator('#pair-detail')).to_contain_text('ungültige Preisstufe')
        page.goto(BASE_URL + '/#pairs?pair=pair_gadget_theft_notice', wait_until='networkidle')
        expect(page.locator('#pair-detail')).to_contain_text('Inkonsistente Feldkombination')
        page.locator('.pair-raw > summary').first.click()
        expect(page.locator('.pair-raw').first).to_have_attribute('open', '')
        page.locator('#theme-toggle').click()
        self.capture('minimal-pairs-comparison-dark.png', 'Preserved inconsistent boundary response and full native option scores in dark theme')
        page.locator('#theme-toggle').click()
        self.nav('method')
        page.go_back()
        expect(page.locator('#pairs')).to_be_visible()
        expect(page.locator('#pair-detail')).to_contain_text('Meldeabstand 48 → 49 Stunden')
        page.go_forward()
        expect(page.locator('#method')).to_be_visible()
        for width in (320, 390):
            page.set_viewport_size({'width': width, 'height': 844})
            self.nav('pairs')
            expect(page.locator('[data-pair]')).to_have_count(24)
            self.overflow(f'minimal pairs {width}')
            page.locator('#pair-outcome').select_option('stable-wrong')
            page.locator('[data-pair="pair_report_delivery_target"]').click()
            self.overflow(f'minimal pairs stable-wrong {width}')
            self.capture(f'minimal-pairs-{width}.png', f'Pair comparison at {width} CSS pixels, unchanged wrong endpoints', full_page=True)
            page.locator('#pair-reset').click()
        page.set_viewport_size({'width': 1440, 'height': 1000})
        self.check('Minimal pairs: exact highlighted edits, paired correctness, stable-wrong and unjustified-change filters, no-match clearing, deep links, Back/Forward, dark theme and 320/390px')

    def reliability(self):
        page, expect = self.page, self.expect
        page.goto(BASE_URL + '/#reliability', wait_until='networkidle')
        expect(page.locator('#reliability-suite')).to_have_value('minimal_pairs48')
        expect(page.locator('#reliability-field')).to_have_value('determination')
        expect(page.locator('.reliability-risk')).to_contain_text('4 / 36')
        expect(page.locator('[data-reliability-bin]')).to_have_count(10)
        expect(page.locator('[data-reliability-error]')).to_have_count(6)
        self.capture('reliability-determination-light.png', 'Minimal-pair determination: fixed threshold 0.90, four errors among 36 selected and separate coverage', full_page=False)
        page.locator('#reliability-field').select_option('action')
        expect(page.locator('.reliability-risk')).to_contain_text('2 / 7')
        expect(page.locator('.reliability-caveats')).to_contain_text('Beide Fehler gehören zum selben Paar')
        page.locator('#reliability-selected-errors').check()
        expect(page.locator('[data-reliability-error]')).to_have_count(2)
        page.locator('[data-reliability-error] summary').first.click()
        expect(page.locator('.reliability-evidence').first).to_be_visible()
        page.locator('#theme-toggle').click()
        self.capture('reliability-action-dark.png', 'Dependent high-score action errors, original input and complete unrounded native option evidence')
        page.locator('#theme-toggle').click()
        # Every field group is inspected separately; the test never pools probabilities.
        source = json.loads((ROOT / 'web/data/reliability.json').read_text())
        for group in source['field_groups']:
            query = urlencode({'suite': group['suite_id'], 'field': group['field'], 'group': group['group_id'], 'threshold': '.90'})
            page.evaluate('(hash) => { location.hash = hash; }', '#reliability?' + query)
            expect(page.locator('#reliability-group')).to_have_value(group['group_id'])
            row = next(r for r in group['risk_coverage'] if r['threshold'] == .9)
            expect(page.locator('.reliability-risk')).to_contain_text(f"{row['incorrect']} / {row['selected_count']}")
            expect(page.locator('[data-reliability-bin]')).to_have_count(10)
            if group['suite_id'] == 'images90' and group['partition']['condition'] == 'blank':
                expect(page.locator('.reliability-caveats')).to_contain_text('BLANK-DIAGNOSTIK')
            if group['suite_id'] == 'images90' and group['partition']['kind'] == 'chart':
                expect(page.locator('.reliability-caveats')).to_contain_text('bar_line/vbar2')
        page.goto(BASE_URL + '/#reliability?suite=minimal_pairs48&field=action&threshold=.99', wait_until='networkidle')
        expect(page.locator('[data-reliability-risk]')).to_have_text('nicht definiert')
        expect(page.locator('.reliability-risk')).to_contain_text('0/0 ist nicht definiert')
        page.locator('#reliability-suite').select_option('clarification72')
        page.locator('#reliability-field').select_option('determination')
        page.locator('#reliability-threshold').select_option('0.9')
        expect(page.locator('.reliability-risk')).to_contain_text('0 / 49')
        expect(page.locator('.reliability-caveats')).to_contain_text('keine')
        for width in (320, 390):
            page.set_viewport_size({'width': width, 'height': 844})
            page.locator('#reliability-suite').select_option('minimal_pairs48')
            page.locator('#reliability-field').select_option('determination')
            expect(page.locator('.reliability-risk')).to_contain_text('4 / 36')
            self.overflow(f'reliability {width}')
            self.capture(f'reliability-{width}.png', f'Separate field risk, coverage and bin evidence at {width} CSS pixels', full_page=True)
            page.locator('#reliability-metrics > summary').click()
            page.locator('#reliability-method > summary').click()
            self.overflow(f'reliability expanded definitions {width}')
            page.locator('#reliability-metrics > summary').click()
            page.locator('#reliability-method > summary').click()
        page.set_viewport_size({'width': 1440, 'height': 1000})
        self.check('Reliability: all 78 separate field groups, exact fixed-threshold risk/coverage, dependent error evidence, image/blank caveats, undefined empty risk, dark theme and 320/390px')

    def readiness(self):
        page, expect = self.page, self.expect
        self.nav('playground')
        expect(page.locator('#run-live')).to_be_disabled()
        expect(page.locator('#backend-readiness')).to_be_visible()
        expect(page.locator('#backend-summary')).to_contain_text('Ergebnismodus')
        expect(page.locator('[data-readiness]')).to_have_count(3)
        expect(page.locator('[data-readiness="0"]')).to_have_attribute('data-status', 'ready')
        for step in ('1', '2'):
            expect(page.locator(f'[data-readiness="{step}"]')).to_have_attribute('data-status', 'pending')
        with page.expect_response(lambda response: urlsplit(response.url).path == '/api/health') as event:
            page.locator('#refresh-backend').click()
        health = event.value.json()
        require(health['inference_enabled'] is False and health['model_loaded'] is False, 'Capture requires the real results-only backend.')
        expect(page.locator('#run-live')).to_be_disabled()
        self.capture('backend-readiness-light.png', 'Actual results-only backend; server reachability is not model readiness')
        self.check('Real disabled backend, explicit health refresh and honest readiness; no fabricated ready state')

    def open_import(self):
        box = self.page.locator('#custom-import-box')
        if box.get_attribute('open') is None:
            box.locator('summary').first.click()

    def import_example(self, *, screenshot=False):
        page, expect = self.page, self.expect
        self.nav('custom')
        self.open_import()
        page.locator('#custom-file').set_input_files(str(ROOT / 'examples/custom_cases/support.json'))
        page.locator('#custom-parse').click()
        expect(page.locator('#custom-preview')).to_be_visible()
        expect(page.locator('#custom-preview-list li')).to_have_count(3)
        expect(page.locator('#custom-preview-copy')).to_contain_text('3 gültige Fälle')
        if screenshot:
            self.capture('custom-import-light.png', 'Validated public synthetic support example; nothing sent to a model')
        page.locator('#custom-accept').click()
        expect(page.locator('#custom-workspace')).to_be_visible()
        expect(page.locator('[data-custom-case]')).to_have_count(3)
        expect(page.locator('[data-custom-answer]')).to_have_count(0)
        expect(page.locator('#custom-case-result')).to_contain_text('Keine Modellantwort')
        expect(page.locator('#custom-run')).to_be_disabled()
        with page.expect_response(lambda response: urlsplit(response.url).path == '/api/health'):
            page.locator('#custom-refresh-backend').click()
        expect(page.locator('#custom-backend-summary')).to_contain_text('Ergebnismodus')
        expect(page.locator('#custom-run')).to_be_disabled()

    def custom_import_edit_export(self):
        page, expect = self.page, self.expect
        self.import_example(screenshot=True)
        self.capture('custom-editor-light.png', 'Private editor showing only the bundled synthetic case, without predictions')
        original = page.locator('#custom-state').input_value()
        page.locator('#custom-state').fill(original + ' Zusatz für Browserregression.')
        expect(page.locator('#custom-export-suite')).to_be_disabled()
        expect(page.locator('[data-custom-answer]')).to_have_count(0)
        page.locator('#custom-discard').click()
        expect(page.locator('#custom-state')).to_have_value(original)
        # The schema and gold fields are inside the editor's disclosure.
        if not page.locator('#custom-questions').is_visible():
            page.locator('#custom-editor details > summary').click()
        page.locator('#custom-gold').fill('{"intent":"unknown_label"}')
        page.locator('#custom-apply').click()
        expect(page.locator('#custom-message')).to_have_class(re.compile(r'.*error.*'))
        expect(page.locator('#custom-export-suite')).to_be_disabled()
        page.locator('#custom-discard').click()
        edited = original + ' Synthetischer Zusatz für Browserregression.'
        page.locator('#custom-state').fill(edited)
        page.locator('#custom-apply').click()
        expect(page.locator('#custom-export-suite')).to_be_enabled()
        expect(page.locator('#custom-export-json')).to_be_disabled()
        expect(page.locator('#custom-export-csv')).to_be_disabled()
        with page.expect_download() as event:
            page.locator('#custom-export-suite').click()
        download = event.value
        require(download.suggested_filename == 'clef-private-suite.json', 'Unexpected suite download name.')
        exported = json.loads(Path(download.path()).read_text(encoding='utf-8'))
        require(exported['cases'][0]['state'] == edited, 'Export did not preserve the edited input.')
        require(exported['cases'][0]['gold'] == self.example['cases'][0]['gold'], 'Export changed gold labels.')
        require(len(exported['cases']) == 3 and 'results' not in exported, 'Export invented responses or lost cases.')
        # Real browser file selection also covers JSONL and CSV parsers, without network upload.
        for name, mime, content in (
            ('synthetic.jsonl', 'application/x-ndjson', '\n'.join(json.dumps(c, ensure_ascii=False) for c in self.example['cases'])),
            ('synthetic.csv', 'text/csv', 'id,state,gold.intent,gold.priority\nsynthetic_csv,Mein Passwort ist vergessen,zugang,normal\n'),
        ):
            self.open_import()
            page.locator('#custom-file').set_input_files({'name': name, 'mimeType': mime, 'buffer': content.encode()})
            page.locator('#custom-parse').click()
            expect(page.locator('#custom-preview')).to_be_visible()
            expect(page.locator('#custom-accept')).to_be_enabled()
        page.locator('#custom-example').click()
        page.locator('#custom-accept').click()
        expect(page.locator('#custom-confirm')).to_be_visible()
        expect(page.locator('#custom-state')).to_have_value(edited)
        page.locator('#custom-confirm-cancel').click()
        expect(page.locator('#custom-state')).to_have_value(edited)
        page.locator('#custom-accept').click()
        page.locator('#custom-confirm-action').click()
        expect(page.locator('[data-custom-case]')).to_have_count(3)
        expect(page.locator('#custom-state')).to_have_value(original)
        page.locator('#custom-search').fill('no-synthetic-case-matches')
        expect(page.locator('[data-custom-case]')).to_have_count(0)
        page.locator('[data-custom-reset]').click()
        expect(page.locator('#custom-search')).to_have_value('')
        expect(page.locator('[data-custom-case]')).to_have_count(3)
        for filter_value, count in (('unlabelled', 2), ('pending', 3), ('error', 0), ('wrong', 0), ('all', 3)):
            page.locator('#custom-filter').select_option(filter_value)
            expect(page.locator('[data-custom-case]')).to_have_count(count)
        page.locator('#custom-clear').click()
        expect(page.locator('#custom-confirm')).to_be_visible()
        page.locator('#custom-confirm-cancel').click()
        expect(page.locator('#custom-workspace')).to_be_visible()
        page.locator('#custom-clear').click()
        page.locator('#custom-confirm-action').click()
        expect(page.locator('#custom-workspace')).to_be_hidden()
        expect(page.locator('#custom-empty')).to_be_visible()
        self.check('Actual JSON/JSONL/CSV file input, preview/accept, invalid gold rejection, edit/discard, JSON download, search/status filters, replace/clear confirmations with cancel')

    def phones(self):
        page, expect = self.page, self.expect
        self.import_example()
        for width in (390, 320):
            page.set_viewport_size({'width': width, 'height': 844})
            self.suite('insurance')
            for pane in ('cases', 'document', 'result'):
                page.locator(f'[data-pane="{pane}"]').click()
                expect(page.locator('#workbench-shell')).to_have_attribute('data-mobile-pane', pane)
                self.capture(f'insurance-{pane}-{width}.png', f'Insurance {pane} panel at {width} CSS pixels', full_page=False)
            for suite in SUITES:
                self.suite(suite)
                for pane in ('cases', 'document', 'result'):
                    page.locator(f'[data-pane="{pane}"]').click()
                    self.overflow(f'{width}px {suite} {pane}')
                for view in ('overview', 'playground', 'method'):
                    self.nav(view)
                    self.overflow(f'{width}px {suite} {view}')
            self.suite('bank-support')
            self.nav('overview')
            self.capture(f'bank-dashboard-{width}.png', f'Bank support dashboard at {width} CSS pixels')
            self.nav('custom')
            self.capture(f'custom-editor-{width}.png', f'Synthetic private editor at {width} CSS pixels')
            self.open_import()
            self.overflow(f'{width}px custom expanded import')
            # Native select intrinsic widths must not grow the nested label grid.
            # Cover the long format options and the conditionally visible CSV preset.
            for format_value in ('auto', 'csv', 'jsonl'):
                page.locator('#custom-format').select_option(format_value)
                controls = ['custom-format'] + (['custom-preset'] if format_value == 'csv' else [])
                for control_id in controls:
                    control = page.locator('#' + control_id)
                    expect(control).to_be_visible()
                    control.focus()
                    expect(control).to_be_focused()
                    bounds = control.evaluate('''el => {
                      const field = el.getBoundingClientRect();
                      const label = el.closest('label').getBoundingClientRect();
                      return {left: field.left, right: field.right, width: field.width,
                        height: field.height, labelLeft: label.left, labelRight: label.right};
                    }''')
                    require(bounds['width'] > 0 and bounds['height'] >= 35 and
                            bounds['left'] >= bounds['labelLeft'] - 1 and
                            bounds['right'] <= bounds['labelRight'] + 1,
                            f'{width}px {control_id} escapes its label: {bounds}')
                self.overflow(f'{width}px custom expanded import, format {format_value}')
            page.locator('#custom-format').select_option('auto')
            page.locator('#custom-import-box > summary').click()
            self.check(f'{width}px: all suites, three workbench panes, overview/live/method/private editor without horizontal overflow')
        page.set_viewport_size({'width': 1440, 'height': 1000})


def capture_run(output, start_server):
    require(not output.exists() or not any(output.iterdir()), 'Output must be new or empty; never mix old screenshots into a run.')
    output.mkdir(parents=True, exist_ok=True)
    (output / 'screenshots').mkdir()
    manifest = {
        'schema_version': 1, 'status': 'running', 'started_utc': datetime.now(timezone.utc).isoformat(),
        'source_sha256': source_hashes(), 'python_version': platform.python_version(),
        'os': platform.system(), 'architecture': platform.machine(), 'base_url': BASE_URL,
        'git_commit': None, 'workflow_run_url': None, 'chromium_sandbox': True,
        'browser_channel': 'chrome', 'browser_application': 'Google Chrome',
        'real_browser_rendering': False, 'model_inference_executed': False, 'synthetic_inputs_only': True,
        'page_errors': [], 'console_errors': [], 'blocked_requests': [], 'request_failures': [], 'http_errors': [],
        'checks': [], 'screenshots': [],
    }
    # Fixed, non-secret provenance only; never dump environment variables or local absolute paths.
    import os
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        manifest['git_commit'] = os.environ.get('GITHUB_SHA')
        manifest['workflow_run_url'] = f"{os.environ['GITHUB_SERVER_URL']}/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}"
    else:
        try:
            result = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], capture_output=True, text=True, check=False)
            manifest['git_commit'] = result.stdout.strip() if result.returncode == 0 else None
        except OSError:
            pass  # A source-hashed local capture can be reviewed without Git installed.
    context = browser = None
    try:
        manifest['playwright_version'] = version('playwright')
        require(manifest['playwright_version'] == PLAYWRIGHT_VERSION, 'Install the version pinned in tests/requirements-browser.txt.')
        from playwright.sync_api import expect, sync_playwright
        with local_server(start_server), sync_playwright() as playwright:
            # Use the documented installed stable channel and its existing sandbox policy.
            # No executable override, custom flags, OS changes or fallback.
            browser = playwright.chromium.launch(channel="chrome", headless=True, chromium_sandbox=True)
            manifest['chromium_version'] = browser.version
            context = browser.new_context(viewport={'width': 1440, 'height': 1000}, device_scale_factor=1,
                                          locale='de-DE', timezone_id='UTC', color_scheme='light',
                                          reduced_motion='reduce', accept_downloads=True, service_workers='block')
            context.set_default_timeout(10000)
            context.set_default_navigation_timeout(30000)
            def guard(route):
                request = route.request
                if not request_allowed(request.method, request.url):
                    manifest['blocked_requests'].append({'method': request.method, 'url': request.url})
                    route.abort('blockedbyclient')
                else:
                    route.continue_()
            context.route('**/*', guard)
            page = context.new_page()
            page.on('pageerror', lambda error: manifest['page_errors'].append(str(error)))
            page.on('console', lambda message: manifest['console_errors'].append(message.text) if message.type == 'error' else None)
            page.on('requestfailed', lambda request: manifest['request_failures'].append({'url': request.url, 'error': request.failure}))
            page.on('response', lambda response: manifest['http_errors'].append({'url': response.url, 'status': response.status}) if response.status >= 400 else None)
            health_response = context.request.get(BASE_URL + '/api/health', max_redirects=0)
            require(health_response.ok, 'Start the local results-only server on 127.0.0.1:8765.')
            health = health_response.json()
            require(health.get('inference_enabled') is False and health.get('model_loaded') is False, 'Refusing a live-enabled or model-loaded server. Use a separate results-only server.')
            manifest['backend'] = {k: health.get(k) for k in ('mode', 'model_key', 'model_id', 'revision', 'inference_enabled', 'model_loaded', 'runtime_state')}
            # A pre-existing loopback server must serve this exact checkout, not another app/version.
            for name, expected in manifest['source_sha256'].items():
                if name.startswith('web/'):
                    response = context.request.get(BASE_URL + '/' + name[4:], max_redirects=0)
                    require(response.ok and hashlib.sha256(response.body()).hexdigest() == expected, f'Server/checkout mismatch: {name}')
            checks = BrowserChecks(page, output, manifest, expect)
            try:
                checks.initial_and_insurance()
                checks.replay('insurance', 'fall_002', 2)
                checks.replay('bank-support', 'bank_cards_03', 3)
                checks.all_suites_and_navigation()
                checks.replay('clarification', 'clarify_order_cancellation_02', 2)
                checks.clarification()
                checks.minimal_pairs()
                checks.reliability()
                checks.readiness()
                checks.custom_import_edit_export()
                checks.phones()
                for field in ('page_errors', 'console_errors', 'blocked_requests', 'request_failures', 'http_errors'):
                    require(not manifest[field], f'{field}: {manifest[field]}')
                require(manifest['source_sha256'] == source_hashes(), 'Sources changed during capture; retry after edits finish.')
                manifest['status'] = 'pass'
            finally:
                context.close()
                browser.close()
    except Exception as error:
        manifest['status'] = 'failed'
        manifest['failure'] = f'{type(error).__name__}: {error}'
        print(manifest['failure'], file=sys.stderr)
    finally:
        manifest['completed_utc'] = datetime.now(timezone.utc).isoformat()
        (output / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if manifest['status'] == 'pass':
        write_gallery_fragment(output)
    print(json.dumps({'status': manifest['status'], 'checks': len(manifest['checks']), 'screenshots': len(manifest['screenshots'])}, indent=2))
    return 0 if manifest['status'] == 'pass' else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'test-results/browser-gallery')
    parser.add_argument('--start-server', action='store_true', help='Start/stop an owned results-only server; fail if port 8765 is occupied.')
    parser.add_argument('--verify-artifact', type=Path, help='Check successful capture, PNG hashes and current sources without launching a browser.')
    args = parser.parse_args()
    if args.verify_artifact:
        verify_artifact(args.verify_artifact.resolve())
        print('Capture provenance and all screenshot hashes verified; inspect images before README publication.')
        return 0
    return capture_run(args.output.resolve(), args.start_server)


if __name__ == '__main__':
    raise SystemExit(main())
