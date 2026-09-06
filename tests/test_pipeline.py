import os
import tempfile

import cv2
import numpy as np

from src.pipeline import run_pipeline


def _create_synthetic_pair():
    rng = np.random.RandomState(42)
    ref = rng.randint(0, 255, (300, 300), dtype=np.uint8)
    # Apply a small known translation to create the moving image
    transform = np.float32([[1, 0, 10], [0, 1, 5]])
    mov = cv2.warpAffine(ref, transform, (300, 300))
    return ref, mov


def test_pipeline_success():
    ref, mov = _create_synthetic_pair()
    with tempfile.TemporaryDirectory() as tmpdir:
        ref_path = os.path.join(tmpdir, "ref.png")
        mov_path = os.path.join(tmpdir, "mov.png")
        cv2.imwrite(ref_path, ref)
        cv2.imwrite(mov_path, mov)

        result = run_pipeline(ref_path, mov_path)
        assert result["status"] == "success"
        assert result["metrics"] is not None
        assert result["metrics"]["inlier_count"] > 0
        assert result["metrics"]["rmse"] is not None
        assert result["registered_image"] is not None
        assert result["registered_image"].shape[:2] == ref.shape[:2]


def test_pipeline_invalid_path():
    result = run_pipeline("/nonexistent/ref.png", "/nonexistent/mov.png")
    assert result["status"] == "failed"
    assert result["reason"] is not None


def test_pipeline_blank_images():
    with tempfile.TemporaryDirectory() as tmpdir:
        ref_path = os.path.join(tmpdir, "ref.png")
        mov_path = os.path.join(tmpdir, "mov.png")
        cv2.imwrite(ref_path, np.zeros((100, 100), dtype=np.uint8))
        cv2.imwrite(mov_path, np.zeros((100, 100), dtype=np.uint8))

        result = run_pipeline(ref_path, mov_path)
        assert result["status"] == "failed"
        assert "keypoints" in result["reason"].lower() or "matches" in result["reason"].lower()
