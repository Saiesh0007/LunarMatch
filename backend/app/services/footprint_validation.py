"""F7: Orbital Footprint Validation."""
import rasterio.features
from shapely.geometry import Polygon
import numpy as np

from . import spice_kernels

def validate_orbital_pair(
    meta_a: dict,
    meta_b: dict,
    spice_ctx: dict,
    overlap_thr: float = 0.30
) -> dict:
    """F7: Orbital Footprint Validation."""
    H = meta_a.get("height", meta_a.get("lines", 1024))
    W = meta_a.get("width", meta_a.get("samples", 1024))
    
    # 1. Compute footprints
    print(f"DEBUG meta_a: {meta_a}")
    print(f"DEBUG meta_b: {meta_b}")
    try:
        utc_a = meta_a.get("utc", "2020-07-01T00:00:00Z")
        utc_b = meta_b.get("utc", "2020-07-01T00:00:01Z")
        fp_a = spice_kernels.compute_footprint(utc_a, meta_a.get("instrument", "OHRC_SYNTHETIC"), spice_ctx)
        fp_b = spice_kernels.compute_footprint(utc_b, meta_b.get("instrument", "OHRC_SYNTHETIC"), spice_ctx)
        print(f"DEBUG fp_a: {fp_a}")
        print(f"DEBUG fp_b: {fp_b}")
    except Exception as e:
        return {
            "ok": False,
            "overlap_ratio": 0.0,
            "valid_mask_shape": (H, W),
            "valid_fraction": 0.0,
            "reason": f"spice exception: {e}"
        }

    corners_a = [p for p in fp_a if p is not None]
    corners_b = [p for p in fp_b if p is not None]

    if len(corners_a) < 3:
        return {
            "ok": False,
            "overlap_ratio": 0.0,
            "valid_mask_shape": (H, W),
            "valid_fraction": 0.0,
            "reason": "degenerate footprint on reference"
        }
    if len(corners_b) < 3:
        return {
            "ok": False,
            "overlap_ratio": 0.0,
            "valid_mask_shape": (H, W),
            "valid_fraction": 0.0,
            "reason": "degenerate footprint on moving"
        }

    # 2. Build Polygons
    poly_a = Polygon(corners_a)
    poly_b = Polygon(corners_b)

    if not poly_a.is_valid or poly_a.area == 0:
        return {
            "ok": False,
            "overlap_ratio": 0.0,
            "valid_mask_shape": (H, W),
            "valid_fraction": 0.0,
            "reason": "invalid polygon after footprint on reference"
        }
    if not poly_b.is_valid or poly_b.area == 0:
        return {
            "ok": False,
            "overlap_ratio": 0.0,
            "valid_mask_shape": (H, W),
            "valid_fraction": 0.0,
            "reason": "invalid polygon after footprint on moving"
        }

    # 3. Compute intersection and IoU
    inter = poly_a.intersection(poly_b)
    union = poly_a.union(poly_b)
    iou = float(inter.area / union.area) if union.area > 0 else 0.0

    # 4. Rasterize
    transform = meta_a.get("transform")
    if inter.is_empty:
        mask = np.zeros((H, W), dtype=bool)
    else:
        # We must project the intersection from Lon/Lat to Image CRS, then to Pixel Space!
        crs_str = meta_a.get("crs")
        inter_proj = inter
        if crs_str:
            from pyproj import Transformer
            from shapely.ops import transform as shapely_transform
            transformer = Transformer.from_crs("+proj=longlat +R=1737400 +no_defs", crs_str, always_xy=True)
            inter_proj = shapely_transform(transformer.transform, inter)
            
        # Now inter_proj is in the CRS (e.g. Lunar Polar Stereographic)
        # We need to project it to Pixel coordinates using the inverse transform!
        if transform is not None:
            from rasterio.transform import Affine
            if isinstance(transform, tuple):
                aff = Affine(*transform)
            else:
                aff = transform
            if not (hasattr(aff, "is_identity") and aff.is_identity):
                inv_transform = ~aff
                def pixel_transform(x, y):
                    return inv_transform @ (x, y)
                inter_pixels = shapely_transform(pixel_transform, inter_proj)
            else:
                inter_pixels = inter_proj
        else:
            inter_pixels = inter_proj

        print(f"DEBUG inter_pixels: {inter_pixels.bounds}")
        mask = rasterio.features.rasterize(
            [(inter_pixels, 1)],
            out_shape=(H, W),
            fill=0,
            dtype=np.uint8
        ).astype(bool)
        
    valid_fraction = float(mask.mean())

    # 6. Decision
    ok = (iou >= overlap_thr) and (valid_fraction > 0.10)
    reason = None
    if not ok:
        if iou < overlap_thr:
            reason = f"overlap below threshold ({iou:.2f} < {overlap_thr})"
        else:
            reason = f"valid fraction below threshold ({valid_fraction:.2f} < 0.10)"

    return {
        "ok": ok,
        "overlap_ratio": iou,
        "valid_mask_shape": (H, W),
        "valid_fraction": valid_fraction,
        "reason": reason
    }
