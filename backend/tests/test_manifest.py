import hashlib
import json

from app.evaluation.manifest import build_run_manifest


def files(tmp_path):
    ref = tmp_path / "reference.bin"
    moving = tmp_path / "moving.bin"
    ref.write_bytes(b"reference")
    moving.write_bytes(b"moving")
    return ref, moving


def test_manifest_contains_required_fields(tmp_path):
    ref, moving = files(tmp_path)
    manifest = build_run_manifest("run-1", str(ref), str(moving), {"alpha": 1})
    assert {"mode", "git_commit", "input_sha256", "config_hash", "python_version", "opencv_version", "numpy_version", "seed"}.issubset(manifest)


def test_manifest_measured_mode(tmp_path):
    ref, moving = files(tmp_path)
    assert build_run_manifest("run-1", str(ref), str(moving), {})["mode"] == "measured"


def test_manifest_synthetic_mode(tmp_path):
    ref, moving = files(tmp_path)
    manifest = build_run_manifest("run-1", str(ref), str(moving), {}, synthetic_validation=True, seed=26166)
    assert manifest["mode"] == "synthetic_validation"
    assert manifest["seed"] == 26166


def test_manifest_input_hash(tmp_path):
    ref, moving = files(tmp_path)
    manifest = build_run_manifest("run-1", str(ref), str(moving), {})
    expected = hashlib.sha256(ref.read_bytes()).hexdigest()
    assert manifest["input_sha256"]["reference"] == expected
