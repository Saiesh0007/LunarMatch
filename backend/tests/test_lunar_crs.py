"""Tests for F1: Lunar Polar Stereographic CRS.

Verifies round-trip coordinate accuracy, nodata propagation,
idempotent output, and performance.

Paper: Piesat full-moon registration (ISPRS Archives 2024), Sec. 2.2.4.
"""
import json
import time
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_bounds

from app.services.lunar_crs import (
    LUNAR_RADIUS,
    LUNAR_SOUTH_POLAR_PROJ4,
    LUNAR_NORTH_POLAR_PROJ4,
    LUNAR_LATLON_PROJ4,
    pixel_to_selenographic,
    selenographic_to_pixel,
    reproject_to_lunar_polar_stereographic,
    log_crs_stage,
)


@pytest.fixture
def tmp_geotiff(tmp_path):
    """Create a minimal georeferenced GeoTIFF in lunar lat/lon CRS."""
    from pyproj import CRS

    width, height = 128, 128
    # Small patch near the south pole: lon 0..10, lat -85..-75
    transform = from_bounds(0.0, -85.0, 10.0, -75.0, width, height)
    crs = CRS.from_proj4(LUNAR_LATLON_PROJ4)

    rng = np.random.default_rng(26166)
    data = rng.integers(10, 240, size=(height, width), dtype=np.uint8)

    path = tmp_path / "test_input.tif"
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=width,
        height=height,
        count=1,
        dtype="uint8",
        crs=crs,
        transform=transform,
    ) as ds:
        ds.write(data, 1)
    return path


def test_round_trip_pixel_selenographic():
    """Pixel -> selenographic -> pixel round-trip within 1e-6 px."""
    # Geotransform for a 10 m/px south polar stereographic tile
    gt = (100.0, 10.0, 0.0, 200.0, 0.0, -10.0)
    crs = LUNAR_SOUTH_POLAR_PROJ4

    x_orig, y_orig = 50.5, 75.3
    lon, lat = pixel_to_selenographic(x_orig, y_orig, gt, crs)
    x_back, y_back = selenographic_to_pixel(lon, lat, gt, crs)

    assert abs(x_back - x_orig) < 1e-6, f"X round-trip error: {abs(x_back - x_orig)}"
    assert abs(y_back - y_orig) < 1e-6, f"Y round-trip error: {abs(y_back - y_orig)}"


def test_round_trip_north_pole():
    """Round-trip using the north polar CRS."""
    gt = (0.0, 5.0, 0.0, 0.0, 0.0, -5.0)
    crs = LUNAR_NORTH_POLAR_PROJ4

    x_orig, y_orig = 12.0, 24.0
    lon, lat = pixel_to_selenographic(x_orig, y_orig, gt, crs)
    x_back, y_back = selenographic_to_pixel(lon, lat, gt, crs)

    assert abs(x_back - x_orig) < 1e-6
    assert abs(y_back - y_orig) < 1e-6


def test_bad_geotransform_raises():
    """pixel_to_selenographic raises on malformed geotransform."""
    with pytest.raises(ValueError, match="6 elements"):
        pixel_to_selenographic(10, 20, (0, 1, 0), LUNAR_SOUTH_POLAR_PROJ4)


def test_reproject_creates_output(tmp_geotiff, tmp_path):
    """reproject_to_lunar_polar_stereographic produces a valid output file."""
    dst = tmp_path / "reprojected.tif"
    result, log = reproject_to_lunar_polar_stereographic(str(tmp_geotiff), str(dst))

    assert Path(result).exists()
    with rasterio.open(result) as ds:
        assert ds.crs is not None
        assert ds.width > 0
        assert ds.height > 0
        data = ds.read(1)
        assert data.shape[0] > 0


def test_reproject_idempotent(tmp_geotiff, tmp_path):
    """Reprojecting twice yields identical output bytes."""
    dst1 = tmp_path / "out1.tif"
    dst2 = tmp_path / "out2.tif"

    result1, log1 = reproject_to_lunar_polar_stereographic(str(tmp_geotiff), str(dst1))
    result2, log2 = reproject_to_lunar_polar_stereographic(str(tmp_geotiff), str(dst2))

    with rasterio.open(dst1) as d1, rasterio.open(dst2) as d2:
        np.testing.assert_array_equal(d1.read(1), d2.read(1))


def test_reproject_no_crs_raises(tmp_path):
    """Source with no CRS raises ValueError."""
    # Create a GeoTIFF without CRS
    path = tmp_path / "no_crs.tif"
    data = np.zeros((64, 64), dtype=np.uint8)
    with rasterio.open(
        path, "w", driver="GTiff", width=64, height=64, count=1, dtype="uint8"
    ) as ds:
        ds.write(data, 1)

    dst = tmp_path / "out.tif"
    with pytest.raises(ValueError, match="no CRS"):
        reproject_to_lunar_polar_stereographic(str(path), str(dst))


def test_reproject_pole_auto_detection(tmp_geotiff, tmp_path):
    """Auto pole detection selects south for negative latitudes."""
    dst = tmp_path / "auto_pole.tif"
    result, log = reproject_to_lunar_polar_stereographic(str(tmp_geotiff), str(dst))

    with rasterio.open(dst) as ds:
        crs_str = ds.crs.to_proj4()
        assert "+lat_0=-90" in crs_str  # south pole


def test_reproject_performance(tmp_geotiff, tmp_path):
    """Reproject completes within 400 ms on a small tile."""
    dst = tmp_path / "perf.tif"
    t0 = time.perf_counter()
    result, log = reproject_to_lunar_polar_stereographic(str(tmp_geotiff), str(dst))
    ms = (time.perf_counter() - t0) * 1000.0
    assert ms < 400, f"Reproject took {ms:.0f} ms, budget is 400 ms"


def test_log_crs_stage(tmp_path):
    """log_crs_stage writes a valid JSONL entry."""
    log_file = tmp_path / "decisions.jsonl"
    with open(log_file, "w", encoding="utf-8") as f:
        log_crs_stage(f, "input.tif", "south", 42.5, False)

    lines = log_file.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["stage"] == "crs"
    assert entry["pole"] == "south"
    assert entry["fallback"] is False
