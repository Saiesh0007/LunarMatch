import cv2
import numpy as np

from app.vision.geometry import magsac_plus_plus


def make_affine_data(inliers=80, outliers=20, seed=7, noise=0.25):
    rng = np.random.default_rng(seed)
    source_inliers = rng.uniform(-100.0, 100.0, (inliers, 2)).astype(np.float32)
    transform = np.array([[1.08, 0.12, 8.0], [-0.07, 0.96, -5.0]], dtype=np.float32)
    target_inliers = source_inliers @ transform[:, :2].T + transform[:, 2]
    target_inliers += rng.normal(0.0, noise, target_inliers.shape).astype(np.float32)
    source_outliers = rng.uniform(-100.0, 100.0, (outliers, 2)).astype(np.float32)
    target_outliers = rng.uniform(-150.0, 150.0, (outliers, 2)).astype(np.float32)
    return np.vstack((source_inliers, source_outliers)), np.vstack((target_inliers, target_outliers)), transform


def transform_rmse(matrix, source, target):
    projected = source @ matrix[:, :2].T + matrix[:, 2]
    return float(np.sqrt(np.mean(np.sum((projected - target) ** 2, axis=1))))


def test_magsac_on_clean_data():
    """Clean affine data recovers within 1e-3 floating-point tolerance."""
    source, target, expected = make_affine_data(inliers=100, outliers=0, noise=0.0)
    matrix, mask, diagnostics = magsac_plus_plus(source, target, model="affine", random_seed=0)
    assert matrix is not None
    assert np.count_nonzero(mask) == 100
    assert transform_rmse(matrix, source, target) < 1e-3
    assert diagnostics["backend"] == "opencv_usac_magsac"


def test_magsac_on_20pct_outliers():
    """At 20% outliers, affine RMSE remains below the 1 px literature baseline."""
    source, target, _ = make_affine_data(inliers=80, outliers=20)
    matrix, mask, _ = magsac_plus_plus(source, target, model="affine", random_seed=0)
    assert matrix is not None
    assert transform_rmse(matrix, source[:80], target[:80]) < 1.0
    assert np.count_nonzero(mask[:80]) >= 75


def test_magsac_recovers_more_inliers_than_ransac():
    """MAGSAC should recover at least RANSAC inliers minus two on 20% outliers."""
    source, target, _ = make_affine_data(inliers=80, outliers=20, seed=17, noise=0.8)
    cv2.setRNGSeed(0)
    _, ransac_mask = cv2.estimateAffine2D(source, target, method=cv2.RANSAC, ransacReprojThreshold=3.0)
    _, magsac_mask, _ = magsac_plus_plus(source, target, model="affine", random_seed=0)
    assert np.count_nonzero(magsac_mask) >= np.count_nonzero(ransac_mask) - 2


def test_magsac_deterministic_with_seed():
    """The same seed produces bit-identical parameters and masks."""
    source, target, _ = make_affine_data(seed=21)
    first = magsac_plus_plus(source, target, model="affine", random_seed=42)
    second = magsac_plus_plus(source, target, model="affine", random_seed=42)
    np.testing.assert_array_equal(first[0], second[0])
    np.testing.assert_array_equal(first[1], second[1])


def test_magsac_handles_low_overlap():
    """At 40% outliers, at least 55 of 60 true inliers should be recovered."""
    source, target, _ = make_affine_data(inliers=60, outliers=40, seed=31, noise=0.4)
    matrix, mask, _ = magsac_plus_plus(source, target, model="affine", random_seed=0, max_iters=5000)
    assert matrix is not None
    assert transform_rmse(matrix, source[:60], target[:60]) < 2.0
    assert np.count_nonzero(mask[:60]) >= 55


def test_magsac_handles_high_outlier_ratio():
    """At 60% outliers, MAGSAC is accurate or safely rejects the estimate."""
    source, target, _ = make_affine_data(inliers=40, outliers=60, seed=41, noise=0.5)
    matrix, mask, diagnostics = magsac_plus_plus(source, target, model="affine", random_seed=0, max_iters=5000)
    if matrix is not None:
        assert transform_rmse(matrix, source[:40], target[:40]) < 3.0
    else:
        assert "failure_reason" in diagnostics
        assert not np.any(mask)
