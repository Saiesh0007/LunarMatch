import pytest
import numpy as np
import rasterio
from rasterio.transform import from_origin
import tempfile
import os
from app.services.input_quality import check_input_quality, check_pair_quality

@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

def make_test_image(path, data, nodata=None, dtype=np.uint8):
    transform = from_origin(0, 0, 10, 10)
    with rasterio.open(
        path, 'w', driver='GTiff',
        height=data.shape[0], width=data.shape[1],
        count=1, dtype=data.dtype, crs='+proj=latlong',
        transform=transform, nodata=nodata
    ) as dst:
        dst.write(data, 1)

def test_clean_image(tmp_dir):
    path = os.path.join(tmp_dir, "clean.tif")
    data = np.full((100, 100), 128, dtype=np.uint8)
    make_test_image(path, data, nodata=0, dtype=np.uint8)
    
    res = check_input_quality(path)
    assert res["ok"] is True
    assert res["invalid_fraction"] == 0.0

def test_majority_invalid(tmp_dir):
    path = os.path.join(tmp_dir, "bad.tif")
    data = np.full((100, 100), 128, dtype=np.uint8)
    # 30% of the footprint is a nodata gap inside the image (not border padding)
    data[20:50, 10:90] = 0
    data[10:20, 30:70] = 0  # (30*80 + 10*40) = 2800 px = 28 % of the raster
    make_test_image(path, data, nodata=0, dtype=np.uint8)

    res = check_input_quality(path)
    assert res["ok"] is False
    assert abs(res["bad_fraction_in_footprint"] - 0.28) < 1e-5
    assert res["fill_fraction"] == 0.0


def test_border_padding_is_not_bad_data(tmp_dir):
    """A map-projected strip rotated in its bounding box leaves ~50 % nodata corners."""
    import cv2
    path = os.path.join(tmp_dir, "rotated_strip.tif")
    data = np.zeros((200, 200), dtype=np.uint8)
    box = cv2.boxPoints(((100, 100), (110, 220), 45)).astype(np.int32)
    cv2.fillPoly(data, [box], 140)
    make_test_image(path, data, nodata=0, dtype=np.uint8)

    res = check_input_quality(path)
    assert res["ok"] is True
    assert res["fill_fraction"] > 0.35
    assert res["bad_fraction_in_footprint"] == 0.0


def test_interior_shadow_is_valid_uint8(tmp_dir):
    """Exact-zero shadows inside a lunar image are data, not nodata."""
    path = os.path.join(tmp_dir, "shadow.tif")
    data = np.full((100, 100), 128, dtype=np.uint8)
    data[30:80, 30:80] = 0  # 25 % deep shadow fully inside the frame
    make_test_image(path, data, dtype=np.uint8)

    res = check_input_quality(path)
    assert res["ok"] is True
    assert res["invalid_fraction"] == 0.0


def test_mostly_empty_raster_rejected(tmp_dir):
    path = os.path.join(tmp_dir, "empty.tif")
    data = np.zeros((100, 100), dtype=np.uint8)
    data[85:, :] = 128  # 15 % valid footprint
    make_test_image(path, data, nodata=0, dtype=np.uint8)

    res = check_input_quality(path)
    assert res["ok"] is False
    assert "valid footprint" in res["reason"]

def test_pair_ok(tmp_dir):
    path_a = os.path.join(tmp_dir, "clean_a.tif")
    path_b = os.path.join(tmp_dir, "clean_b.tif")
    data = np.full((100, 100), 128, dtype=np.uint8)
    make_test_image(path_a, data)
    make_test_image(path_b, data)
    
    res = check_pair_quality(path_a, path_b)
    assert res["ok"] is True
    assert res["invalid_a"] == 0.0
    assert res["invalid_b"] == 0.0

def test_pair_one_bad(tmp_dir):
    path_a = os.path.join(tmp_dir, "clean.tif")
    path_b = os.path.join(tmp_dir, "bad.tif")
    data_a = np.full((100, 100), 128, dtype=np.uint8)
    data_b = np.full((100, 100), 128, dtype=np.uint8)
    data_b[0:80, :] = 0  # only 20 % of the raster carries data
    make_test_image(path_a, data_a)
    make_test_image(path_b, data_b)

    res = check_pair_quality(path_a, path_b)
    assert res["ok"] is False
    assert res["invalid_a"] == 0.0
    assert abs(res["invalid_b"] - 0.80) < 1e-5

def test_missing_nodata_field(tmp_dir):
    path = os.path.join(tmp_dir, "sentinel.tif")
    # Use float32 to test sentinel values
    data = np.full((100, 100), 10.0, dtype=np.float32)
    data[20:50, 10:90] = -9999.0  # interior gap: 24 %
    data[10:20, 30:90] = -9999.0  # + 6 % -> 30 % of the footprint
    # Provide no declared nodata
    make_test_image(path, data, nodata=None, dtype=np.float32)
    
    res = check_input_quality(path)
    assert res["ok"] is False
    assert abs(res["invalid_fraction"] - 0.30) < 1e-5


def test_rgba_png_alpha_is_a_mask_not_data(tmp_dir):
    """Browse PNGs saved as RGBA have an all-255 alpha channel; it must not read as saturated padding."""
    import cv2
    rng = np.random.default_rng(0)
    gray = rng.integers(1, 255, (120, 80), dtype=np.uint8)
    rgba = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGRA)  # alpha = 255 everywhere
    path = os.path.join(tmp_dir, "browse_rgba.png")
    cv2.imwrite(path, rgba)
    res = check_input_quality(path)
    assert res["ok"] is True, res["reason"]
    assert res["fill_fraction"] < 0.01

    rgba[:, :50, 3] = 0  # left 62 % transparent: genuinely outside the image footprint
    cv2.imwrite(path, rgba)
    res = check_input_quality(path)
    assert res["fill_fraction"] == pytest.approx(50 / 80, abs=0.01)
