import numpy as np
from unittest.mock import MagicMock

from src.spatial import spatial_balance, compute_coverage


def _make_mock_matches(n):
    matches = []
    for i in range(n):
        m = MagicMock()
        m.distance = float(i)
        matches.append(m)
    return matches


def test_spatial_balance_basic():
    pts_ref = np.float32([
        [10, 10], [20, 20], [150, 150], [180, 180], [50, 150],
    ])
    inlier_mask = np.array([True, True, True, True, True])
    matches = _make_mock_matches(5)
    selected = spatial_balance(pts_ref, matches, inlier_mask, (200, 200), grid_size=4, max_per_cell=2)
    assert len(selected) > 0
    assert len(selected) <= 5


def test_spatial_balance_no_inliers():
    pts_ref = np.float32([[10, 10], [20, 20]])
    inlier_mask = np.array([False, False])
    matches = _make_mock_matches(2)
    selected = spatial_balance(pts_ref, matches, inlier_mask, (200, 200))
    assert len(selected) == 0


def test_compute_coverage():
    pts = np.float32([[25, 25], [75, 75], [25, 75], [75, 25]])
    coverage = compute_coverage(pts, (100, 100), grid_size=2)
    assert coverage == 1.0


def test_compute_coverage_partial():
    pts = np.float32([[10, 10]])
    coverage = compute_coverage(pts, (100, 100), grid_size=4)
    assert coverage == 1 / 16


def test_compute_coverage_empty():
    pts = np.float32([]).reshape(0, 2)
    coverage = compute_coverage(pts, (100, 100))
    assert coverage == 0.0
