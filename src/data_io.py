"""Strict input loading, provenance verification and scalar parsing."""
from __future__ import annotations

import gzip
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path
from urllib.request import Request, urlopen
import shutil


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_sources(root: Path, download: bool = False) -> list[dict]:
    manifest = json.loads((root / "data/source_manifest.json").read_text(encoding="utf-8"))
    for item in manifest["files"]:
        path = root / "data/raw" / item["filename"]
        if not path.exists():
            if not download:
                raise FileNotFoundError(f"{path}: run python -m src.download first")
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_suffix(path.suffix + ".part")
            with urlopen(Request(item["url"], headers={"User-Agent": "Phase1-Academic-Audit/1.0"}), timeout=90) as response, temporary.open("wb") as out:
                shutil.copyfileobj(response, out)
            temporary.replace(path)
        actual = sha256_file(path)
        if actual != item["sha256"]:
            raise ValueError(f"Source checksum mismatch: {path.name}. Never silently accept changed upstream data.")
    return manifest["files"]


def load_jsonl(path: Path) -> tuple[list[dict], list[dict], list[dict]]:
    records, types, missing = [], {}, {}
    # Fail on malformed JSON rather than hide dropped input lines.
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            record = json.loads(line)
            if not isinstance(record, dict):
                raise TypeError(f"{path.name}:{line_number}: expected object")
            records.append(record)
            for key, value in record.items():
                types.setdefault(key, Counter())[type(value).__name__] += 1
                counters = missing.setdefault(key, Counter())
                counters["null"] += value is None
                counters["empty_string"] += isinstance(value, str) and not value.strip()
                counters["empty_list"] += isinstance(value, list) and not value
                counters["empty_dict"] += isinstance(value, dict) and not value
    type_rows, missing_rows = [], []
    for key in sorted(types):
        for kind, count in sorted(types[key].items()):
            type_rows.append({"file": path.name, "field": key, "raw_type": kind, "count": count})
        missing_rows.append({"file": path.name, "field": key, "rows": len(records),
                             "absent_key": len(records)-sum(types[key].values()), **dict(missing[key])})
    return records, type_rows, missing_rows


def canonical_hash(record: dict) -> str:
    return hashlib.sha256(json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def parse_price(value) -> float:
    if value is None or isinstance(value, bool):
        return math.nan
    if isinstance(value, (int, float)):
        return float(value) if math.isfinite(value) and value >= 0 else math.nan
    if isinstance(value, str):
        text = value.strip().replace(",", "")
        if re.fullmatch(r"\$?\d+(\.\d{1,2})?", text):
            return float(text.lstrip("$"))
    return math.nan


def has_image_url(value) -> bool:
    return isinstance(value, list) and any(
        isinstance(image, dict) and any(isinstance(v, str) and v.startswith(("https://", "http://"))
        for k, v in image.items() if "url" in k or k in ("hi_res", "large", "thumb"))
        for image in value
    )
