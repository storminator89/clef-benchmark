"""Static runner contracts; never starts a browser or inference."""
import ast
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class WahlerCaptureContract(unittest.TestCase):
    def test_sandbox_no_fallback(self):
        tree=ast.parse((ROOT/'tests/capture_wahler_browser.py').read_text())
        launches=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='launch']
        self.assertEqual(len(launches),1)
        self.assertEqual({k.arg:ast.literal_eval(k.value) for k in launches[0].keywords},{'channel':'chrome','headless':True,'chromium_sandbox':True})
        self.assertFalse(any('playwright' in ast.unparse(n) for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom))))
    def test_captures_are_separate_bounded_and_source_bound(self):
        workflow=(ROOT/'.github/workflows/browser-gallery.yml').read_text()
        for text in ['tests/capture_wahler_browser.py','tests/test_wahler_capture_contract.py','studies/wahler580/**','test-results/wahler-browser','steps.wahler-artifact-size.outcome','contents: read','retention-days: 1']:
            self.assertIn(text,workflow)
        script=(ROOT/'tests/capture_wahler_browser.py').read_text()
        for text in ['(1440,390)','studies/wahler580','source_hashes()','new or empty','request_allowed','model_loaded','study-outcome','page.keyboard.press']:
            self.assertIn(text,script)
    def test_format_two_explicitly_delegated(self):
        source=(ROOT/'tests/test_browser.py').read_text()
        self.assertIn("entry['id'] == 'wahler580' and data.get('format_version') == 2",source)
        self.assertIn('mobile checks run in capture_wahler_browser.py',source)
