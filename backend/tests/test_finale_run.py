"""Tests for F34 Finale Run Script."""
import json
import subprocess
import sys
import time
from pathlib import Path
import pytest

from app.config import settings


@pytest.fixture(scope="module")
def executed_finale():
    """Run scripts/finale_run.py once via subprocess and capture duration and output."""
    t0 = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, "scripts/finale_run.py"],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).resolve().parent.parent)
    )
    wall_ms = (time.perf_counter() - t0) * 1000.0

    # Locate the run directory reported in stdout
    report_path = None
    run_dir = None
    for line in proc.stdout.splitlines():
        if line.startswith("Report:"):
            report_path = Path(line.split("Report:", 1)[1].strip())
            run_dir = report_path.parent
            break

    return {
        "proc": proc,
        "wall_ms": wall_ms,
        "report_path": report_path,
        "run_dir": run_dir,
    }


def test_finale_run_completes(executed_finale):
    """Running scripts/finale_run.py exits with code 0."""
    proc = executed_finale["proc"]
    assert proc.returncode == 0, f"finale_run.py failed with code {proc.returncode}:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    assert "Verified run: PASS" in proc.stdout


def test_finale_run_creates_report(executed_finale):
    """After finale_run.py, report.html exists in the run directory and is > 2 KB."""
    report_path = executed_finale["report_path"]
    assert report_path is not None, "Report path not printed in finale_run.py stdout"
    assert report_path.exists(), f"report.html not found at {report_path}"
    assert report_path.stat().st_size > 2048, f"report.html is too small: {report_path.stat().st_size} bytes"


def test_finale_run_all_stages(executed_finale):
    """The run's match_decisions.jsonl contains all 17 required stages."""
    run_dir = executed_finale["run_dir"]
    assert run_dir is not None and run_dir.exists()
    decisions_file = run_dir / "match_decisions.jsonl"
    assert decisions_file.exists()

    decisions = []
    with open(decisions_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    decisions.append(json.loads(line))
                except Exception:
                    pass

    stages = {d["stage"] for d in decisions if "stage" in d}
    required = {
        "crs", "gsd_norm", "overlap", "spice", "spice_build",
        "footprint_validation", "illumination", "input_quality",
        "shadow", "terrain_corr", "radiometric_norm", "scale_space",
        "hypnet", "scdf_gates", "tps", "rift2", "pds_meta"
    }
    missing = required - stages
    assert not missing, f"Missing required stages: {missing}"


def test_finale_run_under_budget(executed_finale):
    """The run completes in under budget wall-clock."""
    wall_ms = executed_finale["wall_ms"]
    assert wall_ms < 35000.0, f"finale_run.py exceeded wall-clock budget: {wall_ms:.1f} ms"
