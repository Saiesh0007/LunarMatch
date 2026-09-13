import json

import numpy as np
import pytest

rasterio = pytest.importorskip("rasterio")
from rasterio.transform import from_origin

from app.io.geotiff_reader import load_lunar_image, read_geotiff_metadata


def make_tiff(path, crs=None):
    with rasterio.open(path, "w", driver="GTiff", height=4, width=5, count=1, dtype="float32", crs=crs, transform=from_origin(100, 200, 5, 5)) as dataset:
        dataset.write(np.ones((1, 4, 5), dtype=np.float32))


def test_read_georeferenced_tiff(tmp_path):
    path = tmp_path / "OHRC_scene.tif"
    make_tiff(path, "EPSG:32643")
    metadata = read_geotiff_metadata(str(path))
    assert metadata["crs"] == "EPSG:32643"
    assert metadata["gsd_meters"] == 5.0
    assert metadata["sensor_hint"] == "OHRC"


def test_read_tiff_without_crs(tmp_path):
    path = tmp_path / "scene.tif"
    make_tiff(path)
    metadata = read_geotiff_metadata(str(path))
    assert metadata["crs"] is None
    assert np.isnan(metadata["gsd_meters"])


def test_read_png_with_sidecar(tmp_path):
    from PIL import Image
    path = tmp_path / "scene.png"
    Image.fromarray(np.full((4, 5), 128, dtype=np.uint8)).save(path)
    path.with_suffix(".json").write_text(json.dumps({"sensor": "OHRC", "gsd_meters": 2.0}), encoding="utf-8")
    image, metadata = load_lunar_image(str(path))
    assert image.dtype == np.float32
    assert image.shape == (4, 5)
    assert metadata["sensor"] == "OHRC"


def test_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        read_geotiff_metadata("missing.tif")
