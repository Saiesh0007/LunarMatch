from typing import Tuple
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

def preprocess_lunar_image(img: np.ndarray, config: PreprocessingConfig) -> Tuple[np.ndarray, dict]:
    """Execute configurable illumination and noise preprocessing pipeline."""
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
        
    return out, meta
