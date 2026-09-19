import pytest
from app.services.illumination import compute_illumination, pair_sun_angle_ok

@pytest.fixture
def spice_ctx():
    import tempfile
    from app.services import spice_kernel_build, spice_kernels
    with tempfile.TemporaryDirectory() as tmpdir:
        spice_kernel_build.build_all(tmpdir, {}, [])
        ctx = spice_kernels.load_kernels(tmpdir)
        yield ctx
        import spiceypy
        spiceypy.kclear()

def test_spice_path(spice_ctx):
    meta = {"time_utc": "2020-07-01T00:32:51Z"}
    from unittest import mock
    with mock.patch("spiceypy.str2et", return_value=0.0):
        res = compute_illumination(meta, spice_ctx)
    
    assert res["source"] == "spice"
    assert res["reason"] is None
    assert res["incidence_deg"] is not None
    assert 0 <= res["incidence_deg"] <= 180
    assert res["solar_elevation_deg"] is not None

def test_pds_fallback():
    meta = {"solar_elevation_deg": 45.0, "solar_azimuth_deg": 120.0}
    res = compute_illumination(meta, None)
    
    assert res["source"] == "pds"
    assert res["solar_elevation_deg"] == 45.0
    assert res["solar_azimuth_deg"] == 120.0
    assert res["incidence_deg"] is None

def test_pair_ok_within_threshold():
    meta_a = {"solar_elevation_deg": 45.0}
    meta_b = {"solar_elevation_deg": 40.0}
    
    assert pair_sun_angle_ok(meta_a, meta_b, None, max_diff_deg=20.0) is True

def test_pair_rejected_above_threshold():
    meta_a = {"solar_elevation_deg": 80.0}
    meta_b = {"solar_elevation_deg": 40.0}
    
    assert pair_sun_angle_ok(meta_a, meta_b, None, max_diff_deg=20.0) is False

def test_missing_both_sources():
    meta = {}
    res = compute_illumination(meta, None)
    
    assert res["source"] == "pds"
    assert res["solar_elevation_deg"] is None
    assert res["solar_azimuth_deg"] is None
    assert res["incidence_deg"] is None
    assert res["reason"] == "PDS solar fields absent"
