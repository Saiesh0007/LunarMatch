import pytest
from unittest import mock
import numpy as np
from app.services import footprint_validation

def test_full_overlap():
    meta_a = {"utc": "t1", "instrument": "i1"}
    meta_b = {"utc": "t2", "instrument": "i2"}
    fp = [(0,0), (0,1000), (1000,1000), (1000,0)]
    with mock.patch("app.services.spice_kernels.compute_footprint", side_effect=[fp, fp]):
        res = footprint_validation.validate_orbital_pair(meta_a, meta_b, None)
        assert res["ok"] is True
        assert np.isclose(res["overlap_ratio"], 1.0)
        assert res["valid_fraction"] > 0.10

def test_partial_overlap():
    meta_a = {}
    meta_b = {}
    fp_a = [(0,0), (0,1000), (1000,1000), (1000,0)]
    fp_b = [(500,0), (500,1000), (1500,1000), (1500,0)]
    with mock.patch("app.services.spice_kernels.compute_footprint", side_effect=[fp_a, fp_b]):
        res = footprint_validation.validate_orbital_pair(meta_a, meta_b, None, overlap_thr=0.1)
        assert res["ok"] is True
        assert 0.2 < res["overlap_ratio"] < 0.4
        assert res["valid_fraction"] > 0.10
        
def test_below_threshold():
    meta_a = {}
    meta_b = {}
    fp_a = [(0,0), (0,10), (10,10), (10,0)]
    fp_b = [(8,0), (8,10), (18,10), (18,0)]
    with mock.patch("app.services.spice_kernels.compute_footprint", side_effect=[fp_a, fp_b]):
        res = footprint_validation.validate_orbital_pair(meta_a, meta_b, None, overlap_thr=0.5)
        assert res["ok"] is False
        assert "below" in res["reason"]

def test_degenerate_footprint():
    meta_a = {}
    meta_b = {}
    fp_a = [None, None, None, (10, 20)]
    fp_b = [(0,0), (0,10), (10,10), (10,0)]
    with mock.patch("app.services.spice_kernels.compute_footprint", side_effect=[fp_a, fp_b]):
        res = footprint_validation.validate_orbital_pair(meta_a, meta_b, None)
        assert res["ok"] is False
        assert "degenerate" in res["reason"]

def test_valid_fraction_reported():
    meta_a = {"height": 100, "width": 100}
    meta_b = {}
    # A 50x50 square at the origin
    fp_a = [(0,0), (0,50), (50,50), (50,0)]
    fp_b = [(0,0), (0,50), (50,50), (50,0)]
    with mock.patch("app.services.spice_kernels.compute_footprint", side_effect=[fp_a, fp_b]):
        res = footprint_validation.validate_orbital_pair(meta_a, meta_b, None)
        assert res["ok"] is True
        assert 0.0 <= res["valid_fraction"] <= 1.0
        # 50x50 area on 100x100 grid is 0.25 valid_fraction
        assert np.isclose(res["valid_fraction"], 0.25)
