from pathlib import Path
import hashlib,json
from provenance_checks import matches
P=Path(__file__).resolve().parents[1]
m=json.loads((P/'benchmark/freeze_manifest.json').read_text())
for name,expected in m['files_sha256'].items():
 actual=hashlib.sha256((P/name).read_bytes()).hexdigest()
 assert matches(P,name,expected),f'Freeze mismatch: {name}'
print(f"Verified {len(m['files_sha256'])} frozen files")
