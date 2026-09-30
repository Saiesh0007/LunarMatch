"""Integration tests for learned matchers in the LunarMatch pipeline."""

import json
from pathlib import Path
from unittest import mock
import pytest

from app.services.pipeline_service import PipelineService
from app.models.requests import PipelineRunRequest
from app.models.schemas import (
    FeatureMethod, MatcherType, GeometricModel, EstimatorMethod,
    SensorType
)


def _load_decisions(run_res):
    out_dir = Path("outputs") / run_res.run_id
    dec_file = out_dir / "match_decisions.jsonl"
    assert dec_file.exists(), f"Decisions file missing at {dec_file}"
    entries = []
    with open(dec_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    return entries


def test_default_rift2_pipeline_unaffected():
    """Verify default RIFT2 pipeline is unaffected and produces standard stages."""
    svc = PipelineService()
    req = PipelineRunRequest(
        reference_image_id="demo_pair_a_ref",
        moving_image_id="demo_pair_a_mov",
        reference_sensor=SensorType.OHRC,
        moving_sensor=SensorType.TMC_2,
        feature_method=FeatureMethod.RIFT2,
        matcher=MatcherType.BF,
        geometric_model=GeometricModel.AFFINE,
        estimator_method=EstimatorMethod.MAGSAC,
        spatial_balancing=True,
        grid_size=6,
    )
    with mock.patch("spiceypy.str2et", side_effect=lambda x: 1.0 if "01Z" in x else 0.0):
        res = svc.execute_pipeline(req)

    decisions = _load_decisions(res)
    stages = [d.get("stage") for d in decisions if "stage" in d]

    assert "rift2" in stages
    assert "matching" in stages
    assert "superpoint" not in stages
    assert "superglue" not in stages
    assert "lightglue" not in stages


def test_pipeline_superpoint_feature_method():
    """Verify selecting SuperPoint produces a superpoint stage entry."""
    svc = PipelineService()
    req = PipelineRunRequest(
        reference_image_id="demo_pair_a_ref",
        moving_image_id="demo_pair_a_mov",
        reference_sensor=SensorType.OHRC,
        moving_sensor=SensorType.TMC_2,
        feature_method=FeatureMethod.SUPERPOINT,
        matcher=MatcherType.BF,
        geometric_model=GeometricModel.AFFINE,
        estimator_method=EstimatorMethod.MAGSAC,
        max_features=500,
    )
    with mock.patch("spiceypy.str2et", side_effect=lambda x: 1.0 if "01Z" in x else 0.0):
        res = svc.execute_pipeline(req)

    decisions = _load_decisions(res)
    sp_entry = next((d for d in decisions if d.get("stage") == "superpoint"), None)
    assert sp_entry is not None, f"Expected superpoint stage in decisions, got {decisions}"
    assert sp_entry.get("applied") is True
    assert sp_entry.get("descriptor_dim") == 256


def test_pipeline_superglue_matcher():
    """Verify selecting SuperGlue matcher produces a superglue stage entry."""
    svc = PipelineService()
    req = PipelineRunRequest(
        reference_image_id="demo_pair_a_ref",
        moving_image_id="demo_pair_a_mov",
        reference_sensor=SensorType.OHRC,
        moving_sensor=SensorType.TMC_2,
        feature_method=FeatureMethod.RIFT2,
        matcher=MatcherType.SUPERGLUE,
        geometric_model=GeometricModel.AFFINE,
        estimator_method=EstimatorMethod.MAGSAC,
        max_features=500,
    )
    with mock.patch("spiceypy.str2et", side_effect=lambda x: 1.0 if "01Z" in x else 0.0):
        res = svc.execute_pipeline(req)

    decisions = _load_decisions(res)
    sg_entry = next((d for d in decisions if d.get("stage") == "superglue"), None)
    assert sg_entry is not None, f"Expected superglue stage in decisions, got {decisions}"
    assert sg_entry.get("applied") is True
    assert "n_matches" in sg_entry


def test_pipeline_lightglue_matcher():
    """Verify selecting LightGlue matcher produces a lightglue stage entry."""
    svc = PipelineService()
    req = PipelineRunRequest(
        reference_image_id="demo_pair_a_ref",
        moving_image_id="demo_pair_a_mov",
        reference_sensor=SensorType.OHRC,
        moving_sensor=SensorType.TMC_2,
        feature_method=FeatureMethod.RIFT2,
        matcher=MatcherType.LIGHTGLUE,
        geometric_model=GeometricModel.AFFINE,
        estimator_method=EstimatorMethod.MAGSAC,
        max_features=500,
    )
    with mock.patch("spiceypy.str2et", side_effect=lambda x: 1.0 if "01Z" in x else 0.0):
        res = svc.execute_pipeline(req)

    decisions = _load_decisions(res)
    lg_entry = next((d for d in decisions if d.get("stage") == "lightglue"), None)
    assert lg_entry is not None, f"Expected lightglue stage in decisions, got {decisions}"
    assert lg_entry.get("applied") is True
    assert "n_matches" in lg_entry


def test_pipeline_missing_weights_fallback():
    """Verify that missing weights degrade gracefully with fallback=True."""
    svc = PipelineService()
    req = PipelineRunRequest(
        reference_image_id="demo_pair_a_ref",
        moving_image_id="demo_pair_a_mov",
        reference_sensor=SensorType.OHRC,
        moving_sensor=SensorType.TMC_2,
        feature_method=FeatureMethod.RIFT2,
        matcher=MatcherType.SUPERGLUE,
        geometric_model=GeometricModel.AFFINE,
        estimator_method=EstimatorMethod.MAGSAC,
        max_features=500,
    )
    orig_is_file = Path.is_file

    def mock_is_file(self):
        if "superglue" in str(self):
            return False
        return orig_is_file(self)

    with mock.patch.object(Path, "is_file", mock_is_file):
        with mock.patch("spiceypy.str2et", side_effect=lambda x: 1.0 if "01Z" in x else 0.0):
            res = svc.execute_pipeline(req)

    decisions = _load_decisions(res)
    sg_entry = next((d for d in decisions if d.get("stage") == "superglue"), None)
    assert sg_entry is not None, f"Expected superglue entry in decisions: {decisions}"
    assert sg_entry.get("applied") is False
    assert sg_entry.get("fallback") is True
    assert "reason" in sg_entry


def test_pipeline_lock_to_default():
    """Verify lock_to_default=True forces RIFT2 and BF even if SuperPoint/SuperGlue requested."""
    svc = PipelineService()
    req = PipelineRunRequest(
        reference_image_id="demo_pair_a_ref",
        moving_image_id="demo_pair_a_mov",
        reference_sensor=SensorType.OHRC,
        moving_sensor=SensorType.TMC_2,
        feature_method=FeatureMethod.SUPERPOINT,
        matcher=MatcherType.SUPERGLUE,
        lock_to_default=True,
    )
    with mock.patch("spiceypy.str2et", side_effect=lambda x: 1.0 if "01Z" in x else 0.0):
        res = svc.execute_pipeline(req)

    decisions = _load_decisions(res)
    stages = [d.get("stage") for d in decisions if "stage" in d]
    assert "rift2" in stages
    assert "matching" in stages
    assert "superpoint" not in stages
    assert "superglue" not in stages

