import pytest
from client_helper import test_client

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
    assert data["execution_mode"] == "LIVE BASELINE"
    assert data["metrics"]["metric_mode"] == "MEASURED"
    assert len(data["stages"]) == 10
    assert data["outputs"]["registered_image_url"] is not None

def test_pipeline_run_simulation_mode():
    req_body = {
        "reference_image_id": "demo_pair_a_ref",
        "moving_image_id": "demo_pair_a_mov",
        "feature_method": "RIFT — SIMULATED",
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
    assert data["execution_mode"] == "DEMO SIMULATION"
    assert data["metrics"]["metric_mode"] == "SIMULATED"
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
