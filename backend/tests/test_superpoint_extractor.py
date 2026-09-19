import time
from pathlib import Path
import numpy as np
import pytest

from app.vision.superpoint_extractor import SuperPointExtractor

_WEIGHTS_PATH = Path(__file__).resolve().parent.parent / "weights" / "superpoint_v1.pth"


@pytest.mark.skipif(not _WEIGHTS_PATH.exists(), reason="SuperPoint weights not found")
def test_superpoint_extractor_execution():
    assert _WEIGHTS_PATH.exists(), "SuperPoint weights file must exist"
    extractor = SuperPointExtractor(str(_WEIGHTS_PATH), max_features=500)

    # Generate test image (640x640) with synthetic features / textured gradient
    np.random.seed(26166)
    img = (np.random.rand(640, 640) * 255).astype(np.uint8)

    t0 = time.perf_counter()
    out1 = extractor.extract(img)
    duration = time.perf_counter() - t0

    assert duration < 8.0, f"Extraction exceeded 8s limit: {duration:.2f}s"
    assert "keypoints" in out1
    assert "descriptors" in out1
    assert "scores" in out1

    kpts1 = out1["keypoints"]
    desc1 = out1["descriptors"]

    assert isinstance(kpts1, np.ndarray)
    assert isinstance(desc1, np.ndarray)
    assert kpts1.ndim == 2 and kpts1.shape[1] == 2
    assert desc1.ndim == 2 and desc1.shape[1] == 256
    assert len(kpts1) == len(desc1)
    assert len(kpts1) > 0

    # Deterministic test
    out2 = extractor.extract(img)
    kpts2 = out2["keypoints"]
    desc2 = out2["descriptors"]

    np.testing.assert_allclose(kpts1, kpts2, rtol=1e-5, atol=1e-5)
    np.testing.assert_allclose(desc1, desc2, rtol=1e-5, atol=1e-5)
