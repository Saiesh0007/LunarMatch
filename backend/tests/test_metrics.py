import numpy as np
import pytest
from app.models.schemas import (
    MatchPairModel,
    RegistrationStatus,
    ConfidenceLevel,
    GeometricModel,
    MetricMode,
)
from app.vision.metrics import MetricsCalculator

def test_metrics_reprojection_rmse():
    # Identity transform
    H = np.eye(3, dtype=np.float32)
    inliers = [
        MatchPairModel(ref_idx=0, mov_idx=0, distance=1.0, ref_pt=[10.0, 10.0], mov_pt=[10.0, 10.0], is_inlier=True),
        MatchPairModel(ref_idx=1, mov_idx=1, distance=1.0, ref_pt=[50.0, 50.0], mov_pt=[50.0, 50.0], is_inlier=True),
        MatchPairModel(ref_idx=2, mov_idx=2, distance=1.0, ref_pt=[100.0, 20.0], mov_pt=[100.0, 20.0], is_inlier=True),
    ]
    rmse = MetricsCalculator.calculate_reprojection_rmse(inliers, H, GeometricModel.HOMOGRAPHY)
    assert rmse == 0.0

def test_metrics_fail_safe_low_inliers():
    status, metrics, reason = MetricsCalculator.evaluate_registration(
        kps_ref_count=100,
        kps_mov_count=100,
        candidate_count=50,
        filtered_count=20,
        inliers=[
            MatchPairModel(ref_idx=0, mov_idx=0, distance=1.0, ref_pt=[10.0, 10.0], mov_pt=[10.0, 10.0], is_inlier=True),
            MatchPairModel(ref_idx=1, mov_idx=1, distance=1.0, ref_pt=[20.0, 20.0], mov_pt=[20.0, 20.0], is_inlier=True),
        ],  # Only 2 inliers < 8 threshold
        matrix=np.eye(3, dtype=np.float32),
        spatial_coverage_before=10.0,
        spatial_coverage_after=10.0,
        runtime_ms=25.0,
        is_matrix_stable=True,
        matrix_msg="Stable",
    )
    assert status == RegistrationStatus.NOT_RELIABLE
    assert metrics.confidence_level == ConfidenceLevel.REJECTED
    assert metrics.rmse_px is None  # Reported as N/A on rejection
    assert "8 minimum threshold" in reason
