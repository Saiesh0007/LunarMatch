import rasterio
import numpy as np

def check_input_quality(img_path: str, invalid_threshold: float = 0.20, check_uint8_sentinel: bool = True) -> dict:
    """
    F9: Input Quality Gate.
    Per-crop cloud/nodata quality control (SCDF, Sec. IV-B).
    Threshold is 20% by default.

    For uint8/uint16, zeros are sentinel. For float32, zero is only invalid
    if it matches the declared nodata value. NaNs are always invalid for floats.

    check_uint8_sentinel should be False for raw, non-georeferenced uint8 images
    (e.g. plain browse PNG/JPG uploads with no reprojection padding), where
    0/255 are legitimate pixel values (deep shadow, glare) rather than nodata.
    """
    invalid_reasons = []
    try:
        with rasterio.open(img_path) as ds:
            data = ds.read()
            nodata_val = ds.nodata
            dtype = data.dtype
            
            invalid_mask = np.zeros(data.shape[1:], dtype=bool)
            
            for band in data:
                band_invalid = np.zeros_like(band, dtype=bool)
                
                # 1. NaN check
                if np.issubdtype(dtype, np.floating):
                    band_invalid |= np.isnan(band)
                    
                # 2. Declared nodata
                if nodata_val is not None:
                    band_invalid |= (band == nodata_val)
                    
                # 3. Sentinel values
                band_invalid |= (band == -9999) | (band == -32768)
                
                # 4. Zero and saturation handling
                if dtype == np.uint8:
                    if check_uint8_sentinel:
                        band_invalid |= (band == 0) | (band == 255)
                elif dtype == np.uint16:
                    band_invalid |= (band == 0)
                else:
                    # For float32, 0 is not a sentinel unless it is nodata
                    pass
                    
                invalid_mask |= band_invalid
                
            total_pixels = invalid_mask.size
            invalid_count = np.count_nonzero(invalid_mask)
            invalid_fraction = float(invalid_count) / total_pixels if total_pixels > 0 else 0.0
            
            if invalid_fraction > invalid_threshold:
                invalid_reasons.append(f"invalid fraction {invalid_fraction:.2f} > {invalid_threshold}")
                
            return {
                "ok": invalid_fraction <= invalid_threshold,
                "invalid_fraction": invalid_fraction,
                "invalid_reasons": invalid_reasons,
                "reason": ", ".join(invalid_reasons) if invalid_reasons else None
            }
    except Exception as e:
        return {
            "ok": False,
            "invalid_fraction": 1.0,
            "invalid_reasons": [str(e)],
            "reason": str(e)
        }

def check_pair_quality(img_a_path: str, img_b_path: str, threshold: float = 0.20, check_uint8_sentinel: bool = True) -> dict:
    iq_a = check_input_quality(img_a_path, threshold, check_uint8_sentinel)
    iq_b = check_input_quality(img_b_path, threshold, check_uint8_sentinel)
    
    ok = iq_a["ok"] and iq_b["ok"]
    reason = None
    if not ok:
        reasons = []
        if not iq_a["ok"]: reasons.append(f"Image A: {iq_a.get('reason')}")
        if not iq_b["ok"]: reasons.append(f"Image B: {iq_b.get('reason')}")
        reason = " | ".join(reasons)
        
    return {
        "ok": ok,
        "invalid_a": iq_a["invalid_fraction"],
        "invalid_b": iq_b["invalid_fraction"],
        "threshold": threshold,
        "reason": reason
    }
