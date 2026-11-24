# Copyright 2026 the LlamaFactory team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Persistent feedback for the WebUI training-memory estimator."""

import json
import os
from pathlib import Path
from typing import Any


CALIBRATION_SCHEMA_VERSION = 1
DEFAULT_CALIBRATION_PATH = Path("llamaboard_cache") / "memory_calibration.json"
ESTIMATE_METADATA_NAME = "memory_estimate.json"
ACTUAL_MEMORY_NAME = "memory_actual.json"
_EMA_ALPHA = 0.25
_MIN_RATIO = 0.5
_MAX_RATIO = 3.0


def get_calibration_path() -> Path:
    configured = os.getenv("LLAMAFACTORY_MEMORY_CALIBRATION_FILE", "").strip()
    return Path(configured).expanduser() if configured else DEFAULT_CALIBRATION_PATH


def _load_store(path: Path) -> dict[str, Any]:
    try:
        with open(path, encoding="utf-8") as stream:
            payload = json.load(stream)
    except (OSError, json.JSONDecodeError):
        return {"version": CALIBRATION_SCHEMA_VERSION, "buckets": {}}

    if not isinstance(payload, dict) or not isinstance(payload.get("buckets"), dict):
        return {"version": CALIBRATION_SCHEMA_VERSION, "buckets": {}}
    return payload


def get_calibration(bucket: str, path: Path | None = None) -> tuple[float, int]:
    entry = _load_store(path or get_calibration_path())["buckets"].get(bucket, {})
    try:
        factor = float(entry.get("ema_ratio", 1.0))
        samples = int(entry.get("samples", 0))
    except (AttributeError, TypeError, ValueError):
        return 1.0, 0

    return min(_MAX_RATIO, max(_MIN_RATIO, factor)), max(0, samples)


def record_calibration(
    bucket: str,
    *,
    actual_gib: float,
    base_estimated_gib: float,
    path: Path | None = None,
) -> dict[str, Any] | None:
    """Record one successful run and return the updated bucket entry."""
    if not bucket or actual_gib <= 0 or base_estimated_gib <= 0:
        return None

    calibration_path = path or get_calibration_path()
    store = _load_store(calibration_path)
    buckets = store.setdefault("buckets", {})
    previous = buckets.get(bucket, {}) if isinstance(buckets.get(bucket), dict) else {}
    samples = max(0, int(previous.get("samples", 0)))
    ratio = min(_MAX_RATIO, max(_MIN_RATIO, actual_gib / base_estimated_gib))
    previous_ratio = float(previous.get("ema_ratio", ratio))
    ema_ratio = ratio if samples == 0 else _EMA_ALPHA * ratio + (1.0 - _EMA_ALPHA) * previous_ratio
    entry = {
        "samples": samples + 1,
        "ema_ratio": round(min(_MAX_RATIO, max(_MIN_RATIO, ema_ratio)), 6),
        "last_ratio": round(ratio, 6),
        "last_actual_gib": round(actual_gib, 4),
        "last_base_estimated_gib": round(base_estimated_gib, 4),
    }
    buckets[bucket] = entry
    store["version"] = CALIBRATION_SCHEMA_VERSION

    calibration_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = calibration_path.with_name(f"{calibration_path.name}.{os.getpid()}.tmp")
    with open(temporary_path, "w", encoding="utf-8") as stream:
        json.dump(store, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")
    os.replace(temporary_path, calibration_path)
    return entry
