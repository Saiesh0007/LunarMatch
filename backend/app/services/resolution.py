"""GSD normalisation and resolution matching.

Ensures input pairs are resampled to a common Ground Sample Distance (GSD).
The coarser (larger) GSD is selected to avoid hallucinating detail.
Uses INTER_AREA for downsampling and INTER_CUBIC for upsampling (if forced).
"""
import time
from pathlib import Path
from typing import Tuple, Optional

import cv2
import numpy as np
import rasterio
from rasterio.transform import Affine

from ..utils.logging import logger


def common_gsd(gsd_a: float, gsd_b: float) -> float:
    """Select the coarser (larger) GSD to prevent detail hallucination."""
    if np.isnan(gsd_a) and np.isnan(gsd_b):
        return float("nan")
    if np.isnan(gsd_a):
        return float(gsd_b)
    if np.isnan(gsd_b):
        return float(gsd_a)
    return float(max(gsd_a, gsd_b))


def resample_to_gsd(
    src_path: str,
    dst_path: str,
    src_gsd: float,
    dst_gsd: float,
) -> str:
    """Resample an image to a target GSD and update its geotransform.

    Args:
        src_path: Path to the input image (must be GeoTIFF).
        dst_path: Path to write the resampled GeoTIFF.
        src_gsd: Current GSD in metres/pixel.
        dst_gsd: Target GSD in metres/pixel.
    Returns:
        Absolute path to the output file.
    Raises:
        ValueError: If the source has no geotransform or cannot be read.
    """
    t0 = time.perf_counter()
    src_p = Path(src_path)
    dst_p = Path(dst_path)

    if src_gsd <= 0 or dst_gsd <= 0 or np.isnan(src_gsd) or np.isnan(dst_gsd):
        raise ValueError(f"Invalid GSDs: src={src_gsd}, dst={dst_gsd}")

    scale_factor = src_gsd / dst_gsd

    # Short-circuit if scale is essentially 1.0 (within 1%)
    if abs(scale_factor - 1.0) < 0.01:
        import shutil
        dst_p.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_p, dst_p)
        logger.info("GSD matches target; passing through unaltered.")
        return str(dst_p.resolve())

    with rasterio.open(src_p) as src_ds:
        if src_ds.transform is None or src_ds.transform.is_identity:
            raise ValueError(f"Source raster {src_path} lacks a valid geotransform.")
        
        orig_transform = src_ds.transform
        orig_crs = src_ds.crs
        nodata = src_ds.nodata
        
        new_width = max(1, int(round(src_ds.width * scale_factor)))
        new_height = max(1, int(round(src_ds.height * scale_factor)))
        
        # Scaling the geotransform: 
        # New pixel size is larger by (1/scale_factor)
        # Translation (top-left) remains the same
        new_transform = orig_transform * Affine.scale(1.0 / scale_factor, 1.0 / scale_factor)

        profile = src_ds.profile.copy()
        profile.update(
            width=new_width,
            height=new_height,
            transform=new_transform,
            driver="GTiff",
            compress="deflate",
        )
        # Remove timestamps for idempotent output
        profile.pop("creation_date", None)

        dst_p.parent.mkdir(parents=True, exist_ok=True)
        with rasterio.open(dst_p, "w", **profile) as dst_ds:
            for band_idx in range(1, src_ds.count + 1):
                src_data = src_ds.read(band_idx)
                
                # INTER_AREA for downsampling (scale_factor < 1)
                # INTER_CUBIC for upsampling (scale_factor > 1)
                interp = cv2.INTER_AREA if scale_factor < 1.0 else cv2.INTER_CUBIC
                
                # cv2.resize expects (width, height)
                dst_data = cv2.resize(src_data, (new_width, new_height), interpolation=interp)
                dst_ds.write(dst_data, band_idx)

    ms = (time.perf_counter() - t0) * 1000.0
    logger.info(f"GSD resampled {src_gsd:.2f} -> {dst_gsd:.2f}m in {ms:.1f} ms")
    return str(dst_p.resolve())


def log_gsd_norm_stage(
    decisions_file,
    src_path: str,
    original_gsd: float,
    target_gsd: float,
    ms: float,
    fallback: bool,
    reason: Optional[str] = None,
) -> None:
    """Append the gsd_norm stage entry to match_decisions.jsonl."""
    import json
    entry = {
        "stage": "gsd_norm",
        "src": src_path,
        "original_gsd": float(original_gsd) if not np.isnan(original_gsd) else None,
        "target_gsd": float(target_gsd) if not np.isnan(target_gsd) else None,
        "ms": round(ms, 2),
        "fallback": fallback,
    }
    if reason:
        entry["reason"] = reason
    decisions_file.write(json.dumps(entry) + "\n")
