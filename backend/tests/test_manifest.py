import hashlib
import json
import subprocess

from app.evaluation import manifest as manifest_module
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
    manifest = build_run_manifest("run-1", str(ref), str(moving), {}, offline_validation=True, seed=26166)
    assert manifest["mode"] == "deterministic_validation"
    assert manifest["seed"] == 26166


def test_manifest_input_hash(tmp_path):
    ref, moving = files(tmp_path)
    manifest = build_run_manifest("run-1", str(ref), str(moving), {})
    expected = hashlib.sha256(ref.read_bytes()).hexdigest()
    assert manifest["input_sha256"]["reference"] == expected


def test_missing_git_repository_does_not_emit_stderr(tmp_path, monkeypatch, capsys):
    ref, moving = files(tmp_path)

    def missing_git_repository(command, **kwargs):
        assert kwargs["stderr"] == subprocess.DEVNULL
        raise subprocess.CalledProcessError(128, command)

    monkeypatch.setattr(manifest_module.subprocess, "check_output", missing_git_repository)

    manifest = build_run_manifest("run-1", str(ref), str(moving), {})

    assert manifest["git_commit"] == "unknown"
    assert capsys.readouterr().err == ""
