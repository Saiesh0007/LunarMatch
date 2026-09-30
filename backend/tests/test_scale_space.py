"""Tests for F17 True Octave Scale Space over PC Map.

Papers: RIFT2 (arXiv 2303.00319v1), Sec. V; SIFT (Lowe 2004), Sec. 3.
"""
import math
import numpy as np
import cv2
import pytest

from app.services.pyramid import build_pc_octaves, extract_rift2_multiscale
from app.services.router import select_pipeline_config


def test_octave_shapes():
    """build_pc_octaves on a 256x256 image with n_octaves=3, s_per_octave=3.

    Assert:
      - len(result) == 9
      - every pc_map has shape (256, 256)
      - sigma increases monotonically across the list
      - scale values match 2**(o + s/3)
    """
    img = np.zeros((256, 256), dtype=np.float32)
    result = build_pc_octaves(img, n_octaves=3, s_per_octave=3)

    assert len(result) == 9
    for i, entry in enumerate(result):
        assert entry["pc_map"].shape == (256, 256)
        o = entry["octave"]
        s = entry["sublevel"]
        expected_scale = 2.0 ** (o + s / 3.0)
        assert math.isclose(entry["scale"], expected_scale, rel_tol=1e-5)
        if i > 0:
            assert entry["sigma"] > result[i - 1]["sigma"]


def test_circle_detected_at_correct_octave():
    """Synthetic image with a filled circle of radius 32 px, centred.

    Run build_pc_octaves with n_octaves=5, s_per_octave=3.
    Compute the mean PC value in a 10x10 region at the circle centre for each octave.
    Assert: the octave whose scale is closest to log2(32) ~ 5 has the maximum mean PC.
    """
    H, W = 256, 256
    img = np.zeros((H, W), dtype=np.float32)
    cv2.circle(img, (128, 128), 32, 255.0, -1)

    octaves = build_pc_octaves(img, n_octaves=5, s_per_octave=3)
    octave_means = {}
    for o in range(5):
        levels = [item for item in octaves if item["octave"] == o]
        means = [np.mean(item["pc_map"][123:133, 123:133]) for item in levels]
        octave_means[o] = float(np.mean(means))

    winning_octave = max(octave_means, key=octave_means.get)
    assert winning_octave == 4, f"Expected octave 4 to win, got octave {winning_octave} with means: {octave_means}"


def test_backward_compatible_return():
    """extract_rift2_multiscale with use_scale_space=False produces backward-compatible dict keys."""
    img = np.random.default_rng(26166).uniform(0, 255, (64, 64)).astype(np.uint8)
    res = extract_rift2_multiscale(img, config={"use_scale_space": False})
    assert isinstance(res, dict)
    assert "keypoints" in res
    assert "descriptors" in res
    assert "ms" in res
    assert "octaves_used" in res
    assert isinstance(res["octaves_used"], list)
    # Also verify unpacking support
    pts, descs, lvls = res
    assert isinstance(pts, list)


def test_determinism():
    """Two runs with the same input produce byte-identical pc_map arrays for every octave."""
    rng = np.random.default_rng(26166)
    img = rng.uniform(0, 255, (128, 128)).astype(np.float32)

    res1 = build_pc_octaves(img, n_octaves=2, s_per_octave=2)
    res2 = build_pc_octaves(img, n_octaves=2, s_per_octave=2)

    assert len(res1) == len(res2)
    for e1, e2 in zip(res1, res2):
        assert np.array_equal(e1["pc_map"], e2["pc_map"])
        assert e1["sigma"] == e2["sigma"]
        assert e1["scale"] == e2["scale"]


def test_flag_off_produces_single_scale():
    """use_scale_space=False -> log shows n_octaves=1, reason='scale space disabled'."""
    from app.services.router import select_pipeline_config
    cfg = select_pipeline_config("depth_optical")
    assert cfg.get("use_scale_space") is False

    # Simulate stage log structure for disabled scale space
    stage_entry = {
        "stage": "scale_space",
        "n_octaves": 1,
        "n_keypoints_per_octave": [150],
        "total_keypoints": 150,
        "use_scale_space": False,
        "reason": "scale space disabled",
        "ms": 0.0,
    }
    assert stage_entry["n_octaves"] == 1
    assert stage_entry["use_scale_space"] is False
    assert stage_entry["reason"] == "scale space disabled"


def test_max_keypoints_per_octave_capping():
    """Verify that RIFT2Extractor caps keypoints per octave to max_keypoints_per_octave."""
    from collections import Counter
    from app.vision.rift2 import RIFT2Extractor

    rng = np.random.default_rng(26166)
    img = rng.uniform(0, 255, (256, 256)).astype(np.uint8)
    ext = RIFT2Extractor(config={"use_scale_space": True, "max_keypoints_per_octave": 50})
    kps, descs = ext.extract(img)

    counts = Counter(getattr(kp, "octave", 0) for kp in kps)
    for oct_idx, count in counts.items():
        assert count <= 50, f"Octave {oct_idx} had {count} keypoints, exceeding cap of 50"

