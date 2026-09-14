import json

import pytest
from client_helper import test_client
from app.config import settings

def test_demo_pairs_list():
    res = test_client.get("/api/v1/images/demo")
    assert res.status_code == 200
    pairs = res.json()
    assert len(pairs) >= 2
    assert "pair_a" in [p["pair_id"] for p in pairs]
    assert "SYNTHETIC PROTOTYPE" in pairs[0]["provenance_note"]

def test_pipeline_run_demo_pair_live_sift():
    req_body = {
        "reference_image_id": "demo_pair_a_ref",
        "moving_image_id": "demo_pair_a_mov",
        "reference_sensor": "OHRC",
        "moving_sensor": "TMC-2",
        "feature_method": "SIFT",
        "matcher": "BF",
        "ratio_threshold": 0.8,
        "geometric_model": "homography",
        "spatial_balancing": True,
        "grid_size": 6,
        "preprocessing": {
            "normalize": True,
            "clahe": True,
            "denoise": True
        },
        "simulation_mode": False
    }
    res = test_client.post("/api/v1/pipeline/run", json=req_body)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["SUCCESSFUL", "LOW_CONFIDENCE"]
    assert data["execution_mode"] == "LIVE"
    assert data["metrics"]["metric_mode"] == "MEASURED"
    assert len(data["stages"]) == 10
    assert data["outputs"]["registered_image_url"] is not None

def test_pipeline_run_simulation_mode():
    req_body = {
        "reference_image_id": "demo_pair_a_ref",
        "moving_image_id": "demo_pair_a_mov",
        "feature_method": "RIFT2",
        "matcher": "FLANN",
        "ratio_threshold": 0.75,
        "geometric_model": "homography",
        "spatial_balancing": True,
        "grid_size": 6,
        "simulation_mode": True
    }
    res = test_client.post("/api/v1/pipeline/run", json=req_body)
    assert res.status_code == 200
    data = res.json()
    assert data["execution_mode"] == "DEMO"
    assert data["metrics"]["metric_mode"] == "DEMO"
    assert data["metrics"]["simulation_seed"] == 26166

def test_pipeline_fail_safe_trigger():
    req_body = {
        "reference_image_id": "demo_pair_a_ref",
        "moving_image_id": "demo_pair_a_mov",
        "feature_method": "SIFT",
        "matcher": "BF",
        "fail_safe_override": True  # Force fail safe trigger
    }
    res = test_client.post("/api/v1/pipeline/run", json=req_body)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "NOT_RELIABLE"
    assert data["metrics"]["rmse_px"] is None
    assert "REGISTRATION NOT RELIABLE" in data["metrics"]["confidence_explanation"]


def test_run_report_is_downloadable_markdown(tmp_path, monkeypatch):
    run_id = "run_report_test"
    run_dir = tmp_path / run_id
    run_dir.mkdir()
    (run_dir / "experiment_log.json").write_text(json.dumps({
        "timestamp": "2026-09-07T08:00:00Z",
        "status": "SUCCESSFUL",
        "execution_mode": "LIVE",
        "reference_sensor": "OHRC",
        "moving_sensor": "TMC-2",
        "feature_method": "SIFT",
        "matcher": "BF",
        "geometric_model": "homography",
    }))
    (run_dir / "metrics.json").write_text(json.dumps({
        "rmse_px": 1.25,
        "inlier_ratio": 82.5,
        "ransac_inliers": 42,
        "spatial_coverage": 66.0,
        "spatial_coverage_before": 48.0,
        "confidence_score": 0.91,
        "metric_mode": "MEASURED",
    }))
    monkeypatch.setattr(settings, "OUTPUTS_DIR", tmp_path)

    response = test_client.get(f"/api/v1/results/{run_id}/report")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/markdown")
    assert response.headers["content-disposition"] == (
        f'attachment; filename=LunarMatch_Report_{run_id}.md'
    )
    assert "# LUNARMATCH" in response.text
    assert "REPROJECTION RMSE      : 1.2500 px" in response.text
