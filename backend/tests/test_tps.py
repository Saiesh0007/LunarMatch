"""Tests for F25 TPS Non-Rigid Residual Correction.

Papers: SCDF (arXiv 2608.22300v1), Sec. III-E; Bookstein 1989.
"""
import cv2
import numpy as np
import pytest

from app.services.tps import apply_tps, fit_tps


def test_identity_warp():
    """src_pts == dst_pts. TPS fit -> predictions equal to input within 1e-6 px."""
    rng = np.random.default_rng(26166)
    pts = rng.uniform(10.0, 500.0, (25, 2)).astype(np.float64)

    tps_fn = fit_tps(pts, pts, regularization=0.0)
    assert tps_fn is not None

    preds = tps_fn(pts)
    max_err = np.max(np.abs(preds - pts))
    assert max_err < 1e-6, f"Expected max error < 1e-6 px, got {max_err}"


def test_sinusoidal_warp():
    """Generate 200 points on a grid with smooth sinusoidal displacement.

    Fit TPS on 80% train, evaluate on 20% holdout: RMS residual < 0.5 px.
    """
    rng = np.random.default_rng(26166)
    gx, gy = np.meshgrid(np.linspace(20, 480, 15), np.linspace(20, 480, 14))
    src = np.column_stack([gx.ravel(), gy.ravel()])[:200].astype(np.float64)

    # Smooth sinusoidal displacement
    disp_x = 2.0 * np.sin(src[:, 1] / 60.0)
    disp_y = 1.5 * np.cos(src[:, 0] / 50.0)
    dst = src + np.column_stack([disp_x, disp_y])

    # 80/20 train/holdout split
    indices = np.arange(len(src))
    rng.shuffle(indices)
    split = int(0.8 * len(indices))
    train_idx, holdout_idx = indices[:split], indices[split:]

    tps_fn = fit_tps(src[train_idx], dst[train_idx], regularization=0.0)
    assert tps_fn is not None

    holdout_pred = tps_fn(src[holdout_idx])
    residuals = holdout_pred - dst[holdout_idx]
    rms = float(np.sqrt(np.mean(np.sum(residuals ** 2, axis=1))))

    assert rms < 0.5, f"Expected holdout RMS < 0.5 px, got {rms}"


def test_insufficient_inliers():
    """5 points (below threshold of 10). fit_tps returns None."""
    rng = np.random.default_rng(26166)
    pts = rng.uniform(10.0, 100.0, (5, 2)).astype(np.float64)

    result = fit_tps(pts, pts)
    assert result is None


def test_determinism():
    """Two runs with the same input produce byte-identical TPS output."""
    rng = np.random.default_rng(26166)
    src = rng.uniform(0.0, 500.0, (30, 2)).astype(np.float64)
    dst = src + rng.normal(0.0, 2.0, (30, 2)).astype(np.float64)

    fn1 = fit_tps(src, dst, regularization=0.0)
    fn2 = fit_tps(src, dst, regularization=0.0)
    assert fn1 is not None and fn2 is not None

    eval_pts = rng.uniform(50.0, 450.0, (50, 2)).astype(np.float64)
    out1 = fn1(eval_pts)
    out2 = fn2(eval_pts)

    assert np.array_equal(out1, out2)


def test_residual_computed_on_holdout():
    """Synthetic: 100 inliers + affine/homography projection with non-rigid deformation.

    Fit TPS on inliers only using 80/20 split.
    Assert residual_rms_after < residual_rms_before on the holdout set.
    """
    rng = np.random.default_rng(26166)
    src_inliers = rng.uniform(50.0, 450.0, (100, 2)).astype(np.float64)

    # Affine/homography transformation matrix
    H = np.array([
        [0.98, -0.04, 15.0],
        [0.04, 0.98, -10.0],
        [0.0001, 0.00005, 1.0],
    ], dtype=np.float64)

    proj = cv2.perspectiveTransform(src_inliers.reshape(-1, 1, 2), H).reshape(-1, 2)
    # Non-rigid deformation field
    deformation = np.column_stack([
        3.0 * np.sin(src_inliers[:, 1] / 50.0),
        2.5 * np.cos(src_inliers[:, 0] / 60.0),
    ])
    dst_inliers = proj + deformation

    # 80/20 train/holdout split
    indices = np.arange(len(src_inliers))
    rng.shuffle(indices)
    split = int(0.8 * len(indices))
    train_idx, holdout_idx = indices[:split], indices[split:]

    # Fit TPS on train inliers
    tps_fn = fit_tps(src_inliers[train_idx], dst_inliers[train_idx], regularization=0.0)
    assert tps_fn is not None

    # Before TPS residual (homography on holdout)
    proj_before = cv2.perspectiveTransform(src_inliers[holdout_idx].reshape(-1, 1, 2), H).reshape(-1, 2)
    residual_rms_before = float(np.sqrt(np.mean(np.sum((proj_before - dst_inliers[holdout_idx]) ** 2, axis=1))))

    # After TPS residual on the SAME holdout
    proj_after = tps_fn(src_inliers[holdout_idx])
    residual_rms_after = float(np.sqrt(np.mean(np.sum((proj_after - dst_inliers[holdout_idx]) ** 2, axis=1))))

    assert residual_rms_after < residual_rms_before, (
        f"Expected residual_rms_after ({residual_rms_after}) < residual_rms_before ({residual_rms_before})"
    )
    # Confirm honest evaluation on holdout (not trivially 0.0)
    assert residual_rms_after > 0.0
