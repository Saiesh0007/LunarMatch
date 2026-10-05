"""Test that the pipeline gracefully handles insufficient matches instead of crashing."""
import sys
from pathlib import Path
import cv2
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.services.pipeline_service import PipelineService
from app.models.requests import PipelineRunRequest
from app.models.schemas import FeatureMethod, MatcherType, GeometricModel, EstimatorMethod
from tests.client_helper import test_client


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
    assert "insufficient" in (result.failure_reason or "").lower() or "not_reliable" in (result.failure_reason or "").lower() or "footprint" in (result.failure_reason or "").lower(), \
        f"Failure reason should mention insufficient matches or invalid footprint: {result.failure_reason}"


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


def test_pipeline_skips_footprint_gate_without_georeferencing(tmp_path):
    source = Path(__file__).resolve().parents[1] / "data" / "examples" / "pair_a_ref.png"
    image = cv2.imread(str(source), cv2.IMREAD_GRAYSCALE)
    reference_path = tmp_path / "reference.png"
    moving_path = tmp_path / "moving.png"
    assert cv2.imwrite(str(reference_path), image)
    assert cv2.imwrite(str(moving_path), image)

    req = PipelineRunRequest(
        reference_image_id=str(reference_path),
        moving_image_id=str(moving_path),
        reference_sensor="OHRC",
        moving_sensor="OHRC",
        feature_method=FeatureMethod.SIFT,
        matcher=MatcherType.BF,
        geometric_model=GeometricModel.HOMOGRAPHY,
    )
    result = PipelineService().execute_pipeline(req)

    assert any(stage.stage_number == 3 for stage in result.stages)
    assert not any(
        stage.details and "valid fraction below threshold" in stage.details
        for stage in result.stages
    )


def test_pipeline_returns_structured_rejection_for_invalid_input_quality(tmp_path):
    source = Path(__file__).resolve().parents[1] / "data" / "examples" / "pair_a_ref.png"
    image = cv2.imread(str(source), cv2.IMREAD_GRAYSCALE)
    # 85 % of the raster is empty padding -> valid footprint below the 25 % floor
    image[: int(image.shape[0] * 0.85), :] = 0
    reference_path = tmp_path / "reference.tif"
    moving_path = tmp_path / "moving.tif"
    assert cv2.imwrite(str(reference_path), image)
    assert cv2.imwrite(str(moving_path), image)

    req = PipelineRunRequest(
        reference_image_id=str(reference_path),
        moving_image_id=str(moving_path),
        reference_sensor="OHRC",
        moving_sensor="OHRC",
        feature_method=FeatureMethod.SIFT,
        matcher=MatcherType.BF,
        geometric_model=GeometricModel.HOMOGRAPHY,
    )
    response = test_client.post("/api/v1/pipeline/run", json=req.model_dump(mode="json"))

    assert response.status_code == 200, response.text
    result = response.json()
    assert result["status"] == "NOT_RELIABLE"
    assert result["metrics"]["confidence_level"] == "REJECTED"
    assert "invalid fraction" in result["failure_reason"]
    assert result["stages"][-1]["name"] == "METRICS"


if __name__ == "__main__":
    test_pipeline_handles_insufficient_matches_gracefully()
    print("test_pipeline_handles_insufficient_matches_gracefully: PASSED")
    test_pipeline_sift_pair_b_also_fails_gracefully()
    print("test_pipeline_sift_pair_b_also_fails_gracefully: PASSED")
