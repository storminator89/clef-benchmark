"""Acquire pinned public datasets; extract original chart bytes. No model code runs.

Dependencies: Pillow and pyarrow from PyPI. Run this before build_benchmark.py.
Raw files stay local. Read Belege's LICENCE.txt before redistributing its files.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import collections
import hashlib
import io
import json
import urllib.request

import pyarrow.parquet as pq
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
CHART_REPO = "YuukiAsuna/synthetic_chart"
CHART_REV = "633cf14bc4c513f6c4806e319905e573afae12f4"
INVOICE_REPO = "laterrr/belege-de-invoices-sample"
INVOICE_REV = "da6044a02bd0b6c1d065b9f5615fe021272ece45"
EXPECTED = {
    "synthetic_chart/data/test-00000-of-00001.parquet": "bdc3175237feaf0ba383c455749113b35948e6a4e86d03506a4ebb7358d97ec8",
    "synthetic_chart/README.md": "473e87d79331b0e16bc98f4ae0b16f6d0f4211cde701313d31cdfa19c8aeed83",
    "belege-de-invoices-sample/LICENCE.txt": "37aedc622f7430cd8214f08e1462bfb036fb01da2cbed094892a82b9d6ac8837",
    "belege-de-invoices-sample/manifest.jsonl": "091cdc69832f227b8217290f0d66a842d63c27e3da30bc0914d0d3c616956426",
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def download(repo, rev, relative):
    path = SOURCE / repo.split("/")[-1] / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    expected = EXPECTED.get(str(path.relative_to(SOURCE)))
    if path.exists() and (not expected or sha(path.read_bytes()) == expected):
        return path
    url = f"https://huggingface.co/datasets/{repo}/resolve/{rev}/{relative}"
    with urllib.request.urlopen(url, timeout=120) as response:
        data = response.read()
    if expected and sha(data) != expected:
        raise ValueError(f"Pinned source checksum mismatch: {relative}")
    path.write_bytes(data)
    return path


def jsonlines(path, rows):
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows))


def acquire_charts():
    download(CHART_REPO, CHART_REV, "README.md")
    parquet = download(CHART_REPO, CHART_REV, "data/test-00000-of-00001.parquet")
    rows = pq.read_table(parquet).to_pylist()
    assert len(rows) == 300
    strata = collections.defaultdict(list)
    for index, row in enumerate(rows):
        row["_idx"] = index
        row["_sha"] = sha(row["image"]["bytes"])
        strata[row["type"], row["difficulty"]].append(row)
    assert len(strata) == 30 and all(len(group) == 10 for group in strata.values())
    selected = [row for key in sorted(strata) for row in sorted(strata[key], key=lambda r: r["_sha"])[:2]]
    out = SOURCE / "chart_selected60"
    (out / "images").mkdir(parents=True, exist_ok=True)
    (out / "labels").mkdir(exist_ok=True)
    manifest = []
    for row in selected:
        name = f"test-{row['_idx']:03d}"
        data = row["image"]["bytes"]
        image = Image.open(io.BytesIO(data))
        extension = image.format.lower()
        if extension == "jpeg":
            extension = "jpg"
        image_path = out / "images" / f"{name}.{extension}"
        label_path = out / "labels" / f"{name}.json"
        image_path.write_bytes(data)  # no re-encoding, resizing, or cropping
        label = {key: value for key, value in row.items() if key not in ["image", "_sha", "_idx"]}
        label["row_index"] = row["_idx"]
        label["image_sha256"] = row["_sha"]
        label["source"] = {"dataset": CHART_REPO, "revision": CHART_REV, "split": "test"}
        label_path.write_text(json.dumps(label, ensure_ascii=False, indent=2))
        manifest.append({"id": name, "row_index": row["_idx"], "image": str(image_path), "labels": str(label_path), "type": row["type"], "difficulty": row["difficulty"], "width": image.width, "height": image.height, "image_sha256": row["_sha"]})
    jsonlines(out / "manifest.jsonl", manifest)
    return len(manifest)


def acquire_invoices():
    for name in ["README.md", "LICENCE.txt", "manifest.jsonl", "DATASET.md", "COUNT.txt"]:
        download(INVOICE_REPO, INVOICE_REV, name)
    out = SOURCE / "belege-de-invoices-sample"
    rows = [json.loads(line) for line in (out / "manifest.jsonl").read_text().splitlines()]
    assert len(rows) == 40
    paths = [row[key] for row in rows for key in ["image", "label"]]
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda name: download(INVOICE_REPO, INVOICE_REV, name), paths))
    manifest = []
    for row in rows:
        image, label = out / row["image"], out / row["label"]
        manifest.append(dict(row, image_absolute=str(image), label_absolute=str(label), image_sha256=sha(image.read_bytes()), label_sha256=sha(label.read_bytes()), source_revision=INVOICE_REV))
    jsonlines(out / "acquired-manifest.jsonl", manifest)
    return len(manifest)


if __name__ == "__main__":
    print({"chart_images_extracted": acquire_charts(), "invoice_images_acquired": acquire_invoices()})
