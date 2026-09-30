"""Tests for F34 Report Generator."""
import json
from pathlib import Path
import pytest

from app.services.report_generator import generate_report, _check_no_banned_strings
from app.config import settings


@pytest.fixture(scope="module")
def latest_run_dir():
    """Locate the most recent run directory that contains match_decisions.jsonl."""
    runs = sorted(
        [d for d in settings.OUTPUTS_DIR.iterdir() if d.is_dir() and (d / "match_decisions.jsonl").exists()],
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    if not runs:
        pytest.skip("No completed run found in outputs directory")
    return runs[0]


def test_generate_report_creates_html(latest_run_dir):
    """After a run, generate_report() writes report.html larger than 2 KB."""
    res = generate_report(latest_run_dir)
    html_path = Path(res["html"])
    assert html_path.exists(), "report.html was not written to run_dir"
    assert html_path.stat().st_size > 2048, f"report.html is too small: {html_path.stat().st_size} bytes"
    assert res["pdf"] is None
    assert "PDF generation deferred" in res["reason"]
    assert res["ms"] > 0


def test_report_contains_required_sections(latest_run_dir):
    """The HTML contains all 9 section headers."""
    res = generate_report(latest_run_dir)
    html = Path(res["html"]).read_text(encoding="utf-8")

    expected_sections = [
        "1. Header",
        "2. Coordinate Summary",
        "3. Geometry Summary",
        "4. Radiometric Summary",
        "5. Feature Extraction Summary",
        "6. Match Summary",
        "7. Quality Assessment",
        "8. Stage Timeline",
        "9. References"
    ]
    for sec in expected_sections:
        assert sec in html, f"Missing section in report HTML: '{sec}'"


def test_report_has_no_banned_strings(latest_run_dir):
    """_check_no_banned_strings does not raise on generated HTML (R11 compliance)."""
    res = generate_report(latest_run_dir)
    html = Path(res["html"]).read_text(encoding="utf-8")
    _check_no_banned_strings(html)


def test_report_stage_timeline(latest_run_dir):
    """The HTML contains every stage name from match_decisions.jsonl in the timeline section."""
    res = generate_report(latest_run_dir)
    html = Path(res["html"]).read_text(encoding="utf-8")

    decisions = []
    with open(latest_run_dir / "match_decisions.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    decisions.append(json.loads(line))
                except Exception:
                    pass

    stage_names = {d["stage"] for d in decisions if "stage" in d}
    timeline_sub = html[html.find("8. Stage Timeline"):html.find("9. References")]
    for stg in stage_names:
        assert f"<code>{stg}</code>" in timeline_sub, f"Stage '{stg}' missing from timeline section"


def test_report_references_papers(latest_run_dir):
    """The HTML contains at least 5 paper citations."""
    res = generate_report(latest_run_dir)
    html = Path(res["html"]).read_text(encoding="utf-8")

    refs_sub = html[html.find("9. References"):]
    papers = [
        "RIFT2",
        "Thin-plate splines",
        "Self-Calibrating Dispersion Filtering",
        "MAGSAC++",
        "Distinctive image features",
        "phase congruency"
    ]
    matched = [p for p in papers if p.lower() in refs_sub.lower()]
    assert len(matched) >= 5, f"Expected at least 5 paper citations, matched {len(matched)}: {matched}"
