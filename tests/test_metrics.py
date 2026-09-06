import numpy as np

from src.metrics import compute_rmse, evaluate, format_metrics


def test_rmse_identity():
    pts_ref = np.float32([[10, 10], [20, 20], [30, 30]])
    pts_mov = pts_ref.copy()
    identity = np.float32([[1, 0, 0], [0, 1, 0]])
    rmse = compute_rmse(pts_ref, pts_mov, identity)
    assert rmse is not None
    assert abs(rmse) < 1e-4


def test_rmse_known_translation():
    pts_ref = np.float32([[15, 15], [25, 25]])
    pts_mov = np.float32([[10, 10], [20, 20]])
    transform = np.float32([[1, 0, 5], [0, 1, 5]])
    rmse = compute_rmse(pts_ref, pts_mov, transform)
    assert rmse is not None
    assert abs(rmse) < 1e-4


def test_rmse_empty():
    pts = np.float32([]).reshape(0, 2)
    transform = np.float32([[1, 0, 0], [0, 1, 0]])
    rmse = compute_rmse(pts, pts, transform)
    assert rmse is None


def test_evaluate():
    pts_ref = np.float32([[10, 10], [20, 20], [30, 30]])
    pts_mov = pts_ref.copy()
    inlier_mask = np.array([True, True, True])
    transform = np.float32([[1, 0, 0], [0, 1, 0]])
    metrics = evaluate(100, 90, 80, 50, 3, inlier_mask, pts_ref, pts_mov, transform, 0.5, 1.23)
    assert metrics["keypoints_ref"] == 100
    assert metrics["inlier_count"] == 3
    assert metrics["inlier_ratio"] == 3 / 50
    assert metrics["rmse"] is not None
    assert metrics["spatial_coverage"] == 0.5
    assert metrics["runtime"] == 1.23


def test_format_metrics():
    metrics = {"inlier_count": 10, "rmse": 1.2345, "spatial_coverage": None}
    text = format_metrics(metrics)
    assert "inlier_count: 10" in text
    assert "rmse: 1.2345" in text
    assert "spatial_coverage: N/A" in text
