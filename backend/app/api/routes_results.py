import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse

from ..config import settings
from ..utils.file_utils import load_json

router = APIRouter(tags=["Results"])

# Known stage-level entry names in match_decisions.jsonl.
# Per-match decision rows are filtered out to keep the response lean (~20 entries).
_STAGE_NAMES = {
    "crs", "gsd_norm", "overlap", "input_quality",
    "spice_build", "spice", "footprint_validation", "illumination",
    "shadow", "terrain_corr", "radiometric_norm", "depth_optical",
    "scale_space", "rift2", "hypnet", "scdf_gates", "magsac",
    "tps", "subpixel", "pds_meta", "matching",
    "asift", "bspline", "pcsd", "selfsim", "cofsm", "msa",
    "illum_norm", "level_filter",
    "superpoint", "superglue", "lightglue",
}

@router.get("/api/v1/results/{run_id}")
@router.get("/api/runs/{run_id}")
def get_run_results(run_id: str):
    """Retrieve full persisted experiment log and metrics for a given run ID.

    Enriches the base experiment_log.json with:
    - stages_detail: stage-level entries parsed from match_decisions.jsonl
    - matcher_benchmark: static benchmark comparison data (null if absent)
    """
    run_dir = settings.OUTPUTS_DIR / run_id
    if not run_dir.exists():
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    log_path = run_dir / "experiment_log.json"
    if not log_path.exists():
        raise HTTPException(status_code=404, detail=f"Experiment log for {run_id} not found")

    result = load_json(log_path)

    # Enrich with stage-level entries from match_decisions.jsonl
    jsonl_path = run_dir / "match_decisions.jsonl"
    if jsonl_path.exists():
        seen_stages = set()
        stages_detail = []
        for line in jsonl_path.read_text(encoding="utf-8").strip().splitlines():
            if not line.strip():
                continue
            entry = json.loads(line)
            stage = entry.get("stage")
            if stage in _STAGE_NAMES:
                # Per-match repeated rows for magsac/subpixel: keep the first representative entry
                if stage in seen_stages and "match_id" in entry:
                    continue
                seen_stages.add(stage)
                stages_detail.append(entry)
        result["stages_detail"] = stages_detail
    else:
        result["stages_detail"] = []

    # Enrich with matcher benchmark comparison data
    benchmark_path = run_dir / "matcher_benchmark.json"
    result["matcher_benchmark"] = load_json(benchmark_path) if benchmark_path.exists() else None

    return result

@router.get("/api/v1/results/{run_id}/artifact/{filename}")
@router.get("/api/runs/{run_id}/artifacts/{key}")
def get_run_artifact(run_id: str, filename: str = None, key: str = None):
    """Stream generated image (registered.png, overlay.png, etc.) or JSON artifact."""
    artifact_name = filename or key
    if not artifact_name:
        raise HTTPException(status_code=400, detail="Artifact filename or key required")
    run_dir = settings.OUTPUTS_DIR / run_id
    artifact_path = run_dir / artifact_name
    
    # Path traversal protection
    if not artifact_path.resolve().is_relative_to(run_dir.resolve()):
        raise HTTPException(status_code=403, detail="Forbidden path")

    if not artifact_path.exists():
        raise HTTPException(status_code=404, detail=f"Artifact {artifact_name} for run {run_id} not found")

    if artifact_name.endswith(".json"):
        return JSONResponse(content=load_json(artifact_path))
    elif artifact_name.endswith(".png"):
        return FileResponse(path=str(artifact_path), media_type="image/png")
    else:
        return FileResponse(path=str(artifact_path))

@router.get("/api/v1/results/{run_id}/report")
@router.get("/api/runs/{run_id}/report")
def get_run_report(run_id: str):
    """Generate and return full formatted markdown report for a given run ID."""
    run_dir = settings.OUTPUTS_DIR / run_id
    if not run_dir.exists():
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    log_path = run_dir / "experiment_log.json"
    metrics_path = run_dir / "metrics.json"
    if not log_path.exists() or not metrics_path.exists():
        raise HTTPException(status_code=404, detail=f"Report artifacts for {run_id} not found")

    log_data = load_json(log_path)
    metrics_data = load_json(metrics_path)

    rmse = metrics_data.get('rmse_px')
    rmse_str = f"{rmse:.4f} px" if rmse is not None else "N/A (Rejected / Unreliable)"
    inlier_ratio = metrics_data.get('inlier_ratio', 0.0)
    inliers = metrics_data.get('ransac_inliers', 0)
    cov = metrics_data.get('spatial_coverage', 0.0)
    cov_pre = metrics_data.get('spatial_coverage_before', 0.0)
    score = metrics_data.get('confidence_score', 0.0) or 0.0

    report = f"""# LUNARMATCH — MISSION INSIGHT & REGISTRATION REPORT
{"=" * 76}
Smart India Hackathon 2026 | Problem Statement: 26166 | Organization: ISRO
Run ID: {run_id}
Timestamp: {log_data.get('timestamp', 'N/A')}
Status: {log_data.get('status', 'N/A')}
Execution Mode: {log_data.get('execution_mode', 'N/A')} ({metrics_data.get('metric_mode', 'N/A')})
{"-" * 76}

## 1. MISSION SENSOR & ALGORITHM METADATA
• Reference Sensor : {log_data.get('reference_sensor', 'N/A')} (Fixed Coordinate Frame)
• Moving Sensor    : {log_data.get('moving_sensor', 'N/A')} (Transformed Coordinate Frame)
• Feature Method   : {log_data.get('feature_method', 'N/A')}
• Feature Matcher  : {log_data.get('matcher', 'N/A')}
• Geometric Model  : {log_data.get('geometric_model', 'N/A')}
• Confidence Level : {metrics_data.get('confidence_level', 'N/A')} (Score: {score * 100:.1f}%)
• Explanation      : {metrics_data.get('confidence_explanation', 'N/A')}

## 2. PRIMARY QUANTITATIVE ACCURACY METRICS
{"-" * 76}
• REPROJECTION RMSE      : {rmse_str}
• RANSAC INLIER RATIO    : {inlier_ratio:.2f} %
• RANSAC INLIER COUNT    : {inliers} geometric consensus tie-points
• SPATIAL COVERAGE (POST): {cov:.2f} %
• SPATIAL COVERAGE (PRE) : {cov_pre:.2f} %
• NET COVERAGE GAIN      : +{max(0.0, cov - cov_pre):.2f} %
• TOTAL LATENCY          : {metrics_data.get('runtime_ms', 0.0):.1f} ms
{"-" * 76}

## 3. FEATURE EXTRACTION & MATCH BREAKDOWN
• Reference Keypoints : {metrics_data.get('keypoints_reference', 0)}
• Moving Keypoints    : {metrics_data.get('keypoints_moving', 0)}
• Candidate Matches   : {metrics_data.get('candidate_matches', 0)}
• Filtered Matches    : {metrics_data.get('filtered_matches', 0)}
• RANSAC Inliers      : {inliers}

{"=" * 76}
PIPELINE EXECUTION SUMMARY
{"=" * 76}
"""
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(
        content=report,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=LunarMatch_Report_{run_id}.md"}
    )
