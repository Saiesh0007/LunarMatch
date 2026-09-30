"""Lunar Polar Stereographic CRS reprojection and coordinate transforms.

Paper: Piesat full-moon registration (ISPRS Archives 2024), Sec. 2.2.4.
Provides reprojection to a lunar polar stereographic CRS, pixel-to-
selenographic conversion, and its inverse.  Pole selection (north or
south) is automatic based on the scene's mean latitude.

Reference ellipsoid: R = 1 737 400 m (IAU 2015 Moon sphere).
"""
import json
import time
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pyproj
from pyproj import CRS, Transformer

from ..utils.logging import logger

# ── Proj4 definitions ─────────────────────────────────────────────────────
LUNAR_RADIUS = 1_737_400.0  # metres (IAU 2015)

LUNAR_SOUTH_POLAR_PROJ4 = (
    "+proj=stere +lat_0=-90 +lon_0=0 +k=1 +x_0=0 +y_0=0 "
    f"+a={LUNAR_RADIUS} +b={LUNAR_RADIUS} +units=m +no_defs"
)

LUNAR_NORTH_POLAR_PROJ4 = (
    "+proj=stere +lat_0=90 +lon_0=0 +k=1 +x_0=0 +y_0=0 "
    f"+a={LUNAR_RADIUS} +b={LUNAR_RADIUS} +units=m +no_defs"
)

LUNAR_LATLON_PROJ4 = (
    f"+proj=longlat +a={LUNAR_RADIUS} +b={LUNAR_RADIUS} +no_defs"
)


def _select_pole(mean_latitude: float) -> str:
    """Return 'south' for negative latitudes, 'north' otherwise."""
    return "south" if mean_latitude < 0 else "north"


def _proj4_for_pole(pole: str) -> str:
    """Return the proj4 string for the given pole."""
    if pole == "south":
        return LUNAR_SOUTH_POLAR_PROJ4
    return LUNAR_NORTH_POLAR_PROJ4


def pixel_to_selenographic(
    x: float,
    y: float,
    geotransform: Tuple[float, float, float, float, float, float],
    crs_proj4: str,
) -> Tuple[float, float]:
    """Convert pixel coordinates to selenographic (lon, lat) degrees.

    Args:
        x: Pixel column (0-indexed, sub-pixel allowed).
        y: Pixel row (0-indexed, sub-pixel allowed).
        geotransform: GDAL-style 6-element affine (c, a, b, f, d, e).
        crs_proj4: Proj4 string of the raster CRS.
    Returns:
        (longitude_deg, latitude_deg) on the lunar sphere.
    Raises:
        ValueError: If the geotransform is malformed.
    """
    if len(geotransform) != 6:
        raise ValueError("geotransform must have 6 elements (GDAL affine)")
    c, a, b, f, d, e = geotransform
    map_x = a * x + b * y + c
    map_y = d * x + e * y + f

    src_crs = CRS.from_proj4(crs_proj4)
    dst_crs = CRS.from_proj4(LUNAR_LATLON_PROJ4)
    transformer = Transformer.from_crs(src_crs, dst_crs, always_xy=True)
    lon, lat = transformer.transform(map_x, map_y)
    return float(lon), float(lat)


def selenographic_to_pixel(
    lon: float,
    lat: float,
    geotransform: Tuple[float, float, float, float, float, float],
    crs_proj4: str,
) -> Tuple[float, float]:
    """Convert selenographic (lon, lat) degrees to pixel coordinates.

    Args:
        lon: Longitude in degrees.
        lat: Latitude in degrees.
        geotransform: GDAL-style 6-element affine.
        crs_proj4: Proj4 string of the raster CRS.
    Returns:
        (x_pixel, y_pixel) in sub-pixel coordinates.
    Raises:
        ValueError: If the geotransform is malformed or singular.
    """
    if len(geotransform) != 6:
        raise ValueError("geotransform must have 6 elements (GDAL affine)")
    c, a, b, f, d, e = geotransform

    src_crs = CRS.from_proj4(LUNAR_LATLON_PROJ4)
    dst_crs = CRS.from_proj4(crs_proj4)
    transformer = Transformer.from_crs(src_crs, dst_crs, always_xy=True)
    map_x, map_y = transformer.transform(lon, lat)

    # Invert the affine: [a b; d e] * [x; y] = [map_x - c; map_y - f]
    det = a * e - b * d
    if abs(det) < 1e-15:
        raise ValueError("Singular geotransform — cannot invert")
    inv_a = e / det
    inv_b = -b / det
    inv_d = -d / det
    inv_e = a / det
    dx = map_x - c
    dy = map_y - f
    px = inv_a * dx + inv_b * dy
    py = inv_d * dx + inv_e * dy
    return float(px), float(py)


def reproject_to_lunar_polar_stereographic(
    src_path: str,
    dst_path: str,
    R: float = LUNAR_RADIUS,
    pole: Optional[str] = None,
    demo_gt: Optional[Tuple[float, float, float, float, float, float]] = None,
) -> Tuple[str, bool]:
    """Reproject a georeferenced raster to lunar polar stereographic CRS.

    Paper: Piesat full-moon registration (ISPRS Archives 2024), Sec. 2.2.4.

    Uses rasterio.warp.reproject with bilinear resampling.  The output
    is a deterministic GeoTIFF with fixed creation options and no
    timestamps, so the operation is idempotent.

    Args:
        src_path: Input GeoTIFF path (must have a CRS and geotransform).
        dst_path: Output GeoTIFF path.
        R: Lunar radius in metres (default 1 737 400).
        pole: Force 'north' or 'south'. If *None*, auto-detect from
              the scene's mean latitude.
    Returns:
        Absolute path to the output file.
    Raises:
        ValueError: If the source has no geotransform or CRS.
    """
    import rasterio
    from rasterio.warp import reproject, Resampling, calculate_default_transform

    t0 = time.perf_counter()
    src_p = Path(src_path)
    dst_p = Path(dst_path)

    t_open_start = time.perf_counter()
    with rasterio.open(src_p) as src_ds:
        t_open_end = time.perf_counter()
        
        if (src_ds.crs is None or src_ds.transform is None or src_ds.transform.is_identity) and demo_gt is not None:
            # Handle demo fixture (.png/.jpg) substitution
            src_crs = CRS.from_proj4(LUNAR_SOUTH_POLAR_PROJ4 if pole is None else _proj4_for_pole(pole))
            from rasterio.transform import Affine
            src_transform = Affine(*demo_gt)
            bounds = rasterio.transform.array_bounds(src_ds.height, src_ds.width, src_transform)
            bounds_tuple = (bounds[0], bounds[1], bounds[2], bounds[3])
        else:
            if src_ds.crs is None or src_ds.transform is None:
                raise ValueError(
                    "Source raster has no CRS or geotransform; "
                    "cannot reproject to lunar polar stereographic"
                )
            src_crs = src_ds.crs
            src_transform = src_ds.transform
            bounds_tuple = src_ds.bounds

        # Determine pole from scene centre latitude
        centre_lon = (bounds_tuple[0] + bounds_tuple[2]) / 2.0
        centre_lat = (bounds_tuple[1] + bounds_tuple[3]) / 2.0
        if pole is None:
            pole = _select_pole(centre_lat)

        dst_crs_proj4 = _proj4_for_pole(pole)
        dst_crs = CRS.from_proj4(dst_crs_proj4)
        
        is_identity = (src_crs == dst_crs)
        if is_identity:
            import shutil
            # If the input was a PNG with demo_gt, write out a GeoTIFF using the demo_gt
            if src_ds.crs is None:
                t1 = time.perf_counter()
                profile = src_ds.profile.copy()
                profile.update(
                    driver="GTiff",
                    height=src_ds.height,
                    width=src_ds.width,
                    transform=src_transform,
                    crs=src_crs,
                    compress="deflate"
                )
                t2 = time.perf_counter()
                with rasterio.open(dst_p, "w", **profile) as dest:
                    for i in range(1, src_ds.count + 1):
                        dest.write(src_ds.read(i), i)
                t3 = time.perf_counter()
            else:
                t1 = time.perf_counter()
                t2 = time.perf_counter()
                shutil.copy2(src_p, dst_p)
                t3 = time.perf_counter()
            logger.info("CRS matches target; bypassing warp.")
            t4 = time.perf_counter()
            
            logger.info(f"Diag: open={(t_open_end-t_open_start)*1000:.1f}ms profile={(t2-t1)*1000:.1f}ms copy={(t3-t2)*1000:.1f}ms log={(t4-t3)*1000:.1f}ms")
            return str(dst_p.resolve()), True

        transform, width, height = calculate_default_transform(
            src_crs,
            dst_crs,
            src_ds.width,
            src_ds.height,
            *bounds_tuple,
        )

        profile = src_ds.profile.copy()
        profile.update(
            crs=dst_crs,
            transform=transform,
            width=width,
            height=height,
            driver="GTiff",
            compress="deflate",
            tiled=True,
            blockxsize=256,
            blockysize=256,
        )
        # Remove any timestamp tags for idempotent output
        profile.pop("creation_date", None)

        nodata = src_ds.nodata

        dst_p.parent.mkdir(parents=True, exist_ok=True)
        with rasterio.open(dst_p, "w", **profile) as dst_ds:
            for band_idx in range(1, src_ds.count + 1):
                src_data = src_ds.read(band_idx)
                dst_data = np.empty((height, width), dtype=src_data.dtype)
                reproject(
                    source=src_data,
                    destination=dst_data,
                    src_transform=src_transform,
                    src_crs=src_crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.bilinear,
                    src_nodata=nodata,
                    dst_nodata=nodata,
                )
                dst_ds.write(dst_data, band_idx)

    ms = (time.perf_counter() - t0) * 1000.0
    logger.info(f"CRS reproject -> {pole} polar stereographic in {ms:.1f} ms")
    return str(dst_p.resolve()), False


def log_crs_stage(
    decisions_file,
    src_path: str,
    pole: str,
    ms: float,
    fallback: bool,
    reason: Optional[str] = None,
) -> None:
    """Append the CRS stage entry to match_decisions.jsonl."""
    entry = {
        "stage": "crs",
        "src": src_path,
        "pole": pole,
        "ms": round(ms, 2),
        "fallback": fallback,
    }
    if reason:
        entry["reason"] = reason
    decisions_file.write(json.dumps(entry) + "\n")
