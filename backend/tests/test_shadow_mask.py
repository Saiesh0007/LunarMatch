import pytest
import numpy as np
import rasterio
import tempfile
import os
from rasterio.transform import from_origin
from app.services.shadow_mask import compute_shadow_mask

@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

def make_test_image(path, shape=(100, 100)):
    data = np.zeros(shape, dtype=np.uint8)
    transform = from_origin(0, 0, 10, 10)
    with rasterio.open(
        path, 'w', driver='GTiff',
        height=data.shape[0], width=data.shape[1],
        count=1, dtype=data.dtype, crs='+proj=latlong',
        transform=transform, nodata=0
    ) as dst:
        dst.write(data, 1)

def make_test_dem(path, data):
    transform = from_origin(0, 0, 10, 10)
    with rasterio.open(
        path, 'w', driver='GTiff',
        height=data.shape[0], width=data.shape[1],
        count=1, dtype=data.dtype, crs='+proj=latlong',
        transform=transform, nodata=0
    ) as dst:
        dst.write(data, 1)

def test_flat_dem_at_zenith(tmp_dir):
    img_path = os.path.join(tmp_dir, "img.tif")
    dem_path = os.path.join(tmp_dir, "dem.tif")
    make_test_image(img_path)
    make_test_dem(dem_path, np.full((100, 100), 100, dtype=np.uint16))
    
    res = compute_shadow_mask(img_path, dem_path, sun_azimuth_deg=90.0, sun_elevation_deg=90.0)
    assert res["lit_fraction"] == 1.0
    assert np.all(res["mask"] == True)

def test_flat_dem_sun_below_horizon(tmp_dir):
    img_path = os.path.join(tmp_dir, "img.tif")
    dem_path = os.path.join(tmp_dir, "dem.tif")
    make_test_image(img_path)
    make_test_dem(dem_path, np.full((100, 100), 100, dtype=np.uint16))
    
    res = compute_shadow_mask(img_path, dem_path, sun_azimuth_deg=90.0, sun_elevation_deg=-10.0)
    assert res["lit_fraction"] == 0.0
    assert np.all(res["mask"] == False)

def test_crater_dem_at_30deg(tmp_dir):
    img_path = os.path.join(tmp_dir, "img.tif")
    dem_path = os.path.join(tmp_dir, "dem.tif")
    make_test_image(img_path)
    
    dem = np.full((100, 100), 2500, dtype=np.float32)
    y, x = np.indices((100, 100))
    dist_sq = (x - 50)**2 + (y - 50)**2
    dem -= 500 * np.exp(-dist_sq / (0.5 * 20**2))
    dem = np.clip(dem, 1, 5000).astype(np.uint16)
    
    make_test_dem(dem_path, dem)
    
    res = compute_shadow_mask(img_path, dem_path, sun_azimuth_deg=90.0, sun_elevation_deg=30.0)
    assert 0.3 < res["lit_fraction"] < 0.9

def test_missing_dem(tmp_dir):
    img_path = os.path.join(tmp_dir, "img.tif")
    make_test_image(img_path)
    
    res = compute_shadow_mask(img_path, None, sun_azimuth_deg=90.0, sun_elevation_deg=30.0)
    assert res["lit_fraction"] == 1.0
    assert res["reason"] == "no DEM provided"
    assert np.all(res["mask"] == True)

def test_clip_prevented_nan(tmp_dir):
    img_path = os.path.join(tmp_dir, "img.tif")
    dem_path = os.path.join(tmp_dir, "dem.tif")
    make_test_image(img_path)
    
    # Very steep crater
    dem = np.full((100, 100), 2500, dtype=np.float32)
    y, x = np.indices((100, 100))
    dist_sq = (x - 50)**2 + (y - 50)**2
    dem -= 2000 * np.exp(-dist_sq / (0.5 * 5**2))
    dem = np.clip(dem, 1, 5000).astype(np.uint16)
    
    make_test_dem(dem_path, dem)
    
    res = compute_shadow_mask(img_path, dem_path, sun_azimuth_deg=90.0, sun_elevation_deg=5.0)
    assert np.all(np.isfinite(res["correction"]))

def test_dem_fixture_assertions():
    fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
    ref_path = os.path.join(fixtures_dir, "demo_b1a1_1024_ref.png")
    dem_path = os.path.join(fixtures_dir, "demo_b1a1_1024_dem.tif")
    if os.path.exists(ref_path) and os.path.exists(dem_path):
        with rasterio.open(ref_path) as ref_ds, rasterio.open(dem_path) as dem_ds:
            assert ref_ds.shape == dem_ds.shape
            assert ref_ds.transform == dem_ds.transform
            assert ref_ds.crs == dem_ds.crs

def test_crater_aspect_orientation():
    """Pin the aspect convention.

    Sun from the east (azimuth 90°). West rim of a crater faces the
    sun -> lit. East rim faces away -> shadowed. If the sign of
    the aspect computation is flipped, these two assertions swap.
    """
    import numpy as np

    # Synthetic single-crater DEM
    yy, xx = np.mgrid[0:1024, 0:1024]
    cx, cy = 512, 512
    radius = 100.0
    depth = 500.0
    r2 = (xx - cx)**2 + (yy - cy)**2
    crater = depth * np.exp(-r2 / (2 * (radius / 2.0)**2))
    dem = (crater + 100).astype(np.uint16)  # base 100m + crater

    # Write to a temp GeoTIFF with the same geotransform as the
    # ref image fixture.
    fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")
    ref_path = os.path.join(fixtures_dir, "demo_b1a1_1024_ref.png")

    with rasterio.open(ref_path) as ref_ds:
        meta = ref_ds.meta.copy()
        meta.update(driver="GTiff", dtype="uint16", count=1, nodata=0)

    with tempfile.TemporaryDirectory() as tmpdir:
        temp_dem = os.path.join(tmpdir, "crater_aspect_dem.tif")
        with rasterio.open(temp_dem, "w", **meta) as dst:
            dst.write(dem, 1)

        result = compute_shadow_mask(
            img_path=ref_path,
            dem_path=temp_dem,
            sun_azimuth_deg=90.0,   # from east
            sun_elevation_deg=30.0,
        )
        mask = result["mask"]

        # Sun is from the east. West side of crater (x < 512) faces
        # the sun. East side (x > 512) faces away.
        assert mask[512, 512 - 40] == True, (
            "west rim should be LIT. If this fails, the aspect sign "
            "in compute_shadow_mask is flipped. Try "
            "np.arctan2(dx, -dy) instead of np.arctan2(-dx, dy)."
        )
        assert mask[512, 512 + 40] == False, (
            "east rim should be SHADOWED. If this fails, same cause."
        )


