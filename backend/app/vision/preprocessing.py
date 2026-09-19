from typing import Tuple, Optional, Any
import cv2
import numpy as np
from ..models.schemas import PreprocessingConfig
from ..utils.logging import logger

def normalize_intensity(img: np.ndarray) -> np.ndarray:
    """Normalize image pixel values to full dynamic range [0, 255]."""
    if img.dtype != np.uint8:
        norm = cv2.normalize(img, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
        return norm.astype(np.uint8)
    
    min_val, max_val = float(img.min()), float(img.max())
    if max_val > min_val:
        norm = ((img.astype(np.float32) - min_val) / (max_val - min_val) * 255.0).astype(np.uint8)
        return norm
    return img

def apply_clahe(img: np.ndarray, clip_limit: float = 2.0, tile_grid_size: int = 8) -> np.ndarray:
    """
    Contrast Limited Adaptive Histogram Equalization (CLAHE).
    Essential for lunar optical & radar datasets to enhance crater rim contrast
    in deep shadow zones and bright sunlit slopes.
    """
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_grid_size, tile_grid_size))
    return clahe.apply(img)

def denoise_image(img: np.ndarray) -> np.ndarray:
    """
    Apply edge-preserving bilateral filtering to suppress sensor noise
    while keeping crisp crater boundaries and boulder features.
    """
    return cv2.bilateralFilter(img, d=5, sigmaColor=35, sigmaSpace=35)

def preprocess_lunar_image(
    img: np.ndarray,
    config: PreprocessingConfig,
    image_path: Optional[str] = None,
    solar_azimuth_deg: float = 180.0,
    solar_elevation_deg: float = 45.0,
    log_stage: Optional[Any] = None,
) -> Tuple[np.ndarray, dict]:
    """Execute configurable illumination, noise, and DEM shadow masking preprocessing pipeline."""
    meta = {}
    out = img.copy()
    
    # Ensure grayscale
    if len(out.shape) == 3:
        out = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
        
    if config.normalize:
        out = normalize_intensity(out)
        meta["normalized"] = True
        
    if config.clahe:
        out = apply_clahe(out, clip_limit=config.clip_limit, tile_grid_size=config.tile_grid_size)
        meta["clahe_applied"] = True
        meta["clahe_clip_limit"] = config.clip_limit
        
    if config.denoise:
        out = denoise_image(out)
        meta["denoised"] = True

    # F10: DEM-based shadow masking
    if image_path is not None:
        from pathlib import Path
        import time
        from ..config import settings
        from ..services import shadow_mask

        dem_dir = settings.DEM_DIR
        if dem_dir is None:
            fixtures_path = settings.BASE_DIR / "tests" / "fixtures"
            if fixtures_path.exists():
                dem_dir = fixtures_path

        image_p = Path(image_path)
        image_stem = image_p.stem

        dem_path = None
        if dem_dir:
            cands = [
                dem_dir / f"{image_stem}_dem.tif",
                dem_dir / f"{image_stem.replace('_ref', '')}_dem.tif" if "_ref" in image_stem else None,
                dem_dir / f"{image_stem.replace('_mov', '')}_dem.tif" if "_mov" in image_stem else None,
                dem_dir / f"{image_stem}.tif",
            ]
            for cand in cands:
                if cand and cand.exists():
                    dem_path = str(cand)
                    break
            if dem_path is None:
                dem_path = str(dem_dir / f"{image_stem}_dem.tif")

        t0_sh = time.perf_counter()
        shadow_result = shadow_mask.compute_shadow_mask(
            img_path=str(image_path),
            dem_path=dem_path,
            sun_azimuth_deg=solar_azimuth_deg,
            sun_elevation_deg=solar_elevation_deg,
        )
        sh_ms = (time.perf_counter() - t0_sh) * 1000.0

        shadow_log = {
            "stage": "shadow",
            "lit_fraction": float(shadow_result["lit_fraction"]),
            "correction_clip_hits": int(shadow_result["correction_clip_hits"]),
            "dem": shadow_result["dem"],
            "reason": shadow_result["reason"],
            "ms": round(sh_ms, 2),
        }
        meta["shadow"] = shadow_log
        if log_stage is not None:
            log_stage(shadow_log)

        # F11: Cosine Terrain Correction (ISRO MCC Phobos Sec. 6 Eq. 7)
        # F11 is the sole applier of correction factor and mask
        from ..services.terrain_correction import apply_cosine_correction
        t0_tc = time.perf_counter()
        tc_result = apply_cosine_correction(
            image=out,
            correction=shadow_result["correction"],
            mask=shadow_result["mask"],
        )
        tc_ms = (time.perf_counter() - t0_tc) * 1000.0
        out = tc_result["image"]

        tc_log = {
            "stage": "terrain_corr",
            "mean_before": float(tc_result["mean_before"]),
            "mean_after": float(tc_result["mean_after"]),
            "std_before": float(tc_result["std_before"]),
            "std_after": float(tc_result["std_after"]),
            "clip_hits": int(tc_result["clip_hits"]),
            "reason": tc_result["reason"],
            "ms": round(tc_ms, 2),
        }
        meta["terrain_corr"] = tc_log
        if log_stage is not None:
            log_stage(tc_log)
        
    return out, meta
