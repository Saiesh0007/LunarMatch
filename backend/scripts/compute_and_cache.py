"""Pre-compute real SIFT vs RIFT2 comparison results on Pair A and cache them.

This replaces the fabricated hard-coded SIFT baseline in routes_demo.py.
Run: python scripts/compute_and_cache.py
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.services.pipeline_service import PipelineService
from app.models.requests import PipelineRunRequest
from app.models.schemas import FeatureMethod, MatcherType, GeometricModel, EstimatorMethod
from app.utils.file_utils import to_json_serializable

ROOT = Path(__file__).resolve().parents[2]
CACHE_PATH = ROOT / "backend" / "data" / "demo" / "compare_result.json"


def run_method(feature_method: str, label: str):
    req = PipelineRunRequest(
        reference_image_id="demo_pair_a_ref",
        moving_image_id="demo_pair_a_mov",
        feature_method=feature_method,
        matcher=MatcherType.BF,
        geometric_model=GeometricModel.AFFINE,
        estimator_method=EstimatorMethod.MAGSAC,
    )
    svc = PipelineService()
    result = svc.execute_pipeline(req)
    from app.config import settings
    qr_path = settings.OUTPUTS_DIR / result.run_id / "quality_report.json"
    qr = json.loads(qr_path.read_text()) if qr_path.exists() else {}
    dec = qr.get("registration_decision", {})
    checklist = dec.get("checklist", {})
    n_in = qr.get("n_inliers", 0)
    rmse = checklist.get("rmse_pixels", {}).get("value")
    coverage = checklist.get("spatial_coverage", {}).get("value", 0.0)
    ratio_val = checklist.get("inlier_ratio", {}).get("value", 0.0)
    return {
        "status": result.status.value,
        "inliers": n_in,
        "rmse_px": rmse,
        "coverage": coverage,
        "inlier_ratio": ratio_val,
        "decision": dec.get("decision"),
        "quality_report": to_json_serializable(qr),
    }


def main():
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "pair_name": "Pair A: Demo alignment (sun azimuth 45° vs 55°, 10° delta)",
        "provenance": "REAL MEASURED — both SIFT and LunarMatch RIFT2 run through the full pipeline on the same pair",
        "sift": run_method("sift", "SIFT"),
        "lunarmatch": run_method("rift2_multiscale", "RIFT2"),
    }
    CACHE_PATH.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Cached to {CACHE_PATH}")
    print(json.dumps({k: v for k, v in result.items() if k not in ("sift", "lunarmatch")} | {k: {kk: vv for kk, vv in v.items() if kk != "quality_report"} for k, v in result.items() if k in ("sift", "lunarmatch")}, indent=2))


if __name__ == "__main__":
    main()
