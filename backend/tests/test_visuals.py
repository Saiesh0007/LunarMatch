from pathlib import Path
import subprocess
import sys


def test_generate_visual_assets():
    root = Path(__file__).resolve().parents[2]
    output = root / "docs" / "visuals"
    command = [sys.executable, str(root / "backend/scripts/generate_visuals.py"), "--demo-pair-a", "--output", str(output)]
    result = subprocess.run(command, cwd=root / "backend", capture_output=True, text=True, timeout=180)
    assert result.returncode == 0, result.stderr
    for name in ("overlay_blink.gif", "match_points.png", "coverage_grid.png", "residual_heatmap.png", "sift_vs_rift2.png", "robustness_curves.png"):
        path = output / name
        assert path.exists() and path.stat().st_size > 0
