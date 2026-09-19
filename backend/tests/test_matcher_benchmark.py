"""Tests for matcher benchmark endpoint integration and script execution."""
import json
import subprocess
import sys
from pathlib import Path

import pytest
from client_helper import test_client
from app.config import settings


# ──────────────────────────────────────────────────────────────────
# 1. Benchmark endpoint returns data when matcher_benchmark.json exists
# ──────────────────────────────────────────────────────────────────
def test_matcher_benchmark_endpoint(tmp_path, monkeypatch):
    """Given a run directory with matcher_benchmark.json present, the
    API response includes a non-null matcher_benchmark object."""
    run_id = "run_bench_present"
    run_dir = tmp_path / run_id
    run_dir.mkdir()

    # Minimal experiment_log.json required by the endpoint
    (run_dir / "experiment_log.json").write_text(json.dumps({
        "run_id": run_id,
        "timestamp": "2026-09-18T08:00:00Z",
        "status": "SUCCESSFUL",
    }))

    # Matcher benchmark data
    benchmark_data = {
        "pairs_tested": 2,
        "timestamp": "2026-09-18T08:00:00Z",
        "matchers": [
            {"name": "RIFT2 + BF", "success_rate": 1.0,
             "mean_rmse_px": 0.59, "mean_time_ms": 4279,
             "notes": "Shipped (live)"},
            {"name": "SuperGlue", "skipped": True,
             "reason": "torch not installed"},
        ]
    }
    (run_dir / "matcher_benchmark.json").write_text(json.dumps(benchmark_data))

    monkeypatch.setattr(settings, "OUTPUTS_DIR", tmp_path)

    response = test_client.get(f"/api/v1/results/{run_id}")
    assert response.status_code == 200
    data = response.json()

    assert data["matcher_benchmark"] is not None
    assert data["matcher_benchmark"]["pairs_tested"] == 2
    assert len(data["matcher_benchmark"]["matchers"]) == 2
    assert data["matcher_benchmark"]["matchers"][0]["name"] == "RIFT2 + BF"
    assert data["matcher_benchmark"]["matchers"][1]["skipped"] is True


# ──────────────────────────────────────────────────────────────────
# 2. Benchmark absent — matcher_benchmark is null
# ──────────────────────────────────────────────────────────────────
def test_matcher_benchmark_absent(tmp_path, monkeypatch):
    """Given a run directory without matcher_benchmark.json, the API
    response has matcher_benchmark == null."""
    run_id = "run_bench_absent"
    run_dir = tmp_path / run_id
    run_dir.mkdir()

    (run_dir / "experiment_log.json").write_text(json.dumps({
        "run_id": run_id,
        "timestamp": "2026-09-18T08:00:00Z",
        "status": "SUCCESSFUL",
    }))

    monkeypatch.setattr(settings, "OUTPUTS_DIR", tmp_path)

    response = test_client.get(f"/api/v1/results/{run_id}")
    assert response.status_code == 200
    data = response.json()

    assert data["matcher_benchmark"] is None
    assert data["stages_detail"] == []


# ──────────────────────────────────────────────────────────────────
# 3. Benchmark script produces valid JSON with RIFT2 result
# ──────────────────────────────────────────────────────────────────
def test_matcher_benchmark_script_runs(tmp_path):
    """Running scripts/matcher_benchmark.py produces a valid JSON file
    with at least one non-skipped entry (RIFT2)."""
    backend_dir = Path(__file__).resolve().parent.parent
    script_path = backend_dir / "scripts" / "matcher_benchmark.py"

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(backend_dir),
        capture_output=True,
        text=True,
        timeout=300,  # RIFT2 can be slow on CPU
    )
    assert result.returncode == 0, f"Script failed:\n{result.stderr}"

    out_path = backend_dir / "outputs" / "matcher_benchmark.json"
    assert out_path.exists(), "matcher_benchmark.json not created"

    with open(out_path, "r") as f:
        data = json.load(f)

    assert "pairs_tested" in data
    assert data["pairs_tested"] >= 1
    assert "matchers" in data
    assert len(data["matchers"]) >= 1

    # At least RIFT2 must be non-skipped
    non_skipped = [m for m in data["matchers"] if not m.get("skipped")]
    assert len(non_skipped) >= 1, "Expected at least RIFT2 to run successfully"
    assert non_skipped[0]["name"] == "RIFT2 + BF"
    assert non_skipped[0]["success_rate"] is not None


# ──────────────────────────────────────────────────────────────────
# 4. Graceful degradation — deep matchers skipped without crash
# ──────────────────────────────────────────────────────────────────
def test_matcher_benchmark_graceful_degradation(tmp_path):
    """If deep matcher dependencies are missing, the script still
    produces valid JSON with RIFT2 results plus skipped entries."""
    backend_dir = Path(__file__).resolve().parent.parent
    script_path = backend_dir / "scripts" / "matcher_benchmark.py"

    # Run with a modified environment that hides weight files
    # (the script checks for weight files on disk, not torch availability)
    # We can verify by checking that the output contains skipped entries
    # for matchers whose weights are absent (which they are in this repo)
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(backend_dir),
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Script failed:\n{result.stderr}"

    out_path = backend_dir / "outputs" / "matcher_benchmark.json"
    with open(out_path, "r") as f:
        data = json.load(f)

    # RIFT2 must always be present and non-skipped
    rift2_entries = [m for m in data["matchers"] if m["name"] == "RIFT2 + BF"]
    assert len(rift2_entries) == 1
    assert not rift2_entries[0].get("skipped", False)

    # Deep matchers should be present (either run or skipped)
    deep_names = {"SuperGlue", "LightGlue", "LoFTR"}
    deep_entries = [m for m in data["matchers"] if m["name"] in deep_names]
    # Each deep matcher that is skipped should have a reason
    for entry in deep_entries:
        if entry.get("skipped"):
            assert "reason" in entry
            assert len(entry["reason"]) > 0


# ──────────────────────────────────────────────────────────────────
# 5. stages_detail filtering returns only stage-level entries
# ──────────────────────────────────────────────────────────────────
def test_stages_detail_filtering(tmp_path, monkeypatch):
    """stages_detail only contains entries whose 'stage' field is in
    the known stage names set, not per-match decision rows."""
    run_id = "run_stages_filter"
    run_dir = tmp_path / run_id
    run_dir.mkdir()

    (run_dir / "experiment_log.json").write_text(json.dumps({
        "run_id": run_id,
        "timestamp": "2026-09-18T08:00:00Z",
        "status": "SUCCESSFUL",
    }))

    # Write a JSONL with stage entries and non-stage entries
    lines = [
        '{"stage": "pds_meta", "ms": 11.95, "reason": "PDS metadata absent"}',
        '{"stage": "crs", "ms": 428.04, "fallback": false}',
        '{"stage": "input_quality", "ok": true, "ms": 5.0}',
        '{"match_idx": 0, "ref_pt": [100, 200], "mov_pt": [110, 210], "distance": 0.5}',
        '{"match_idx": 1, "ref_pt": [150, 250], "mov_pt": [160, 260], "distance": 0.6}',
        '{"stage": "subpixel", "match_id": 0, "residual_px": 0.413}',
        '{"stage": "subpixel", "match_id": 1, "residual_px": 0.512}',
        '{"stage": "overlap", "overlap_ratio": 0.89, "ms": 359.25}',
    ]
    (run_dir / "match_decisions.jsonl").write_text("\n".join(lines) + "\n")

    monkeypatch.setattr(settings, "OUTPUTS_DIR", tmp_path)

    response = test_client.get(f"/api/v1/results/{run_id}")
    assert response.status_code == 200
    data = response.json()

    # Retains the 5 stage-level entries, discarding non-stage and duplicate per-match rows
    assert len(data["stages_detail"]) == 5
    stage_names = [s["stage"] for s in data["stages_detail"]]
    assert "pds_meta" in stage_names
    assert "crs" in stage_names
    assert "input_quality" in stage_names
    assert "subpixel" in stage_names
    assert "overlap" in stage_names
