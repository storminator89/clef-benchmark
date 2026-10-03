"""Read-only checks for evidence-derived, deterministic chart assets."""
import importlib.util
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('evaluation_charts', ROOT/'scripts/generate_evaluation_charts.py')
CHARTS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHARTS)

class EvaluationChartsTests(unittest.TestCase):
    def test_planned_denominators(self):
        partitions, diagnostic = CHARTS.load_data(ROOT)
        data = {(r['suite'],r['split']):r for r in partitions}
        for suite, clef, jev in [('bank_support80',68,75),('finance100',76,78)]:
            row=data[suite,'german_primary']
            self.assertEqual((row['clef'],row['jev'],row['expected']),(clef,jev,80))
        self.assertEqual(sum(r['expected'] for r in partitions),974)
        self.assertEqual([(r['correct'],r['total']) for r in diagnostic],[(5,13),(59,59)])
        self.assertIsNone(data['massive300','german_test_primary']['clef'])
        self.assertEqual(data['massive300','german_test_primary']['jev'],233)

    def test_svg_assets_are_current_and_accessible(self):
        first=CHARTS.render(ROOT)
        self.assertEqual(first,CHARTS.render(ROOT))
        self.assertNotIn('jev_coverage.svg', first)
        for name,content in first.items():
            self.assertEqual((ROOT/'docs/charts'/name).read_text(),content,name)
            if name.endswith('.svg'):
                svg=ET.fromstring(content)
                self.assertEqual(svg.get('role'),'img')
                self.assertIsNotNone(svg.find('{http://www.w3.org/2000/svg}title'))
                self.assertIsNotNone(svg.find('{http://www.w3.org/2000/svg}desc'))
                self.assertNotIn('<script',content)
                self.assertNotIn('href=',content)

if __name__ == '__main__': unittest.main()
