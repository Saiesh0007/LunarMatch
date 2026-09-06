import numpy as np

from src.registration import register, create_overlay, create_difference


def test_register_affine_identity():
    ref = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
    mov = ref.copy()
    identity = np.float32([[1, 0, 0], [0, 1, 0]])
    result = register(ref, mov, identity, model="affine")
    assert result.shape == ref.shape
    np.testing.assert_array_equal(result, mov)


def test_register_homography_identity():
    ref = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
    mov = ref.copy()
    identity = np.float64([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    result = register(ref, mov, identity, model="homography")
    assert result.shape == ref.shape


def test_create_overlay():
    ref = np.random.randint(0, 255, (50, 50), dtype=np.uint8)
    reg = np.random.randint(0, 255, (50, 50), dtype=np.uint8)
    overlay = create_overlay(ref, reg)
    assert overlay.shape[:2] == (50, 50)
    assert overlay.ndim == 3


def test_create_difference():
    ref = np.full((50, 50), 100, dtype=np.uint8)
    reg = np.full((50, 50), 120, dtype=np.uint8)
    diff = create_difference(ref, reg)
    assert diff.shape == (50, 50)
    assert np.all(diff == 20)
