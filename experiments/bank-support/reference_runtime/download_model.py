"""Download exact official release. No execution of downloaded code here."""
from pathlib import Path
import json,time,shutil
from huggingface_hub import snapshot_download
P=Path(__file__).parent
REV='17f0b0ad64efb65d273590632833508766b2aae6'
manifest_path=P/'model_file_manifest.json'
expected=json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
remaining=sum(max(0,info['bytes']-((P/'model'/name).stat().st_size if (P/'model'/name).exists() else 0)) for name,info in expected.items()) if expected else 20_000_000_000
if shutil.disk_usage(P).free < remaining+3_000_000_000:
 raise RuntimeError(f'Insufficient disk: need approximately {remaining+3_000_000_000} additional bytes including reserve')
started=time.monotonic()
print('Starting exact official release',REV,flush=True)
path=snapshot_download('Cloudflare/clef-flash',revision=REV,local_dir=P/'model',max_workers=2)
print(json.dumps({'path':path,'elapsed_seconds':time.monotonic()-started}),flush=True)
