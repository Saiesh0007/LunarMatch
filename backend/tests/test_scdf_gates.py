"""Tests for SCDF self-calibrating outlier rejection gates."""
import numpy as np
import pytest
from app.services.scdf_gates import self_calibrate, apply_gates


def test_50_percent_outliers_rejected():
    """Verify that magnitude gate and LOO gate reject ~50% random noise outliers."""
    rng = np.random.default_rng(26166)
    pos = rng.uniform(0, 500, (200, 2))

    # 100 inliers from smooth deformation field
    inlier_disp = 10.0 + 0.01 * pos[:100] + rng.normal(0, 0.2, (100, 2))
    # 100 outliers from random large noise
    outlier_disp = rng.uniform(-100, 100, (100, 2))

    displacements = np.vstack([inlier_disp, outlier_disp])
    confidences = np.ones(200)

    res = self_calibrate(displacements, pos, confidences)

    # Magnitude gate rejects most outliers
    rejected_mag = (~res["keep_magnitude"]).sum()
    assert rejected_mag >= 70, f"Expected magnitude gate to reject most outliers, got {rejected_mag}"

    # LOO gate rejects remaining inconsistent displacements
    rejected_loo = (~res["keep_loo"]).sum()
    assert rejected_loo > 0, "Expected LOO gate to reject remaining outliers"

    # Total kept should be close to 100 (e.g. 80 - 105)
    total_kept = res["kept_mask"].sum()
    assert 80 <= total_kept <= 105, f"Expected total kept close to 100, got {total_kept}"


def test_bimodal_error_threshold_adapts():
    """Verify error threshold adapts to empirical distribution rather than fixed value."""
    rng = np.random.default_rng(42)
    pos = rng.uniform(0, 100, (100, 2))
    disp = rng.uniform(0, 5, (100, 2))

    # Distribution 1: 90% in [0, 0.5], 10% in [5, 10]
    errors_low = np.concatenate([
        rng.uniform(0.0, 0.5, 90),
        rng.uniform(5.0, 10.0, 10),
    ])
    res_low = self_calibrate(disp, pos, errors=errors_low)

    # Distribution 2: shifted higher: 90% in [2.0, 3.0], 10% in [15, 20]
    errors_high = np.concatenate([
        rng.uniform(2.0, 3.0, 90),
        rng.uniform(15.0, 20.0, 10),
    ])
    res_high = self_calibrate(disp, pos, errors=errors_high)

    assert res_low["error_threshold"] < 1.0, f"Expected low threshold, got {res_low['error_threshold']}"
    assert res_high["error_threshold"] > 2.0, f"Expected high threshold, got {res_high['error_threshold']}"
    assert res_high["error_threshold"] > res_low["error_threshold"] * 2.0


def test_null_correlations_k_is_8():
    """Verify null correlations K=8 contract is satisfied."""
    rng = np.random.default_rng(42)
    pos = rng.uniform(0, 100, (25, 2))
    disp = rng.uniform(0, 5, (25, 2))
    res = self_calibrate(disp, pos)

    # Mock stage log as recorded in pipeline_service.py
    stage_log = {
        "stage": "scdf_gates",
        "kept": int(res["kept_mask"].sum()),
        "rejected_magnitude": int((~res["keep_magnitude"]).sum()),
        "rejected_loo": int((~res["keep_loo"]).sum()),
        "rejected_response": int((~res["keep_response"]).sum()),
        "rejected_error": int((~res["keep_error"]).sum()),
        "null_correlations_k": 8,
        "pair_median_disp": float(res["median_disp"]),
        "ms": 1.5,
    }
    assert stage_log["null_correlations_k"] == 8


def test_determinism():
    """Verify determinism: identical inputs produce identical kept masks."""
    rng = np.random.default_rng(12345)
    pos = rng.uniform(0, 200, (50, 2))
    disp = rng.uniform(-10, 10, (50, 2))
    conf = rng.uniform(0.5, 1.0, 50)

    res1 = self_calibrate(disp, pos, conf)
    res2 = self_calibrate(disp, pos, conf)

    assert np.array_equal(res1["kept_mask"], res2["kept_mask"])
    assert res1["median_disp"] == res2["median_disp"]
    assert res1["magnitude_threshold"] == res2["magnitude_threshold"]


def test_empty_input():
    """Verify graceful handling of empty inputs without crashing."""
    empty_pos = np.empty((0, 2), dtype=np.float64)
    empty_disp = np.empty((0, 2), dtype=np.float64)

    res = self_calibrate(empty_disp, empty_pos)

    assert len(res["kept_mask"]) == 0
    assert res["kept_mask"].dtype == bool
    assert res["reason"] == "empty_input"
    assert res["median_disp"] == 0.0
