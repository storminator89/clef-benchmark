"""Opt-in final admitted-data screenshot check on the approved browser runner.
Run: python3 tests/capture_wahler_browser.py --output <artifact-directory>
Never invoked by unittest discovery. No model execution, no sandbox fallback.
"""
import argparse
import hashlib
import json
from pathlib import Path
from test_browser import local_server, request_allowed, source_hashes, BASE_URL, ROOT

def capture_source_hashes():
    hashes=source_hashes()
    paths=[ROOT/'tests/capture_wahler_browser.py']+sorted((ROOT/'studies/wahler580').rglob('*'))
    for path in paths:
        if path.is_file():hashes[path.relative_to(ROOT).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    assert not args.output.exists() or not any(args.output.iterdir()), 'Use a new or empty capture directory'
    args.output.mkdir(parents=True,exist_ok=True)
    from playwright.sync_api import sync_playwright,expect
    captures=[]
    with local_server(True),sync_playwright() as p:
        browser=p.chromium.launch(channel='chrome',headless=True,chromium_sandbox=True)
        try:
            for width in (1440,390):
                context=browser.new_context(viewport={'width':width,'height':1000},device_scale_factor=1)
                context.route('**/*',lambda route:route.continue_() if request_allowed(route.request.method,route.request.url) else route.abort())
                page=context.new_page();errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
                response=page.request.get(BASE_URL+'/api/health');assert response.ok
                health=response.json();assert health.get('inference_enabled') is False and health.get('model_loaded') is False
                page.goto(BASE_URL+'/#studies?study=wahler580')
                expect(page.locator('.study-chart-group')).to_have_count(8)
                expect(page.locator('.study-chart-row')).to_have_count(24)
                expect(page.locator('.study-case')).to_have_count(100)
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
                assert page.evaluate('(()=>{const x=[...document.querySelectorAll("[id]")].map(e=>e.id);return new Set(x).size===x.length})()')
                name=f'wahler-three-model-{width}.png';page.screenshot(path=str(args.output/name),full_page=True);captures.append(name)
                page.locator('#study-model').select_option('jev');page.locator('#study-outcome').select_option('technical')
                expect(page.locator('.study-case')).to_have_count(2)
                page.locator('.study-case>summary').first.focus();page.keyboard.press('Enter')
                expect(page.locator('.study-case').first).to_have_attribute('open','')
                expect(page.locator('.study-case').first).to_contain_text('fachliches Ergebnis unbekannt')
                name=f'wahler-unavailable-case-{width}.png';page.screenshot(path=str(args.output/name),full_page=True);captures.append(name)
                page.locator('[data-study="language72"]').click();expect(page.locator('.study-case')).to_have_count(72)
                page.locator('[data-study="jev974"]').click();expect(page.locator('.study-case')).to_have_count(100)
                page.locator('[data-study="wahler580"]').click();expect(page.locator('.study-chart-group')).to_have_count(8)
                assert not errors,errors
                context.close()
        finally:browser.close()
    (args.output/'capture.json').write_text(json.dumps({'status':'passed','chromium_sandbox':True,'source_sha256':capture_source_hashes(),'screenshots':{name:hashlib.sha256((args.output/name).read_bytes()).hexdigest() for name in captures}},indent=2)+'\n')
if __name__=='__main__':main()
