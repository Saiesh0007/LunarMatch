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
    # 30% of pixels set to nodata (0 for uint8)
    data[0:30, :] = 0
    make_test_image(path, data, nodata=0, dtype=np.uint8)
    
    res = check_input_quality(path)
    assert res["ok"] is False
    assert abs(res["invalid_fraction"] - 0.30) < 1e-5

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
    data_b[0:30, :] = 0
    make_test_image(path_a, data_a)
    make_test_image(path_b, data_b)
    
    res = check_pair_quality(path_a, path_b)
    assert res["ok"] is False
    assert res["invalid_a"] == 0.0
    assert abs(res["invalid_b"] - 0.30) < 1e-5

def test_missing_nodata_field(tmp_dir):
    path = os.path.join(tmp_dir, "sentinel.tif")
    # Use float32 to test sentinel values
    data = np.full((100, 100), 10.0, dtype=np.float32)
    data[0:30, :] = -9999.0
    # Provide no declared nodata
    make_test_image(path, data, nodata=None, dtype=np.float32)
    
    res = check_input_quality(path)
    assert res["ok"] is False
    assert abs(res["invalid_fraction"] - 0.30) < 1e-5
