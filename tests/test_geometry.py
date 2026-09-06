import numpy as np

from src.geometry import estimate, compute_inlier_stats


def test_estimate_affine_identity():
    pts = np.float32([[10, 10], [50, 10], [50, 50], [10, 50], [30, 30]])
    transform, mask = estimate(pts, pts, model="affine")
    assert transform is not None
    assert mask is not None
    expected = np.array([[1, 0, 0], [0, 1, 0]], dtype=np.float64)
    np.testing.assert_allclose(transform, expected, atol=1.0)


def test_estimate_homography():
    pts = np.float32([[10, 10], [90, 10], [90, 90], [10, 90], [50, 50]])
    transform, mask = estimate(pts, pts, model="homography")
    assert transform is not None
    assert transform.shape == (3, 3)


def test_estimate_too_few_points():
    pts = np.float32([[10, 10], [20, 20]])
    transform, mask = estimate(pts, pts)
    assert transform is None
    assert mask is None


def test_inlier_stats():
    mask = np.array([True, True, False, True, False])
    count, ratio = compute_inlier_stats(mask)
    assert count == 3
    assert abs(ratio - 0.6) < 1e-6


def test_inlier_stats_none():
    count, ratio = compute_inlier_stats(None)
    assert count == 0
    assert ratio == 0.0
