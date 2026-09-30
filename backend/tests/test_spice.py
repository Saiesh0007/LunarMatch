import os
import tempfile
import spiceypy
from app.services import spice_kernels, spice_kernel_build

def test_all_four_corners_project_to_moon():
    """Verify all four FOV corners intersect the lunar surface.
    A degenerate footprint makes F7's mask empty."""
    import tempfile
    from app.services import spice_kernel_build
    with tempfile.TemporaryDirectory() as tmpdir:
        tm_path = spice_kernel_build.build_all(tmpdir, {}, [])
        ctx = spice_kernels.load_kernels(tmpdir)
        from unittest import mock
        with mock.patch("spiceypy.str2et", return_value=0.0):
            fp = spice_kernels.compute_footprint("2020-07-01T00:32:51Z", "OHRC_SYNTHETIC", ctx)
        spiceypy.kclear()
        corners = [(lon, lat) for lon, lat in fp if lon is not None]
        assert len(corners) == 4, (
            f"only {len(corners)} of 4 corners hit the Moon: {fp}. "
            f"Adjust FOV in IK or orbit altitude in SPK until all four "
            f"project. Document the chosen values in the module docstring."
        )

def test_spice():
    # 1. load_kernels(None) -> None
    assert spice_kernels.load_kernels(None) is None
    
    # 2. load_kernels("/nonexistent") -> None
    assert spice_kernels.load_kernels("/nonexistent/dir/here") is None
    
    # Generate kernels for tests 3-5
    with tempfile.TemporaryDirectory() as tmpdir:
        tm_path = spice_kernel_build.build_all(tmpdir, {}, [])
        ctx = spice_kernels.load_kernels(tmpdir)
        try:
            # 3. compute_footprint returns 4 entries, >=2 are valid
            from unittest import mock
            utc = "2000-01-01T12:00:00Z" # J2000
            with mock.patch("spiceypy.str2et", return_value=0.0):
                footprint = spice_kernels.compute_footprint(utc, "OHRC_SYNTHETIC", ctx)
            assert len(footprint) == 4
            valid_corners = [x for x in footprint if x is not None]
            assert len(valid_corners) >= 2
            
            # 4. validate_pair_geometry with ctx=None
            meta_a = {"width": 1024, "height": 1024, "transform": (0, 30e-6, 0, 0, 0, -30e-6)}
            meta_b = {"width": 1024, "height": 1024, "transform": (0, 30e-6, 0, 0, 0, -30e-6)}
            res_none = spice_kernels.validate_pair_geometry(meta_a, meta_b, None)
            assert not res_none["ok"]
            assert res_none["reason"] == "no SPICE kernels configured"
            
            # 5. validate_pair_geometry with valid ctx
            res_valid = spice_kernels.validate_pair_geometry(meta_a, meta_b, ctx)
            assert res_valid["ok"] is True
            assert res_valid["sun_angle_diff_deg"] is not None
        finally:
            spiceypy.kclear()
