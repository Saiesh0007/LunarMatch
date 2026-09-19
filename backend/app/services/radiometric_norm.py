"""F12: Cross-Modal Radiometric Normalisation.

Papers: MultiResSAR Sec. II-B; SCDF Sec. IV-B.
"""
from typing import Optional
import numpy as np
import cv2
import skimage.exposure


def match_histograms_to(
    src: np.ndarray,
    ref: np.ndarray,
    method: str = "clahe+hist",
) -> np.ndarray:
    """
    Match radiometric distribution of src to ref using CLAHE and/or histogram matching.

    Methods:
      "none"       — return src unchanged
      "clahe"      — CLAHE on both, return CLAHE'd src
      "hist"       — histogram match src to ref, no CLAHE
      "clahe+hist" — CLAHE both, then histogram match (default)

    Parameters:
      src: Source image to be adjusted
      ref: Reference image providing target histogram
      method: String selecting normalisation method

    Returns:
      Normalized src image with same dtype as input src.
    """
    if method == "none":
        return src

    orig_dtype = src.dtype

    # Handle NaN/Inf gracefully
    has_nan_src = np.isnan(src).any() or np.isinf(src).any()
    if has_nan_src:
        nan_mask = np.isnan(src) | np.isinf(src)
        src_work = np.nan_to_num(src, nan=0.0, posinf=0.0, neginf=0.0)
    else:
        src_work = src.copy()

    ref_work = np.nan_to_num(ref, nan=0.0, posinf=0.0, neginf=0.0)

    # 1. Apply CLAHE if requested
    if method in ("clahe", "clahe+hist"):
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        if np.issubdtype(orig_dtype, np.floating):
            s_min, s_max = float(src_work.min()), float(src_work.max())
            r_min, r_max = float(ref_work.min()), float(ref_work.max())
            s_denom = s_max - s_min if s_max > s_min else 1.0
            r_denom = r_max - r_min if r_max > r_min else 1.0
            src_u8 = np.clip((src_work - s_min) / s_denom * 255.0, 0, 255).astype(np.uint8)
            ref_u8 = np.clip((ref_work - r_min) / r_denom * 255.0, 0, 255).astype(np.uint8)
            src_clahe_u8 = clahe.apply(src_u8)
            ref_clahe_u8 = clahe.apply(ref_u8)
            src_work = src_clahe_u8.astype(np.float32) / 255.0 * s_denom + s_min
            ref_work = ref_clahe_u8.astype(np.float32) / 255.0 * r_denom + r_min
        elif orig_dtype == np.uint16:
            src_work = clahe.apply(src_work.astype(np.uint16))
            ref_work = clahe.apply(ref_work.astype(np.uint16))
        else:
            src_work = clahe.apply(src_work.astype(np.uint8))
            ref_work = clahe.apply(ref_work.astype(np.uint8))

    # 2. Histogram matching
    if method == "clahe":
        result = src_work
    elif method in ("hist", "clahe+hist"):
        if orig_dtype == np.uint16:
            src_u8 = (src_work / 256.0).astype(np.uint8)
            ref_u8 = (ref_work / 256.0).astype(np.uint8)
            matched_u8 = skimage.exposure.match_histograms(src_u8, ref_u8)
            result = (matched_u8.astype(np.float32) * 256.0).clip(0, 65535).astype(np.uint16)
        elif np.issubdtype(orig_dtype, np.floating):
            result = skimage.exposure.match_histograms(src_work.astype(np.float32), ref_work.astype(np.float32))
        else:
            result = skimage.exposure.match_histograms(src_work.astype(np.uint8), ref_work.astype(np.uint8))
    else:
        result = src_work

    # 3. Cast to original dtype
    if np.issubdtype(orig_dtype, np.integer):
        dtype_max = np.iinfo(orig_dtype).max
        result = np.clip(np.round(result), 0, dtype_max).astype(orig_dtype)
    else:
        result = result.astype(orig_dtype)

    if has_nan_src and np.issubdtype(orig_dtype, np.floating):
        result[nan_mask] = np.nan

    return result
