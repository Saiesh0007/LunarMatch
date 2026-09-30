"""Unit tests for LightGlueMatcher wrapper."""

from pathlib import Path
import numpy as np
import pytest
import torch

from app.vision.lightglue_matcher import LightGlueMatcher

WEIGHTS_PATH = Path(__file__).resolve().parent.parent / "weights" / "superpoint_lightglue.pth"


def test_lightglue_matcher_loads_and_matches():
    """Verify LightGlueMatcher loads weights and matches a synthetic keypoint pair."""
    assert WEIGHTS_PATH.exists(), f"Weights missing at {WEIGHTS_PATH}"

    matcher = LightGlueMatcher(str(WEIGHTS_PATH))

    # Create synthetic keypoints and descriptors
    torch.manual_seed(26166)
    np.random.seed(26166)

    n_pts = 60
    kp_a = np.random.uniform(50, 550, size=(n_pts, 2)).astype(np.float32)
    # Small shift for image B
    kp_b = (kp_a + np.random.normal(0, 1.0, size=(n_pts, 2))).astype(np.float32)

    # Identical or near-identical descriptors
    desc_a = np.random.randn(n_pts, 256).astype(np.float32)
    desc_a /= np.linalg.norm(desc_a, axis=1, keepdims=True) + 1e-7

    desc_b = desc_a + np.random.normal(0, 0.05, size=(n_pts, 256)).astype(np.float32)
    desc_b /= np.linalg.norm(desc_b, axis=1, keepdims=True) + 1e-7

    img_shape = (640, 640)

    res = matcher.match(kp_a, desc_a, kp_b, desc_b, img_shape, img_shape)

    assert "matches" in res
    assert "scores" in res
    assert "ms" in res

    matches = res["matches"]
    scores = res["scores"]

    assert isinstance(matches, np.ndarray)
    assert matches.ndim == 2
    assert matches.shape[1] == 2
    assert len(matches) > 0, "Expected matches on near-identical synthetic pair"

    assert isinstance(scores, np.ndarray)
    assert len(scores) == len(matches)
    assert np.all(scores >= 0.0)
    assert np.all(scores <= 1.0)


def test_lightglue_matcher_empty_keypoints():
    """Verify LightGlueMatcher handles empty keypoint arrays gracefully."""
    matcher = LightGlueMatcher(str(WEIGHTS_PATH))
    kp_empty = np.empty((0, 2), dtype=np.float32)
    desc_empty = np.empty((0, 256), dtype=np.float32)

    res = matcher.match(kp_empty, desc_empty, kp_empty, desc_empty, (640, 640), (640, 640))
    assert len(res["matches"]) == 0
    assert len(res["scores"]) == 0
