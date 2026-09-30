import json
import os

from app.config import settings
from tests.client_helper import test_client


def test_failure_case_skips_newer_run_without_quality_report(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "OUTPUTS_DIR", tmp_path)

    completed_run = tmp_path / "run_with_quality_report"
    completed_run.mkdir()
    (completed_run / "quality_report.json").write_text(json.dumps({
        "registration_decision": {
            "decision": "REGISTRATION_NOT_RELIABLE",
            "reason": "Insufficient inliers",
            "failed_criteria": ["inlier_count"],
            "checklist": {
                "inlier_count": {"value": 12, "threshold": 30, "pass": False}
            },
        },
        "n_inliers": 12,
        "subpixel": {"n_rejected_refinement": 2},
    }), encoding="utf-8")

    incomplete_run = tmp_path / "newer_run_without_quality_report"
    incomplete_run.mkdir()
    os.utime(completed_run, (1, 1))
    os.utime(incomplete_run, (2, 2))

    response = test_client.get("/api/demo/failure-case")

    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "REGISTRATION_NOT_RELIABLE"
    assert data["failed_criteria"] == ["inlier_count"]
    assert data["n_inliers"] == 12
    assert len(data["criteria"]) == 7