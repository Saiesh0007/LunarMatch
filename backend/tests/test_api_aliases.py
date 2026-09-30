"""Tests for API route aliases (F31).

Verifies that:
1. test_runs_alias: GET /api/runs/{run_id} returns identical response to GET /api/v1/results/{run_id}.
2. test_artifacts_alias: GET /api/runs/{run_id}/artifacts/{key} returns identical response to
   GET /api/v1/results/{run_id}/artifact/{filename}.
3. test_report_alias: GET /api/runs/{run_id}/report returns identical response to GET /api/v1/results/{run_id}/report.
4. test_404_behavior: GET /api/runs/{nonexistent} returns 404 with identical body to GET /api/v1/results/{nonexistent}.
5. test_both_families_available: OpenAPI schema (/openapi.json) lists both /api/runs/* and /api/v1/results/* paths.
"""
import json
import shutil
import pytest
from app.config import settings
from tests.client_helper import test_client


@pytest.fixture
def mock_run():
    run_id = "run_alias_test_f31"
    run_dir = settings.OUTPUTS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    log_file = run_dir / "experiment_log.json"
    log_data = {
        "run_id": run_id,
        "timestamp": "2026-09-17T20:40:00Z",
        "status": "SUCCESS",
        "execution_mode": "LIVE",
        "reference_sensor": "OHRC",
        "moving_sensor": "TMC-2",
        "feature_method": "rift2",
        "matcher": "BF",
        "geometric_model": "AFFINE",
    }
    log_file.write_text(json.dumps(log_data), encoding="utf-8")

    metrics_file = run_dir / "metrics.json"
    metrics_data = {
        "metric_mode": "MEASURED",
        "rmse_px": 0.42,
        "inlier_ratio": 92.5,
        "ransac_inliers": 150,
        "spatial_coverage": 95.0,
        "spatial_coverage_before": 20.0,
        "confidence_score": 0.95,
        "confidence_level": "HIGH",
        "confidence_explanation": "Consensus match verified",
        "runtime_ms": 123.4,
        "keypoints_reference": 500,
        "keypoints_moving": 480,
        "candidate_matches": 300,
        "filtered_matches": 160,
    }
    metrics_file.write_text(json.dumps(metrics_data), encoding="utf-8")

    artifact_file = run_dir / "test_artifact.json"
    artifact_file.write_text(json.dumps({"artifact": "data", "status": "ok"}), encoding="utf-8")

    yield run_id

    shutil.rmtree(run_dir, ignore_errors=True)


def test_runs_alias(mock_run):
    """GET /api/runs/{run_id} returns the same body as GET /api/v1/results/{run_id}."""
    r_old = test_client.get(f"/api/v1/results/{mock_run}")
    r_new = test_client.get(f"/api/runs/{mock_run}")

    assert r_old.status_code == 200
    assert r_new.status_code == 200
    assert r_old.json() == r_new.json()


def test_artifacts_alias(mock_run):
    """GET /api/runs/{run_id}/artifacts/{key} returns the same body as GET /api/v1/results/{run_id}/artifact/{filename}."""
    r_old = test_client.get(f"/api/v1/results/{mock_run}/artifact/test_artifact.json")
    r_new = test_client.get(f"/api/runs/{mock_run}/artifacts/test_artifact.json")

    assert r_old.status_code == 200
    assert r_new.status_code == 200
    assert r_old.json() == r_new.json()


def test_report_alias(mock_run):
    """GET /api/runs/{run_id}/report returns the same body as GET /api/v1/results/{run_id}/report."""
    r_old = test_client.get(f"/api/v1/results/{mock_run}/report")
    r_new = test_client.get(f"/api/runs/{mock_run}/report")

    assert r_old.status_code == 200
    assert r_new.status_code == 200
    assert r_old.text == r_new.text


def test_404_behavior():
    """GET /api/runs/{nonexistent} returns 404 with the same body as GET /api/v1/results/{nonexistent}."""
    nonexistent = "run_does_not_exist_99999"
    r_old = test_client.get(f"/api/v1/results/{nonexistent}")
    r_new = test_client.get(f"/api/runs/{nonexistent}")

    assert r_old.status_code == 404
    assert r_new.status_code == 404
    assert r_old.json() == r_new.json()

    # Also test nonexistent artifact 404
    r_art_old = test_client.get(f"/api/v1/results/{nonexistent}/artifact/missing.png")
    r_art_new = test_client.get(f"/api/runs/{nonexistent}/artifacts/missing.png")
    assert r_art_old.status_code == 404
    assert r_art_new.status_code == 404
    assert r_art_old.json() == r_art_new.json()


def test_both_families_available():
    """OpenAPI schema (/openapi.json) lists both /api/runs/* and /api/v1/results/* paths."""
    r = test_client.get("/openapi.json")
    assert r.status_code == 200
    paths = r.json().get("paths", {})

    # Old family
    assert "/api/v1/results/{run_id}" in paths
    assert "/api/v1/results/{run_id}/artifact/{filename}" in paths
    assert "/api/v1/results/{run_id}/report" in paths

    # New alias family
    assert "/api/runs/{run_id}" in paths
    assert "/api/runs/{run_id}/artifacts/{key}" in paths
    assert "/api/runs/{run_id}/report" in paths
