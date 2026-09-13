from dataclasses import dataclass, replace
import json
import logging
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PipelineConfig:
    source_sensor: str
    reference_sensor: str
    preprocessing: str
    feature_method: str
    matcher: str
    estimator: str
    geometry_model: str
    subpixel_refinement: bool
    pyramid_levels: int
    rationale: str


def _canonical_sensor(value: object) -> str:
    normalized = str(value or "").upper().replace("-", "_").replace(" ", "_")
    aliases = {
        "TMC_2": "TMC2",
        "TMC2": "TMC2",
        "LRO_NAC": "LRO_NAC",
        "LRONAC": "LRO_NAC",
        "OHRC": "OHRC",
        "IIRS": "IIRS",
        "SELENE": "SELENE",
    }
    return aliases.get(normalized, "unknown")


def detect_sensor(metadata: dict, filename: Optional[str] = None) -> str:
    """Detect a supported lunar sensor from metadata or filename.

    Args:
        metadata: Parsed PDS metadata dictionary.
        filename: Optional source filename used as a fallback.
    Returns:
        Canonical sensor name or ``unknown``.
    Raises:
        None: Malformed metadata falls back safely to ``unknown``.
    """
    for key in ("sensor", "INSTRUMENT_ID", "INSTRUMENT_NAME", "instrument_id", "instrument_name"):
        if key in metadata:
            detected = _canonical_sensor(metadata[key])
            if detected != "unknown":
                return detected
            value_text = str(metadata[key]).upper().replace("-", "_")
            for token, sensor in (("OHRC", "OHRC"), ("TMC2", "TMC2"), ("TMC_2", "TMC2"), ("IIRS", "IIRS"), ("LRO_NAC", "LRO_NAC"), ("LRO NAC", "LRO_NAC"), ("SELENE", "SELENE")):
                if token in value_text:
                    return sensor
    text = str(filename or "").upper().replace("-", "_")
    for token, sensor in (("OHRC", "OHRC"), ("TMC2", "TMC2"), ("TMC_2", "TMC2"), ("IIRS", "IIRS"), ("LRO_NAC", "LRO_NAC"), ("SELENE", "SELENE")):
        if token in text:
            return sensor
    logger.warning("Unable to detect sensor; falling back to unknown")
    return "unknown"


def _config(source: str, reference: str, feature: str, matcher: str, estimator: str, geometry: str, preprocessing: str, levels: int, rationale: str) -> PipelineConfig:
    return PipelineConfig(source, reference, preprocessing, feature, matcher, estimator, geometry, True, levels, rationale)


_ROUTING_TABLE = {
    ("OHRC", "OHRC"): _config("OHRC", "OHRC", "rift2_multiscale", "bf_ratio", "magsac", "affine", "clahe_denoise", 3, "Same sensor with changing Sun angle; multiscale RIFT2 preserves phase structure."),
    ("OHRC", "TMC2"): _config("OHRC", "TMC2", "rift2_multiscale", "bf_ratio", "magsac", "affine", "clahe", 3, "Cross-sensor scale gap requires a three-level RIFT2 pyramid."),
    ("OHRC", "IIRS"): _config("OHRC", "IIRS", "rift2", "mi_dense", "magsac", "affine", "clahe", 1, "IIRS resolution is coarse; use single-scale dense matching."),
    ("OHRC", "LRO_NAC"): _config("OHRC", "LRO_NAC", "hopc_rift2_fusion", "bf_ratio", "magsac", "affine", "clahe", 3, "High-resolution sensors with differing illumination benefit from HOPC and RIFT2."),
    ("TMC2", "LRO_NAC"): _config("TMC2", "LRO_NAC", "rift2", "flann_ratio", "magsac", "similarity", "denoise_only", 1, "Comparable structural bands allow simple single-scale similarity estimation."),
    ("TMC2", "SELENE"): _config("TMC2", "SELENE", "rift2", "flann_ratio", "ransac", "similarity", "denoise_only", 1, "Conservative single-scale similarity fallback for this sensor pair."),
    ("IIRS", "LRO_NAC"): _config("IIRS", "LRO_NAC", "hopc", "mi_dense", "magsac", "affine", "clahe", 1, "Hyperspectral-to-NAC registration uses dense HOPC at coarse resolution."),
    ("unknown", "unknown"): _config("unknown", "unknown", "rift2_multiscale", "bf_ratio", "magsac", "affine", "clahe", 3, "Unknown sensors use the robust general-purpose multiscale configuration."),
}


def select_pipeline_config(source_metadata: dict, reference_metadata: dict, user_override: Optional[str] = None) -> PipelineConfig:
    """Select a deterministic pipeline configuration for a sensor pair.

    Args:
        source_metadata: Source PDS metadata or sensor dictionary.
        reference_metadata: Reference PDS metadata or sensor dictionary.
        user_override: Optional feature/config override.
    Returns:
        A populated :class:`PipelineConfig`.
    Raises:
        None: Unknown pairs safely use the unknown fallback configuration.
    """
    source = detect_sensor(source_metadata)
    reference = detect_sensor(reference_metadata)
    selected = _ROUTING_TABLE.get((source, reference), _ROUTING_TABLE[("unknown", "unknown")])
    if user_override:
        override = str(user_override).lower()
        feature = "hopc_rift2_fusion" if override in ("fusion", "hopc_rift2_fusion") else override
        selected = replace(selected, feature_method=feature, rationale=f"User override selected {feature}; automatic sensor routing bypassed.")
    return selected


def reduce_iirs_to_grayscale(iirs_cube: np.ndarray, band_mask_path: Optional[str] = None) -> tuple[np.ndarray, str]:
    """Reduce an IIRS hyperspectral cube to a normalized band-mean image.

    Args:
        iirs_cube: Hyperspectral cube with shape ``(H, W, bands)``.
        band_mask_path: Optional JSON mask path containing a boolean ``mask`` list.
    Returns:
        Float32 grayscale image in [0, 1] and the method label.
    Raises:
        ValueError: If the cube is not three-dimensional or has no bands.
    """
    cube = np.asarray(iirs_cube, dtype=np.float32)
    if cube.ndim != 3 or cube.shape[2] == 0:
        raise ValueError("iirs_cube must have shape (H, W, bands)")
    indices = np.arange(cube.shape[2])
    mask_path = Path(band_mask_path) if band_mask_path else Path("backend/data/iirs_band_mask.json")
    if mask_path.exists():
        try:
            payload = json.loads(mask_path.read_text(encoding="utf-8"))
            mask = np.asarray(payload.get("mask", []), dtype=bool)
            if len(mask) == cube.shape[2] and np.any(mask):
                indices = indices[mask]
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            pass
    grayscale = np.mean(cube[:, :, indices], axis=2)
    if np.nanmin(grayscale) < 0.0 or np.nanmax(grayscale) > 1.0:
        grayscale -= np.nanmin(grayscale)
        maximum = np.nanmax(grayscale)
        if maximum > 0:
            grayscale /= maximum
    return np.ascontiguousarray(np.nan_to_num(grayscale), dtype=np.float32), "band_mean_fallback"
