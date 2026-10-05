import cv2
import numpy as np

from app.vision.dense_structural import register_dense


def _terrain(seed, size=384):
    rng = np.random.default_rng(seed)
    img = cv2.GaussianBlur(rng.normal(0, 1, (size, size)).astype(np.float32), (0, 0), 3)
    for _ in range(40):  # crater-like rims give the structure a lunar scene has
        c = tuple(int(v) for v in rng.integers(20, size - 20, 2))
        cv2.circle(img, c, int(rng.integers(5, 25)), float(rng.uniform(1, 3)), 2)
    return cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)


def test_recovers_known_shift_and_rotation():
    ref = _terrain(1)
    A = cv2.getRotationMatrix2D((192, 192), 3.0, 1.0)
    A[:, 2] += (7.0, -5.0)
    mov = cv2.warpAffine(ref, A, (384, 384), borderMode=cv2.BORDER_REFLECT)
    res = register_dense(ref, mov, scale_prior=1.0, angle_prior=0.0)
    assert res.H is not None, res.diagnostics
    H_true = np.linalg.inv(np.vstack([A, [0, 0, 1]]))  # moving -> reference
    pts = np.float64([[100, 100], [280, 120], [200, 290]]).reshape(-1, 1, 2)
    err = cv2.perspectiveTransform(pts, res.H) - cv2.perspectiveTransform(pts, H_true)
    assert np.abs(err).max() < 1.0


def test_rejects_unrelated_texture():
    """Two independent noise fields must not produce a 'verified' pose (false-lock regression)."""
    res = register_dense(_terrain(2), _terrain(3), scale_prior=1.0, angle_prior=0.0)
    assert res.H is None
    assert res.diagnostics.get("failure_reason")
