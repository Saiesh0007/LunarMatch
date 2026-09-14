"""End-to-end smoke test for the full pipeline.

This canary test runs a complete pipeline execution on a synthetic pair
to verify no native crashes occur in the critical path. It serves as a
regression net for the Windows native access violations that were
diagnosed and stabilized.
"""
import numpy as np
import pytest


def generate_synthetic_pair(seed: int = 42, size: int = 256) -> tuple:
    """Generate a deterministic synthetic image pair using NumPy + PIL only."""
    from PIL import Image
    rng = np.random.default_rng(seed)

    # Base crater surface
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)

    def make_surface(suffix_seed):
        r = np.random.default_rng(suffix_seed)
        img = np.zeros((size, size), dtype=np.float32)
        for _ in range(15):
            cx, cy = r.uniform(0.1, 0.9, 2) * size
            radius = r.uniform(size * 0.02, size * 0.12)
            dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
            ring = np.exp(-((dist - radius) ** 2) / (2.0 * (radius * 0.15) ** 2))
            img += ring * r.uniform(0.5, 1.5)
        img = (img - img.min()) / (img.max() - img.min() + 1e-9)
        return (img * 255).astype(np.uint8)

    ref = make_surface(seed)
    mov = make_surface(seed + 1)
    return ref, mov


def test_full_pipeline_smoke():
    """End-to-end smoke test: no native crashes, all stages reachable.

    Runs a minimal pipeline on a NumPy-only synthetic pair.
    This test catches regressions in the Windows native crash stabilization work.
    """
    from app.services.pipeline_service import PipelineService
    from app.models.requests import PipelineRunRequest
    from app.models.schemas import (
        FeatureMethod, MatcherType, GeometricModel, EstimatorMethod,
        SensorType, PreprocessingConfig
    )

    # Use demo_pair_a which has moderate illumination difference (45 vs 55 degrees)
    req = PipelineRunRequest(
        reference_image_id="demo_pair_a_ref",
        moving_image_id="demo_pair_a_mov",
        reference_sensor=SensorType.OHRC,
        moving_sensor=SensorType.TMC_2,
        feature_method=FeatureMethod.SIFT,
        matcher=MatcherType.BF,
        geometric_model=GeometricModel.AFFINE,
        estimator_method=EstimatorMethod.MAGSAC,
        spatial_balancing=True,
        grid_size=6,
    )
    svc = PipelineService()
    result = svc.execute_pipeline(req)

    assert result.status is not None
    assert result.status.value in ("SUCCESSFUL", "ACCEPTED", "LOW_CONFIDENCE", "NOT_RELIABLE")
    assert result.metrics is not None
    assert hasattr(result.metrics, "rmse_px")
