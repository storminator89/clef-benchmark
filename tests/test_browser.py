"""Optional real-browser regression test; start python server.py first.
Requires Python Playwright 1.62.0 and a Chromium executable.
Never requests inference. No model results are mocked or simulated.
"""
import json
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    from playwright.sync_api import sync_playwright
    (ROOT/'docs/screenshots').mkdir(parents=True,exist_ok=True)
    errors=[];checks=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,chromium_sandbox=True)
        page=browser.new_page(viewport={'width':1440,'height':1200},device_scale_factor=1)
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto('http://127.0.0.1:8765',wait_until='networkidle')
        page.wait_for_function("document.querySelector('#result-banner').textContent.includes('Abgeschlossener')")
        assert page.locator('.stat-value').first.inner_text().replace('\xa0',' ')=='96,7 %'
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
        page.screenshot(path=str(ROOT/'docs/screenshots/overview-desktop.png'),full_page=True)
        checks.append('desktop overview: final scores and no horizontal overflow')
        page.get_by_role('link',name='Fälle entdecken').click()
        page.locator('#filter-errors').check()
        assert page.locator('.case-item').count()==4
        page.locator('#search').fill('no-match-xyz')
        assert page.locator('.case-item').count()==0
        assert 'Keine Fälle' in page.locator('#case-list').inner_text()
        page.get_by_role('button',name='Zurücksetzen').click()
        assert page.locator('.case-item').count()==120
        page.locator('#filter-split').select_option('english_control')
        assert page.locator('.case-item').count()==30
        page.locator('#filter-split').select_option('mixed_schema_diagnostic')
        assert page.locator('.case-item').count()==30
        page.locator('#filter-split').select_option('german_primary')
        page.locator('.case-item').nth(1).click()
        page.locator('#case-detail summary').first.click()
        assert page.locator('#case-detail pre').is_visible()
        page.screenshot(path=str(ROOT/'docs/screenshots/explorer-desktop.png'),full_page=True)
        checks.append('explorer: errors, search-empty/reset, language filters, detail and schema')
        page.get_by_role('button',name='Im Playground öffnen').click()
        assert page.locator('#run-live').is_disabled()
        page.get_by_role('button',name='Gespeicherte Antwort').click()
        assert page.locator('#output-kind').inner_text()=='Gespeicherte Inferenz'
        assert page.locator('.output-choice').inner_text()
        original=page.locator('#input-state').input_value()
        page.locator('#input-state').fill(original+' Bearbeitet.')
        assert page.locator('#show-saved').is_disabled()
        page.locator('#input-state').fill(original)
        assert page.locator('#show-saved').is_enabled()
        page.locator('#input-schema').fill('{')
        assert page.locator('#show-saved').is_disabled()
        page.locator('#example-select').select_option(index=2)
        assert page.locator('#show-saved').is_enabled()
        page.get_by_role('button',name='Gespeicherte Antwort').click()
        page.get_by_role('button',name='Gespeicherte Antwort').click()
        page.screenshot(path=str(ROOT/'docs/screenshots/playground-desktop.png'),full_page=True)
        checks.append('playground: disabled live backend, real saved replay, edited input blocked, malformed JSON blocked, repeated replay')
        page.get_by_role('link',name='Methodik',exact=True).click()
        page.go_back()
        assert page.locator('#playground').is_visible()
        page.go_forward()
        assert page.locator('#method').is_visible()
        page.locator('#theme-toggle').click()
        assert page.locator('html').get_attribute('data-theme')=='light'
        page.reload(wait_until='networkidle')
        assert page.locator('html').get_attribute('data-theme')=='light'
        checks.append('navigation: back/forward; light-theme persistence')
        page.locator('a[data-nav="overview"]').click()
        page.screenshot(path=str(ROOT/'docs/screenshots/overview-light.png'),full_page=True)
        page.locator('#theme-toggle').click()
        page.set_viewport_size({'width':390,'height':844})
        for route in ['overview','explorer','playground','method']:
            page.goto('http://127.0.0.1:8765/#'+route,wait_until='networkidle')
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'),route
            assert page.locator('#'+route).is_visible()
            page.screenshot(path=str(ROOT/f'docs/screenshots/{route}-mobile.png'),full_page=True)
        checks.append('mobile 390px: all four views without horizontal overflow')
        if (ROOT/'web/data/finance.json').is_file():
            finance=json.loads((ROOT/'web/data/finance.json').read_text())
            page.locator('#suite-select').select_option('finance')
            assert '80 eigenständige' in page.locator('#suite-description').inner_text()
            page.locator('a[data-nav="explorer"]').click()
            assert page.locator('.case-item').count()==80
            page.locator('#filter-errors').check()
            expected=sum(not c['result']['correct'] for c in finance['cases'] if c['split']=='german_primary')
            assert page.locator('.case-item').count()==expected
            page.locator('#suite-select').select_option('general')
            assert page.locator('.case-item').count()==120
            checks.append('suite switching: finance80 vs general120, independent error counts and reset filters')
        assert not errors,errors
        browser.close()
    result={'status':'pass','checks':checks,'console_errors':errors,'model_inference_executed':False}
    print(json.dumps(result,indent=2))
    (ROOT/'docs/browser-test-results.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
