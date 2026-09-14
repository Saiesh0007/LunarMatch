"""Test that the pipeline gracefully handles insufficient matches instead of crashing."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.services.pipeline_service import PipelineService
from app.models.requests import PipelineRunRequest
from app.models.schemas import FeatureMethod, MatcherType, GeometricModel, EstimatorMethod


def test_pipeline_handles_insufficient_matches_gracefully():
    """Pipeline returns NOT_RELIABLE, does not crash, on pairs with too few matches.

    This is a regression test for the crash in magsac_plus_plus() when
    filtered_matches is empty (np.asarray([]) creates a 1-D array that
    fails the shape check in geometry.py).
    """
    req = PipelineRunRequest(
        reference_image_id="demo_pair_b_ref",
        moving_image_id="demo_pair_b_mov",
        feature_method=FeatureMethod.RIFT2_MULTISCALE,
        matcher=MatcherType.BF,
        geometric_model=GeometricModel.AFFINE,
        estimator_method=EstimatorMethod.MAGSAC,
    )
    svc = PipelineService()

    result = svc.execute_pipeline(req)

    assert result.status is not None, "Pipeline should return a result, not crash"
    assert result.status.value == "NOT_RELIABLE", f"Expected NOT_RELIABLE, got {result.status.value}"
    assert result.failure_reason is not None, "Should have a failure reason"
    assert "insufficient" in (result.failure_reason or "").lower() or "not_reliable" in (result.failure_reason or "").lower(), \
        f"Failure reason should mention insufficient matches: {result.failure_reason}"


def test_pipeline_sift_pair_b_also_fails_gracefully():
    """SIFT on the challenging Pair B should also fail gracefully (not crash)."""
    req = PipelineRunRequest(
        reference_image_id="demo_pair_b_ref",
        moving_image_id="demo_pair_b_mov",
        feature_method=FeatureMethod.SIFT,
        matcher=MatcherType.BF,
        geometric_model=GeometricModel.AFFINE,
        estimator_method=EstimatorMethod.MAGSAC,
    )
    svc = PipelineService()
    result = svc.execute_pipeline(req)
    assert result.status.value in ("NOT_RELIABLE", "FAILED"), f"Expected graceful failure, got {result.status.value}"


if __name__ == "__main__":
    test_pipeline_handles_insufficient_matches_gracefully()
    print("test_pipeline_handles_insufficient_matches_gracefully: PASSED")
    test_pipeline_sift_pair_b_also_fails_gracefully()
    print("test_pipeline_sift_pair_b_also_fails_gracefully: PASSED")
