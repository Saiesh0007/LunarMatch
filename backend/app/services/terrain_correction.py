"""F11: Cosine Terrain Correction.

Paper: ISRO MCC Phobos (planet.pdf), Sec. 6 — Eq. 7:
       ρ_H = ρ_T · (cos Φ / cos β)
"""
from typing import Optional, Dict, Any
import numpy as np


def apply_cosine_correction(
    image: np.ndarray,
    correction: np.ndarray,
    mask: Optional[np.ndarray] = None,
) -> Dict[str, Any]:
    """
    Apply radiometric cosine terrain correction to image based on local topography and solar zenith.

    Parameters:
        image: Input image (uint8, uint16, float32, etc.)
        correction: Radiometric correction factor array (cos(Phi) / cos(beta))
        mask: Optional boolean mask (True = lit, False = shadowed/excluded)

    Returns:
        dict with:
          image: corrected image in original dtype
          mean_before: float
          mean_after: float
          std_before: float
          std_after: float
          clip_hits: int
          reason: str | None
    """
    orig_dtype = image.dtype

    if np.issubdtype(orig_dtype, np.integer):
        dtype_max = float(np.iinfo(orig_dtype).max)
    else:
        # For floating point images, max bound is 1.0 if normalized, else large float
        dtype_max = 1.0 if float(np.nanmax(image)) <= 1.0 else float(np.finfo(np.float32).max)

    img_f = image.astype(np.float32)

    if mask is not None:
        img_f[~mask] = 0
        valid_mask = mask
    else:
        valid_mask = np.ones(img_f.shape[:2], dtype=bool)

    if np.any(valid_mask):
        mean_before = float(img_f[valid_mask].mean())
        std_before = float(img_f[valid_mask].std())
    else:
        mean_before = 0.0
        std_before = 0.0

    # Apply correction
    corrected = img_f * correction

    # Clip to [0, dtype_max]
    corrected_clipped = np.clip(corrected, 0.0, dtype_max)

    if np.issubdtype(orig_dtype, np.integer):
        clip_hits = int(np.sum((corrected_clipped == 0.0) | (corrected_clipped == dtype_max)))
    else:
        clip_hits = int(np.sum(np.isclose(corrected_clipped, 0.0) | np.isclose(corrected_clipped, dtype_max)))

    if np.any(valid_mask):
        mean_after = float(corrected_clipped[valid_mask].mean())
        std_after = float(corrected_clipped[valid_mask].std())
    else:
        mean_after = 0.0
        std_after = 0.0

    if np.issubdtype(orig_dtype, np.integer):
        out_img = np.round(corrected_clipped).astype(orig_dtype)
    else:
        out_img = corrected_clipped.astype(orig_dtype)

    return {
        "image": out_img,
        "mean_before": mean_before,
        "mean_after": mean_after,
        "std_before": std_before,
        "std_after": std_after,
        "clip_hits": clip_hits,
        "reason": None,
    }
