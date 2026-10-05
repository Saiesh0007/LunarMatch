import cv2
import rasterio
from rasterio.enums import ColorInterp
import numpy as np

MIN_FOOTPRINT_FRACTION = 0.25


def _border_connected(mask: np.ndarray) -> np.ndarray:
    """Pixels of `mask` belonging to connected regions that touch the raster border."""
    if not mask.any():
        return np.zeros_like(mask, dtype=bool)
    n, labels = cv2.connectedComponents(mask.astype(np.uint8), connectivity=8)
    border = np.unique(np.concatenate([labels[0, :], labels[-1, :], labels[:, 0], labels[:, -1]]))
    border = border[border != 0]
    return np.isin(labels, border) & mask


def check_input_quality(img_path: str, invalid_threshold: float = 0.20, check_uint8_sentinel: bool = True,
                        min_footprint_fraction: float = MIN_FOOTPRINT_FRACTION) -> dict:
    """
    F9: Input Quality Gate.
    Per-crop cloud/nodata quality control (SCDF, Sec. IV-B).

    Pixels are split into
      * fill    - nodata/sentinel regions connected to the raster border. This is
                  the padding a map-projected or rotated strip leaves around its
                  footprint (a north-up OHRC strip at 45 deg is ~50 % fill) and is
                  not a data-quality problem by itself.
      * bad     - nodata, NaN or sentinel pixels INSIDE the footprint (data gaps,
                  dropped lines, saturated/missing blocks).
    The crop is rejected when bad pixels exceed `invalid_threshold` of the
    footprint, or when the valid footprint covers less than
    `min_footprint_fraction` of the raster.

    Sentinels: declared nodata, NaN (floats), -9999 / -32768, 0 for uint16.
    For uint8, 0/255 are treated as padding only where they are border-connected
    (check_uint8_sentinel=True); interior 0/255 are legitimate deep shadow or
    glare in lunar imagery and are never counted as bad.
    """
    invalid_reasons = []
    try:
        with rasterio.open(img_path) as ds:
            data = ds.read()
            nodata_val = ds.nodata
            dtype = data.dtype

            # An alpha channel (e.g. RGBA browse PNGs) is a transparency mask, not image data:
            # transparent pixels are missing, and its 0/255 values must not be read as sentinels.
            alpha = [i for i, ci in enumerate(ds.colorinterp) if ci == ColorInterp.alpha]
            hard = np.zeros(data.shape[1:], dtype=bool)   # unambiguous missing data
            for i in alpha:
                hard |= data[i] == 0
            colour = [band for i, band in enumerate(data) if i not in alpha]
            low = np.ones(data.shape[1:], dtype=bool)     # uint8 extremes in every colour channel:
            high = np.ones(data.shape[1:], dtype=bool)    # padding only where border-connected
            for band in colour:
                if np.issubdtype(dtype, np.floating):
                    hard |= np.isnan(band)
                if nodata_val is not None and not (isinstance(nodata_val, float) and np.isnan(nodata_val)):
                    hard |= (band == nodata_val)
                hard |= (band == -9999) | (band == -32768)
                if dtype == np.uint16:
                    hard |= (band == 0)
                low &= band == 0
                high &= band == 255
            soft = (low | high) if (dtype == np.uint8 and check_uint8_sentinel and colour) else np.zeros_like(hard)

            fill = _border_connected(hard | soft)
            bad = hard & ~fill
            total = fill.size
            footprint = total - int(np.count_nonzero(fill))
            fill_fraction = float(np.count_nonzero(fill)) / total if total else 1.0
            footprint_fraction = 1.0 - fill_fraction
            bad_fraction = float(np.count_nonzero(bad)) / footprint if footprint > 0 else 1.0
            invalid_fraction = float(np.count_nonzero(fill | bad)) / total if total else 1.0

            if footprint_fraction < min_footprint_fraction:
                invalid_reasons.append(
                    f"invalid fraction {invalid_fraction:.2f} (valid footprint {footprint_fraction:.2f} < {min_footprint_fraction})")
            if bad_fraction > invalid_threshold:
                invalid_reasons.append(f"invalid fraction {bad_fraction:.2f} > {invalid_threshold} inside image footprint")

            return {
                "ok": not invalid_reasons,
                "invalid_fraction": invalid_fraction,
                "fill_fraction": fill_fraction,
                "bad_fraction_in_footprint": bad_fraction,
                "invalid_reasons": invalid_reasons,
                "reason": ", ".join(invalid_reasons) if invalid_reasons else None
            }
    except Exception as e:
        return {
            "ok": False,
            "invalid_fraction": 1.0,
            "fill_fraction": 1.0,
            "bad_fraction_in_footprint": 1.0,
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
        "fill_a": iq_a.get("fill_fraction"),
        "fill_b": iq_b.get("fill_fraction"),
        "threshold": threshold,
        "reason": reason
    }
