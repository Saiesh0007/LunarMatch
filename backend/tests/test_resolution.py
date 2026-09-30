"""Tests for F2: Common GSD / resolution normalisation.

Verifies common GSD selection logic and the correct resampling of GeoTIFFs,
including geotransform scaling and pixel dimensions.
"""
import json
import time
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_bounds

from app.services.resolution import (
    common_gsd,
    resample_to_gsd,
    log_gsd_norm_stage,
)


@pytest.fixture
def tmp_geotiff(tmp_path):
    """Create a minimal 30m GSD GeoTIFF for testing."""
    width, height = 100, 100
    gsd = 30.0
    
    # from_bounds(west, south, east, north, width, height)
    # Origin at 0, 0
    transform = from_bounds(0.0, -gsd * height, gsd * width, 0.0, width, height)
    
    rng = np.random.default_rng(26166)
    data = rng.integers(10, 240, size=(height, width), dtype=np.uint8)

    path = tmp_path / "test_gsd_30m.tif"
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=width,
        height=height,
        count=1,
        dtype="uint8",
        transform=transform,
    ) as ds:
        ds.write(data, 1)
    return path


def test_common_gsd_logic():
    """Verify common_gsd selects the coarser (larger) GSD."""
    assert common_gsd(30.0, 15.0) == 30.0
    assert common_gsd(15.0, 30.0) == 30.0
    assert common_gsd(10.0, 10.0) == 10.0
    assert np.isnan(common_gsd(float("nan"), float("nan")))
    assert common_gsd(30.0, float("nan")) == 30.0
    assert common_gsd(float("nan"), 15.0) == 15.0


def test_resample_downsample_to_coarser(tmp_geotiff, tmp_path):
    """Test resampling from 30m to 60m (downsampling resolution)."""
    dst = tmp_path / "resampled_60m.tif"
    result = resample_to_gsd(str(tmp_geotiff), str(dst), 30.0, 60.0)

    assert Path(result).exists()
    with rasterio.open(result) as ds:
        # width/height should be halved
        assert ds.width == 50
        assert ds.height == 50
        
        # New transform should have 60m pixel size
        assert ds.transform.a == 60.0
        assert ds.transform.e == -60.0
        
        # Origin should remain 0, 0
        assert ds.transform.c == 0.0
        assert ds.transform.f == 0.0


def test_resample_upsample_to_finer(tmp_geotiff, tmp_path):
    """Test resampling from 30m to 15m (upsampling resolution)."""
    dst = tmp_path / "resampled_15m.tif"
    result = resample_to_gsd(str(tmp_geotiff), str(dst), 30.0, 15.0)

    assert Path(result).exists()
    with rasterio.open(result) as ds:
        # width/height should be doubled
        assert ds.width == 200
        assert ds.height == 200
        
        # New transform should have 15m pixel size
        assert ds.transform.a == 15.0
        assert ds.transform.e == -15.0


def test_resample_same_gsd_passes_through(tmp_geotiff, tmp_path):
    """Test resampling to the same GSD does a direct file copy."""
    dst = tmp_path / "resampled_30m.tif"
    result = resample_to_gsd(str(tmp_geotiff), str(dst), 30.0, 30.0)

    assert Path(result).exists()
    with rasterio.open(result) as ds:
        assert ds.width == 100
        assert ds.height == 100
        assert ds.transform.a == 30.0


def test_invalid_gsd_raises(tmp_geotiff, tmp_path):
    """Test invalid GSD values raise ValueError."""
    dst = tmp_path / "invalid.tif"
    with pytest.raises(ValueError, match="Invalid GSDs"):
        resample_to_gsd(str(tmp_geotiff), str(dst), 30.0, 0.0)
    with pytest.raises(ValueError, match="Invalid GSDs"):
        resample_to_gsd(str(tmp_geotiff), str(dst), -10.0, 30.0)
    with pytest.raises(ValueError, match="Invalid GSDs"):
        resample_to_gsd(str(tmp_geotiff), str(dst), 30.0, float("nan"))


def test_log_gsd_norm_stage(tmp_path):
    """Verify log_gsd_norm_stage writes correctly."""
    log_file = tmp_path / "decisions.jsonl"
    with open(log_file, "w", encoding="utf-8") as f:
        log_gsd_norm_stage(f, "input.tif", 30.0, 60.0, 15.5, False)
        log_gsd_norm_stage(f, "fallback.tif", float("nan"), float("nan"), 1.0, True, "no GSD")

    lines = log_file.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 2
    
    entry1 = json.loads(lines[0])
    assert entry1["stage"] == "gsd_norm"
    assert entry1["original_gsd"] == 30.0
    assert entry1["target_gsd"] == 60.0
    assert entry1["fallback"] is False
    
    entry2 = json.loads(lines[1])
    assert entry2["original_gsd"] is None
    assert entry2["target_gsd"] is None
    assert entry2["fallback"] is True
    assert entry2["reason"] == "no GSD"
