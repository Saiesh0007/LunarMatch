import numpy as np
from scipy.ndimage import rotate

from app.vision.hopc import compute_hopc, hopc_similarity


def make_patch(seed: int = 1, size: int = 128) -> np.ndarray:
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    patch = np.zeros((size, size), dtype=np.float32)
    for _ in range(8):
        cx, cy = rng.uniform(0.1, 0.9, 2) * size
        radius = rng.uniform(6.0, 20.0)
        distance = np.hypot(xx - cx, yy - cy)
        patch += np.exp(-((distance - radius) ** 2) / (2.0 * 3.0 ** 2))
    patch = (patch - patch.min()) / (patch.max() - patch.min() + 1e-6)
    return patch.astype(np.float32)


def test_hopc_output_shape():
    hopc_map = compute_hopc(make_patch())
    assert hopc_map.shape == (128, 128, 288)
    assert hopc_map.dtype == np.float32


def test_hopc_rotation_invariance():
    patch = make_patch(seed=4)
    rotated = rotate(patch, 30.0, reshape=False, order=1, mode="reflect")
    assert hopc_similarity(patch, rotated) >= 0.7


def test_hopc_illumination_invariance():
    patch = make_patch(seed=5)
    shifted = np.clip(1.6 * patch + 0.14, 0.0, 1.0).astype(np.float32)
    assert hopc_similarity(patch, shifted) >= 0.7


def test_hopc_discriminates_different_patches():
    assert hopc_similarity(make_patch(seed=6), make_patch(seed=99)) < 0.5