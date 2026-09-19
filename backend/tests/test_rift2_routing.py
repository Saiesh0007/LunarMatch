"""Tests for RIFT2 direct routing (F29).

Verifies that:
1. test_rift2_routes_live: Request with method="rift2" and is_demo_mode=False
   runs live; match_decisions.jsonl has {"stage": "rift2", "fallback": false}.
2. test_rift2_demo_when_explicit: Request with method="rift2" and is_demo_mode=True
   runs demo path; stage entry is still present with fallback=True.
3. test_other_methods_unaffected: Request with method="sift" still works as before.
4. test_rift2_descriptor_dim: Live rift2 route produces 216-dim descriptors (not 128).
"""
import json
from unittest import mock
import numpy as np
import pytest

from app.services.pipeline_service import PipelineService
from app.models.requests import PipelineRunRequest
from app.models.schemas import (
    FeatureMethod, MatcherType, GeometricModel, EstimatorMethod,
    SensorType, ExecutionMode
)
from app.vision.rift2 import RIFT2Extractor


def test_rift2_routes_live():
    """Request with method="rift2" and is_demo_mode=False runs live pipeline."""
    req = PipelineRunRequest(
        reference_image_id="demo_pair_a_ref",
        moving_image_id="demo_pair_a_mov",
        reference_sensor=SensorType.OHRC,
        moving_sensor=SensorType.TMC_2,
        feature_method=FeatureMethod.RIFT2,
        matcher=MatcherType.BF,
        geometric_model=GeometricModel.AFFINE,
        estimator_method=EstimatorMethod.MAGSAC,
        is_demo_mode=False,
    )
    svc = PipelineService()
    with mock.patch("spiceypy.str2et", side_effect=lambda x: 1.0 if "01Z" in x else 0.0):
        res = svc.execute_pipeline(req)

    assert res.execution_mode == ExecutionMode.LIVE
    out_dir = svc.outputs_dir / res.run_id
    jsonl_path = out_dir / "match_decisions.jsonl"
    assert jsonl_path.exists()

    entries = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))

    rift2_entry = next((e for e in entries if e.get("stage") == "rift2"), None)
    assert rift2_entry is not None, "rift2 stage missing from match_decisions.jsonl"
    assert rift2_entry.get("fallback") is False, f"Expected fallback=False, got {rift2_entry}"
    assert rift2_entry.get("descriptor_dim") == 216


def test_rift2_demo_when_explicit():
    """Request with method="rift2" and is_demo_mode=True runs demo pipeline."""
    req = PipelineRunRequest(
        reference_image_id="demo_pair_a_ref",
        moving_image_id="demo_pair_a_mov",
        reference_sensor=SensorType.OHRC,
        moving_sensor=SensorType.TMC_2,
        feature_method=FeatureMethod.RIFT2,
        matcher=MatcherType.BF,
        geometric_model=GeometricModel.AFFINE,
        estimator_method=EstimatorMethod.MAGSAC,
        is_demo_mode=True,
    )
    svc = PipelineService()
    res = svc.execute_pipeline(req)

    assert res.execution_mode == ExecutionMode.DEMO
    out_dir = svc.outputs_dir / res.run_id
    jsonl_path = out_dir / "match_decisions.jsonl"
    assert jsonl_path.exists()

    entries = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))

    rift2_entry = next((e for e in entries if e.get("stage") == "rift2"), None)
    assert rift2_entry is not None, "rift2 stage missing from demo match_decisions.jsonl"
    assert rift2_entry.get("fallback") is True


def test_other_methods_unaffected():
    """Request with method="sift" still works as before in live mode."""
    req = PipelineRunRequest(
        reference_image_id="demo_pair_a_ref",
        moving_image_id="demo_pair_a_mov",
        reference_sensor=SensorType.OHRC,
        moving_sensor=SensorType.TMC_2,
        feature_method=FeatureMethod.SIFT,
        matcher=MatcherType.BF,
        geometric_model=GeometricModel.AFFINE,
        estimator_method=EstimatorMethod.MAGSAC,
        is_demo_mode=False,
    )
    svc = PipelineService()
    with mock.patch("spiceypy.str2et", side_effect=lambda x: 1.0 if "01Z" in x else 0.0):
        res = svc.execute_pipeline(req)

    assert res.execution_mode == ExecutionMode.LIVE
    assert res.metrics is not None
    assert res.metrics.rmse_px is not None


def test_rift2_descriptor_dim():
    """Live RIFT2 extractor produces 216-dim descriptors."""
    # Test on a synthetic image crop
    rng = np.random.default_rng(42)
    test_img = (rng.uniform(0, 255, (256, 256))).astype(np.uint8)

    extractor = RIFT2Extractor(max_features=200)
    kps, desc = extractor.extract(test_img)

    assert desc is not None
    if len(desc) > 0:
        assert desc.shape[1] == 216, f"Expected 216-dim descriptor, got {desc.shape[1]}"
    else:
        # If no keypoints on pure noise, test on textured gradient
        yy, xx = np.mgrid[0:256, 0:256].astype(np.float32)
        textured = ((np.sin(xx / 10.0) + np.cos(yy / 10.0) + 2.0) * 60.0).astype(np.uint8)
        kps, desc = extractor.extract(textured)
        assert len(kps) > 0
        assert desc.shape[1] == 216
