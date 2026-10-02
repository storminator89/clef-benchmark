"""Accept unchanged measured files or the explicitly recorded portable export."""
import hashlib,json
def matches(root,relative,recorded):
 path=root/relative
 if not path.is_file():return False
 actual=hashlib.sha256(path.read_bytes()).hexdigest()
 if actual==recorded:return True
 mapping=root/'provenance/portable_export.json'
 if not mapping.is_file():return False
 item=json.loads(mapping.read_text())['files'].get(str(relative),{})
 return item.get('measured_or_original_sha256')==recorded and item.get('export_sha256')==actual
