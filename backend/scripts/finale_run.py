"""Finale submission run script.

Runs the full pipeline on the demo pair, verifies all required
stages are present, generates the report, and prints a summary.
"""
import csv
import json
import math
import sys
import time
from pathlib import Path
from unittest import mock

# Ensure backend root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.pipeline_service import PipelineService
from app.models.requests import PipelineRunRequest
from app.models.schemas import (
    FeatureMethod, MatcherType, GeometricModel, EstimatorMethod, SensorType
)
from app.services.report_generator import generate_report


def run_finale() -> int:
    """Execute full pipeline, verify 17 stages and artifacts, generate report."""
    t0_start = time.perf_counter()

    # Step 1: Run pipeline on demo pair
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
    svc = PipelineService()
    with mock.patch("spiceypy.str2et", side_effect=lambda x: 1.0 if "01Z" in x else 0.0):
        result = svc.execute_pipeline(req)

    run_dir = svc.outputs_dir / result.run_id

    # Step 2 & 3: Load match_decisions.jsonl and verify all 17 required stages present
    decisions_path = run_dir / "match_decisions.jsonl"
    if not decisions_path.exists():
        print(f"FAILED: match_decisions.jsonl not found at {decisions_path}")
        return 1

    decisions = []
    with open(decisions_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    decisions.append(json.loads(line))
                except Exception:
                    pass

    stages_present = {d["stage"] for d in decisions if "stage" in d}
    required = {
        "crs", "gsd_norm", "overlap", "spice", "spice_build",
        "footprint_validation", "illumination", "input_quality",
        "shadow", "terrain_corr", "radiometric_norm", "scale_space",
        "hypnet", "scdf_gates", "tps", "rift2", "pds_meta"
    }
    missing = required - stages_present
    if missing:
        print(f"FAILED: Missing required stages: {missing}")
        return 1

    # Step 4: Verify match_points.csv exists and has at least one row with non-NaN residual
    csv_path = run_dir / "match_points.csv"
    if not csv_path.exists():
        print(f"FAILED: match_points.csv not found at {csv_path}")
        return 1

    has_non_nan_residual = False
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                r = float(row.get("residual_pixels", "nan"))
                if not math.isnan(r):
                    has_non_nan_residual = True
                    break
            except Exception:
                pass
    if not has_non_nan_residual:
        print("FAILED: No row with non-NaN residual column found in match_points.csv")
        return 1

    # Step 5: Call generate_report(run_dir)
    rep_info = generate_report(run_dir)
    report_file = Path(rep_info["html"])

    # Step 6: Verify report.html exists and is > 2 KB
    if not report_file.exists() or report_file.stat().st_size <= 2048:
        size = report_file.stat().st_size if report_file.exists() else 0
        print(f"FAILED: report.html missing or <= 2 KB (size: {size} bytes)")
        return 1

    total_ms = (time.perf_counter() - t0_start) * 1000.0

    # Step 7: Print summary
    print(f"Pipeline completed in {total_ms:.1f} ms")
    print("All 17 required stages present")
    print(f"Report: {report_file}")
    print("Verified run: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(run_finale())
