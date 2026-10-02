"""Optional real-browser regression; start python server.py first.

Run only in an environment where Chromium and loopback browsing are permitted.
This script is NOT part of Python unittest discovery and was NOT executed in the
creation environment. It never calls /api/infer or loads a model. Screenshots are
created only by a genuine, successful browser run; never by a design mockup.
"""
import json
import os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def main():
    from playwright.sync_api import sync_playwright
    output = ROOT / 'docs' / 'screenshots'
    output.mkdir(parents=True, exist_ok=True)
    checks, errors, inference_calls = [], [], []
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=os.environ.get('CHROMIUM_PATH', '/usr/bin/chromium'),
            headless=True, chromium_sandbox=True,
        )
        page = browser.new_page(viewport={'width': 1440, 'height': 1000}, device_scale_factor=1)
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda request: inference_calls.append(request.url)
                if request.url.endswith('/api/infer') else None)
        page.goto('http://127.0.0.1:8765', wait_until='networkidle')
        page.wait_for_function("document.querySelectorAll('.case-item').length === 60")
        assert page.locator('#suite-select').input_value() == 'insurance'
        assert page.locator('[data-field]').count() == 2
        assert page.locator('.document-section').count() > 0
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(output / 'workbench-desktop.png'), full_page=True)
        checks.append('1440px: real document workbench with 60 cases and two fields')

        page.locator('[data-case="fall_002"]').click()
        page.locator('[data-field="evidence"]').click()
        page.locator('[data-evidence="gold"]').click()
        assert page.locator('.highlight-gold').count() > 0
        page.locator('#highlight-select').select_option('none')
        assert page.locator('.highlight-gold,.highlight-model,.highlight-both').count() == 0
        page.locator('#search').fill('not-a-real-case-xyz')
        assert page.locator('.case-item').count() == 0
        assert page.locator('.document-section').count() == 0
        page.locator('#reset-filters').click()
        assert page.locator('.case-item').count() == 60
        checks.append('document: field switch, evidence navigation, highlighting and empty-filter reset')

        # Only verified, actually recorded benchmark replay is used here.
        insurance = json.loads((ROOT / 'web/data/insurance.json').read_text())
        page.locator('#open-playground').click()
        assert page.locator('#playground').is_visible()
        if insurance['status'] == 'completed':
            page.locator('#show-saved').click()
            assert page.locator('[data-output-field]').count() == 2
            assert page.locator('#output-kind').inner_text() == 'Gespeicherte Inferenz'
            original = page.locator('#input-state').input_value()
            page.locator('#input-state').fill(original + ' Bearbeitet.')
            assert page.locator('#show-saved').is_disabled()
            assert page.locator('[data-output-field]').count() == 0
            page.locator('#input-state').fill(original)
            assert page.locator('#show-saved').is_enabled()
        else:
            assert page.locator('#show-saved').is_disabled()
        page.locator('#input-schema').fill('{')
        assert page.locator('#show-saved').is_disabled()
        page.locator('#example-select').select_option('fall_003')
        checks.append('editor: multi-field replay or explicit pending state; edited/malformed input invalidation')

        for suite, count, errors_count, has_pairs in [('general', 120, 4, True), ('finance', 80, 4, True), ('clean72', 72, 11, False)]:
            page.locator('#suite-select').select_option(suite)
            page.locator('[data-nav="explorer"]').click()
            assert page.locator('.case-item').count() == count
            page.locator('#filter-outcome').select_option('errors')
            assert page.locator('.case-item').count() == errors_count
            page.locator('[data-nav="overview"]').click()
            assert page.locator('#paired-panel').is_visible() == has_pairs
        page.goto('http://127.0.0.1:8765/#explorer?suite=general&case=en_it_routing_003&field=decision', wait_until='networkidle')
        assert page.locator('#filter-split').input_value() == 'english_control'
        assert page.locator('[data-case="en_it_routing_003"]').get_attribute('aria-pressed') == 'true'
        checks.append('suite denominators, error counts, independent pairs and control-case deep link')

        page.locator('[data-nav="playground"]').click()
        page.locator('[data-nav="method"]').click()
        page.go_back()
        assert page.locator('#playground').is_visible()
        page.go_forward()
        assert page.locator('#method').is_visible()
        previous_theme = page.locator('html').get_attribute('data-theme')
        page.locator('#theme-toggle').click()
        expected_theme = 'dark' if previous_theme == 'light' else 'light'
        page.reload(wait_until='networkidle')
        assert page.locator('html').get_attribute('data-theme') == expected_theme
        checks.append('history and persisted light/dark theme')

        for width in (390, 320):
            page.set_viewport_size({'width': width, 'height': 844})
            page.goto('http://127.0.0.1:8765/#explorer?suite=insurance', wait_until='networkidle')
            for pane in ('cases', 'document', 'result'):
                page.locator(f'[data-pane="{pane}"]').click()
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (width, pane)
                assert page.locator('#workbench-shell').get_attribute('data-mobile-pane') == pane
                page.screenshot(path=str(output / f'workbench-{pane}-{width}.png'), full_page=True)
            for route in ('overview', 'playground', 'method'):
                page.locator(f'[data-nav="{route}"]').click()
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (width, route)
                assert page.locator('#' + route).is_visible()
            checks.append(f'{width}px: deliberate phone panes and three other views without viewport overflow')
        assert not errors, errors
        assert not inference_calls, inference_calls
        browser.close()
    result = {'status': 'pass', 'checks': checks, 'console_errors': errors,
              'model_inference_executed': False, 'real_browser_rendering': True}
    print(json.dumps(result, indent=2))
    (ROOT / 'docs/browser-test-results.json').write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
