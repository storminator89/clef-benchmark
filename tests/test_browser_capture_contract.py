"""Model-free safety/provenance tests for the optional browser capture runner.

These tests do not import Playwright, bind a socket, launch Chromium or create
screenshots. They do not constitute browser/visual verification.
"""
import ast
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).with_name('test_browser.py')
spec = importlib.util.spec_from_file_location('browser_capture_contract_subject', SCRIPT)
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)


class BrowserCaptureContractTests(unittest.TestCase):
    def test_guard_allows_only_fixed_origin_read_requests(self):
        for method in ('GET', 'HEAD'):
            for path in ('/', '/app.js', '/data/insurance.json', '/api/health'):
                self.assertTrue(capture.request_allowed(method, capture.BASE_URL + path))
        for url in ('http://localhost:8765/', 'http://127.0.0.1:9000/',
                    'https://127.0.0.1:8765/', 'https://example.com/',
                    'http://127.0.0.1:8765.evil.example/',
                    'http://user:secret@127.0.0.1:8765/'):
            self.assertFalse(capture.request_allowed('GET', url))

    def test_guard_never_permits_inference_or_writes(self):
        for method in ('GET', 'HEAD', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'):
            self.assertFalse(capture.request_allowed(method, capture.BASE_URL + '/api/infer'))
            self.assertFalse(capture.request_allowed(method, capture.BASE_URL + '/api/infer?x=1'))
        for method in ('POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'):
            self.assertFalse(capture.request_allowed(method, capture.BASE_URL + '/api/health'))

    def test_browser_dependency_is_imported_only_inside_capture(self):
        tree = ast.parse(SCRIPT.read_text())
        top_level_imports = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]
        self.assertFalse(any('playwright' in ast.unparse(node) for node in top_level_imports))
        self.assertEqual(capture.PLAYWRIGHT_VERSION, '1.62.0')

    def test_launch_has_sandbox_and_no_alternate_binary_or_flags(self):
        tree = ast.parse(SCRIPT.read_text())
        launches = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute) and node.func.attr == 'launch']
        self.assertEqual(len(launches), 1)
        keywords = {item.arg: ast.literal_eval(item.value) for item in launches[0].keywords}
        self.assertEqual(keywords, {'headless': True, 'chromium_sandbox': True})

    def test_gallery_uses_standard_runner_and_bounded_short_lived_storage(self):
        workflow = (SCRIPT.parents[1]/'.github/workflows/browser-gallery.yml').read_text()
        self.assertIn('runs-on: ubuntu-24.04', workflow)
        self.assertIn('contents: read', workflow)
        self.assertIn('retention-days: 1\n', workflow)
        self.assertIn('10 * 1024 * 1024', workflow)
        self.assertIn("steps.artifact-size.outcome == 'success'", workflow)
        self.assertNotIn('context.tracing.start', SCRIPT.read_text())
        self.assertNotIn('record_video', SCRIPT.read_text())

    def test_existing_output_is_never_reused_or_deleted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sentinel = root / 'previous-capture.txt'
            sentinel.write_text('keep')
            with self.assertRaisesRegex(AssertionError, 'new or empty'):
                capture.capture_run(root, False)
            self.assertEqual(sentinel.read_text(), 'keep')
            self.assertEqual(list(root.iterdir()), [sentinel])

    def test_failed_capture_cannot_be_published(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'manifest.json').write_text(json.dumps({'status': 'failed'}))
            with self.assertRaisesRegex(AssertionError, 'did not pass'):
                capture.verify_artifact(root)
            with self.assertRaisesRegex(AssertionError, 'did not pass'):
                capture.write_gallery_fragment(root)
            self.assertFalse((root / 'README-GALLERY.txt').exists())

    def test_success_flags_do_not_override_changed_sources(self):
        manifest = {'status': 'pass', 'real_browser_rendering': True,
                    'model_inference_executed': False, 'synthetic_inputs_only': True,
                    'chromium_sandbox': True, 'source_sha256': {'web/app.js': 'old'}}
        with tempfile.TemporaryDirectory() as tmp, patch.object(capture, 'source_hashes', return_value={'web/app.js': 'new'}):
            root = Path(tmp)
            (root / 'manifest.json').write_text(json.dumps(manifest))
            with self.assertRaisesRegex(AssertionError, 'Sources changed'):
                capture.verify_artifact(root)

    def test_clean_flags_without_real_pngs_are_insufficient(self):
        manifest = {'status': 'pass', 'real_browser_rendering': True,
                    'model_inference_executed': False, 'synthetic_inputs_only': True,
                    'chromium_sandbox': True, 'source_sha256': {},
                    'page_errors': [], 'console_errors': [], 'blocked_requests': [],
                    'request_failures': [], 'http_errors': [], 'screenshots': []}
        with tempfile.TemporaryDirectory() as tmp, patch.object(capture, 'source_hashes', return_value={}):
            root = Path(tmp)
            (root / 'manifest.json').write_text(json.dumps(manifest))
            with self.assertRaisesRegex(AssertionError, 'Required gallery capture is missing'):
                capture.verify_artifact(root)

    def test_bad_png_is_rejected_without_producing_an_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'not-a-screenshot.txt'
            path.write_text('This is not a PNG or a browser screenshot.')
            with self.assertRaisesRegex(AssertionError, 'Not a PNG'):
                capture.png_size(path)


if __name__ == '__main__':
    unittest.main()
