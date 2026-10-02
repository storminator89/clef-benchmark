"""Offline checks for local documentation and repository report links."""
from html.parser import HTMLParser
from pathlib import Path
import re,unittest
from urllib.parse import unquote,urlsplit
ROOT=Path(__file__).resolve().parents[1]
PREFIX='https://github.com/storminator89/clef-benchmark/blob/main/'
class Links(HTMLParser):
 def __init__(self):super().__init__();self.urls=[];self.ids=set()
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.add(a['id'])
  for name in ('src','href'):
   if name in a:self.urls.append(a[name])
class LinkTests(unittest.TestCase):
 def test_markdown_local_paths(self):
  for path in ROOT.rglob('*.md'):
   if any(part in {'node_modules','.git','.venv','venv'} for part in path.relative_to(ROOT).parts):continue
   for target in re.findall(r'\]\(([^\s)]+)',path.read_text()):
    if target.startswith(('https:','http:','mailto:','#')):continue
    target=unquote(target.split('#')[0])
    if target:self.assertTrue((path.parent/target).exists(),f'{path.relative_to(ROOT)}: {target}')
 def test_web_links_and_known_public_report_paths(self):
  doc=Links();doc.feed((ROOT/'web/index.html').read_text())
  for target in doc.urls:
   if target.startswith(PREFIX):self.assertTrue((ROOT/target[len(PREFIX):]).is_file(),target)
   elif target.startswith('#'):self.assertIn(target[1:],doc.ids)
   elif not urlsplit(target).scheme:self.assertTrue((ROOT/'web'/target).is_file(),target)
if __name__=='__main__':unittest.main()
