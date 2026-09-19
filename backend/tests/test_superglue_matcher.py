from pathlib import Path
import numpy as np
import pytest

from app.vision.superglue_matcher import SuperGlueMatcher

_SP_WEIGHTS = Path(__file__).resolve().parent.parent / "weights" / "superpoint_v1.pth"
_SG_WEIGHTS = Path(__file__).resolve().parent.parent / "weights" / "superglue_outdoor.pth"


@pytest.mark.skipif(not _SG_WEIGHTS.exists(), reason="SuperGlue weights not found")
def test_superglue_matcher():
    matcher = SuperGlueMatcher(sp_weights=str(_SP_WEIGHTS), sg_weights=str(_SG_WEIGHTS))

    np.random.seed(26166)
    # Generate 50 keypoints and 256-D descriptors for both images
    kp_a = np.random.uniform(50, 550, size=(50, 2)).astype(np.float32)
    kp_b = kp_a + np.random.normal(0, 1.0, size=(50, 2)).astype(np.float32)

    desc_a = np.random.randn(50, 256).astype(np.float32)
    desc_a /= np.linalg.norm(desc_a, axis=1, keepdims=True)

    desc_b = desc_a + np.random.normal(0, 0.05, size=(50, 256)).astype(np.float32)
    desc_b /= np.linalg.norm(desc_b, axis=1, keepdims=True)

    res1 = matcher.match(kp_a, desc_a, kp_b, desc_b, (640, 640), (640, 640))

    assert "matches" in res1
    assert "scores" in res1
    assert "ms" in res1
    assert isinstance(res1["matches"], np.ndarray)
    assert res1["matches"].ndim == 2
    assert res1["matches"].shape[1] == 2

    # Determinism
    res2 = matcher.match(kp_a, desc_a, kp_b, desc_b, (640, 640), (640, 640))
    np.testing.assert_array_equal(res1["matches"], res2["matches"])
    np.testing.assert_allclose(res1["scores"], res2["scores"], rtol=1e-5, atol=1e-5)
