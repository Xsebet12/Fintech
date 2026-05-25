from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from glob import glob
from pathlib import Path
from typing import Any, Optional

import pandas as pd


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def ensure_dir(path: str | Path) -> Path:
    target = Path(path)
    target.mkdir(parents=True, exist_ok=True)
    return target


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_versioned_name(base_name: str, timestamp: Optional[str] = None, extension: str = ".csv") -> str:
    stamp = timestamp or utc_now_iso()
    safe_stamp = stamp.replace(":", "").replace(".", "")
    return f"{base_name}_{safe_stamp}{extension}"


def save_dataframe_versioned(
    df: pd.DataFrame,
    output_dir: str | Path,
    base_name: str,
    *,
    include_index: bool = False,
    metadata: Optional[dict[str, Any]] = None,
) -> tuple[Path, Optional[Path]]:
    output_path = ensure_dir(output_dir) / build_versioned_name(base_name)
    df.to_csv(output_path, index=include_index)

    metadata_path: Optional[Path] = None
    if metadata is not None:
        metadata_dir = ensure_dir(Path(output_dir) / ".." / "metadata")
        metadata_path = metadata_dir / build_versioned_name(base_name, extension=".json")
        payload = dict(metadata)
        payload.setdefault("records", int(len(df)))
        payload.setdefault("columns", list(df.columns))
        payload.setdefault("saved_at", utc_now_iso())
        payload.setdefault("output_file", output_path.name)
        payload.setdefault("output_hash", sha256_file(output_path))
        with open(metadata_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)

    return output_path, metadata_path


def latest_version_path(output_dir: str | Path, base_name: str, extension: str = ".csv") -> Optional[Path]:
    pattern = str(Path(output_dir) / f"{base_name}_*{extension}")
    candidates = [Path(candidate) for candidate in glob(pattern)]
    if not candidates:
        return None
    return max(candidates, key=lambda item: item.stat().st_mtime)
