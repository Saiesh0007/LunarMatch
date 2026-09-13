import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

import cv2
import numpy as np


def _sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_run_manifest(
    run_id: str,
    reference_path: str,
    moving_path: str,
    config: dict[str, Any],
    synthetic_validation: bool = False,
    seed: int | None = None,
    routing_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build reproducibility metadata for a pipeline run.

    Args:
        run_id: Unique pipeline run identifier.
        reference_path: Reference input path.
        moving_path: Moving input path.
        config: JSON-serializable pipeline configuration.
        synthetic_validation: Whether the deterministic harness was used.
        seed: Harness seed, when applicable.
        routing_config: Optional serialized sensor routing decision.
    Returns:
        Manifest dictionary with hashes and runtime versions.
    Raises:
        FileNotFoundError: If either input path is missing.
    """
    config_json = json.dumps(config, sort_keys=True, default=str, separators=(",", ":"))
    try:
        commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True, cwd=Path(__file__).parents[3]).strip()
    except (OSError, subprocess.SubprocessError):
        commit = "unknown"
    manifest = {
        "run_id": run_id,
        "mode": "synthetic_validation" if synthetic_validation else "measured",
        "git_commit": commit,
        "input_sha256": {"reference": _sha256(reference_path), "moving": _sha256(moving_path)},
        "config_hash": hashlib.sha256(config_json.encode("utf-8")).hexdigest(),
        "python_version": platform.python_version(),
        "opencv_version": cv2.__version__,
        "numpy_version": np.__version__,
        "seed": seed if synthetic_validation else None,
    }
    if routing_config is not None:
        manifest["routing_config"] = routing_config
    return manifest
