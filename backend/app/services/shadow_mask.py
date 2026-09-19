import numpy as np
import rasterio
from scipy.ndimage import gaussian_filter
from typing import Optional

def compute_shadow_mask(img_path: str, dem_path: Optional[str], sun_azimuth_deg: float, sun_elevation_deg: float) -> dict:
    """
    F10: DEM-based shadow masking.
    
    If dem_path is None, returns all-ones mask and 1.0 correction.
    Otherwise:
      1. Loads DEM with rasterio.
      2. Verifies shape matches image.
      3. Applies Gaussian blur to DEM (sigma=1.5).
      4. Computes terrain slope lambda and aspect theta_b using np.gradient.
         (aspect convention: arctan2(-dx, dy) aligns with image coords where y increases downwards)
      5. Computes cos_beta from the solar angles and topography.
      6. Computes radiometric correction and shadow mask (lit = cos_beta > 0).
    """
    try:
        with rasterio.open(img_path) as src:
            img_shape = src.shape
    except Exception as e:
        return {
            "mask": np.ones((1024, 1024), dtype=bool),
            "correction": np.ones((1024, 1024), dtype=np.float32),
            "lit_fraction": 1.0,
            "correction_clip_hits": 0,
            "dem": None,
            "reason": f"img_path open failed: {e}"
        }

    if dem_path is None:
        return {
            "mask": np.ones(img_shape, dtype=bool),
            "correction": np.ones(img_shape, dtype=np.float32),
            "lit_fraction": 1.0,
            "correction_clip_hits": 0,
            "dem": None,
            "reason": "no DEM provided"
        }
        
    try:
        with rasterio.open(dem_path) as dem_ds:
            dem = dem_ds.read(1).astype(np.float32)
            
            if dem.shape != img_shape:
                return {
                    "mask": np.ones(img_shape, dtype=bool),
                    "correction": np.ones(img_shape, dtype=np.float32),
                    "lit_fraction": 1.0,
                    "correction_clip_hits": 0,
                    "dem": None,
                    "reason": "DEM shape mismatch"
                }
            
            # 3. Apply Gaussian blur (sigma=1.5)
            dem_smoothed = gaussian_filter(dem, sigma=1.5)
            
            # 4. Compute slope and aspect
            dy, dx = np.gradient(dem_smoothed)
            slope = np.arctan(np.sqrt(dx**2 + dy**2))
            aspect = np.arctan2(dx, -dy)  # Sign choice: (dx, -dy) aligns with solar azimuth from North/East in image coords
            
            # 5. Solar zenith and azimuth
            phi = np.radians(90.0 - sun_elevation_deg)
            theta_a = np.radians(sun_azimuth_deg)
            
            # 6. cos(beta)
            cos_beta = (np.cos(slope) * np.cos(phi) +
                        np.sin(slope) * np.sin(phi) * np.cos(theta_a - aspect))
            
            # 7. safe_cos_beta and correction
            # CRITICAL: clip safe_cos_beta BEFORE dividing, not after
            safe_cos_beta = np.clip(cos_beta, 1e-3, None)
            correction = np.clip(np.cos(phi) / safe_cos_beta, 0.5, 2.0)
            
            # 8. mask
            mask = cos_beta > 0
            
            # 9. lit_fraction
            lit_fraction = float(mask.mean())
            
            # 10. correction_clip_hits
            hits = int(np.sum(np.isclose(correction, 0.5, atol=1e-5) | np.isclose(correction, 2.0, atol=1e-5)))
            
            return {
                "mask": mask,
                "correction": correction.astype(np.float32),
                "lit_fraction": lit_fraction,
                "correction_clip_hits": hits,
                "dem": dem_path,
                "reason": None
            }
            
    except Exception as e:
        return {
            "mask": np.ones(img_shape, dtype=bool),
            "correction": np.ones(img_shape, dtype=np.float32),
            "lit_fraction": 1.0,
            "correction_clip_hits": 0,
            "dem": None,
            "reason": str(e)
        }
