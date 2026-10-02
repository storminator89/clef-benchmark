"""Recreate the excluded, unscored source-row0 warmup image from pinned parquet."""
from pathlib import Path
import hashlib
import pyarrow.parquet as pq
P=Path(__file__).resolve().parents[1]
row=pq.read_table(P/'source/synthetic_chart/data/test-00000-of-00001.parquet').slice(0,1).to_pylist()[0]
b=row['image']['bytes']
assert hashlib.sha256(b).hexdigest()=='62fc37f439c079aed2e689c61b09f14b52e4d94f3810c878faa50e12290f9a5f'
out=P/'source/pilot_unscored/chart.png';out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(b)
print(out)
