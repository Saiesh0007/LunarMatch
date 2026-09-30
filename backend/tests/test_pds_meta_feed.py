"""Tests for PDS metadata feed (F30).

Verifies that:
1. test_gsd_propagated: gsd_meters from PDS metadata propagates into request context,
   stage log, and scales ground residual in match_points.csv.
2. test_solar_angles_propagated: solar angles propagate and feed the F8 illumination
   stage when SPICE is unavailable.
3. test_missing_metadata: runs with no PDS metadata set fields to None with reason set.
4. test_determinism: identical inputs produce identical pds_meta stage records.
"""
import csv
import json
from unittest import mock
from pathlib import Path
import numpy as np
import pytest

from app.services.pipeline_service import PipelineService
from app.models.requests import PipelineRunRequest
from app.models.schemas import (
    FeatureMethod, MatcherType, GeometricModel, EstimatorMethod,
    SensorType, ExecutionMode
)


PDS_LABEL_TEMPLATE = """<Product_Observational xmlns='urn:test'>
  <Observation_Area>
    <Time_Coordinates><Start_Date_Time>2024-01-02T03:04:05Z</Start_Date_Time></Time_Coordinates>
    <Mission_Area>
      <Instrument_Id>OHRC</Instrument_Id>
      <Solar_Elevation>{solar_elevation}</Solar_Elevation>
      <Solar_Azimuth>{solar_azimuth}</Solar_Azimuth>
    </Mission_Area>
    <File_Area_Observational>
      <Array_2D_Image>
        <Lines>640</Lines>
        <Samples>640</Samples>
        <Pixel_Scale>{gsd}</Pixel_Scale>
      </Array_2D_Image>
    </File_Area_Observational>
  </Observation_Area>
</Product_Observational>"""


def _load_stage_entries(svc: PipelineService, run_id: str):
    out_dir = svc.outputs_dir / run_id
    jsonl_path = out_dir / "match_decisions.jsonl"
    assert jsonl_path.exists()
    entries = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    return entries, out_dir


def test_gsd_propagated(tmp_path):
    """Run pipeline with PDS metadata specifying gsd_meters=30.0."""
    label_file = tmp_path / "test_label.xml"
    label_file.write_text(
        PDS_LABEL_TEMPLATE.format(solar_elevation=42.5, solar_azimuth=120.0, gsd=30.0),
        encoding="utf-8"
    )

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
        pds_label_path=str(label_file),
    )

    svc = PipelineService()
    with mock.patch("spiceypy.str2et", side_effect=lambda x: 1.0 if "01Z" in x else 0.0):
        res = svc.execute_pipeline(req)

    assert res.execution_mode == ExecutionMode.LIVE
    entries, out_dir = _load_stage_entries(svc, res.run_id)

    pds_entry = next((e for e in entries if e.get("stage") == "pds_meta"), None)
    assert pds_entry is not None, "pds_meta stage entry missing from match_decisions.jsonl"
    assert pds_entry["gsd_meters"] == 30.0
    assert pds_entry["solar_elevation_deg"] == 42.5
    assert pds_entry["solar_azimuth_deg"] == 120.0

    csv_path = out_dir / "match_points.csv"
    assert csv_path.exists(), "match_points.csv missing"
    finite_matches = 0
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        assert "residual_pixels" in reader.fieldnames
        assert "residual_meters" in reader.fieldnames
        for row in reader:
            r_px = float(row["residual_pixels"])
            r_m = float(row["residual_meters"])
            if np.isfinite(r_px) and np.isfinite(r_m):
                assert np.isclose(r_m, r_px * 30.0, rtol=1e-3)
                finite_matches += 1

    assert finite_matches > 0, "Expected at least one finite residual pair in match_points.csv"


def test_solar_angles_propagated(tmp_path):
    """Assert solar elevation & azimuth propagate to F8 illumination stage when SPICE is unavailable."""
    label_file = tmp_path / "test_angles.xml"
    label_file.write_text(
        PDS_LABEL_TEMPLATE.format(solar_elevation=38.0, solar_azimuth=115.0, gsd=25.0),
        encoding="utf-8"
    )

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
        disable_spice=True,
        pds_label_path=str(label_file),
    )

    svc = PipelineService()
    res = svc.execute_pipeline(req)

    assert res.execution_mode == ExecutionMode.LIVE
    entries, _ = _load_stage_entries(svc, res.run_id)

    pds_entry = next((e for e in entries if e.get("stage") == "pds_meta"), None)
    assert pds_entry is not None
    assert pds_entry["solar_elevation_deg"] == 38.0
    assert pds_entry["solar_azimuth_deg"] == 115.0

    illum_entry = next((e for e in entries if e.get("stage") == "illumination"), None)
    assert illum_entry is not None, "illumination stage entry missing"
    assert illum_entry["source"] == "pds", f"Expected source='pds' when SPICE disabled, got {illum_entry.get('source')}"
    assert illum_entry["solar_elevation_a"] == 38.0
    assert illum_entry["solar_elevation_b"] == 38.0
    assert illum_entry["diff_deg"] == 0.0
    assert illum_entry["ok"] is True


def test_missing_metadata():
    """Run with no PDS metadata. Stage entry has None values and reason is set without crashing."""
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
    entries, out_dir = _load_stage_entries(svc, res.run_id)

    pds_entry = next((e for e in entries if e.get("stage") == "pds_meta"), None)
    assert pds_entry is not None, "pds_meta stage entry missing from match_decisions.jsonl"
    assert pds_entry["gsd_meters"] is None
    assert pds_entry["solar_elevation_deg"] is None
    assert pds_entry["solar_azimuth_deg"] is None
    assert pds_entry.get("reason") is not None, "Expected reason to be set when PDS metadata is missing"

    # Verify ground residual in match_points.csv is NaN
    csv_path = out_dir / "match_points.csv"
    assert csv_path.exists()
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            r_m = float(row["residual_meters"])
            assert np.isnan(r_m), f"Expected NaN residual_meters without GSD, got {r_m}"


def test_determinism(tmp_path):
    """Same input produces identical pds_meta stage log entry (ignoring ms)."""
    label_file = tmp_path / "det_label.xml"
    label_file.write_text(
        PDS_LABEL_TEMPLATE.format(solar_elevation=50.0, solar_azimuth=90.0, gsd=15.0),
        encoding="utf-8"
    )

    def run_once():
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
            pds_label_path=str(label_file),
        )
        svc = PipelineService()
        with mock.patch("spiceypy.str2et", side_effect=lambda x: 1.0 if "01Z" in x else 0.0):
            res = svc.execute_pipeline(req)
        entries, _ = _load_stage_entries(svc, res.run_id)
        return next(e for e in entries if e.get("stage") == "pds_meta")

    e1 = run_once()
    e2 = run_once()

    assert e1["stage"] == e2["stage"]
    assert e1["gsd_meters"] == e2["gsd_meters"] == 15.0
    assert e1["solar_elevation_deg"] == e2["solar_elevation_deg"] == 50.0
    assert e1["solar_azimuth_deg"] == e2["solar_azimuth_deg"] == 90.0
    assert e1.get("reason") == e2.get("reason")
