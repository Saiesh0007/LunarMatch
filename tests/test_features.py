import numpy as np
import pytest

from src.features import extract


def _make_textured_image():
    rng = np.random.RandomState(42)
    img = rng.randint(0, 255, (200, 200), dtype=np.uint8)
    return img


def test_extract_sift():
    img = _make_textured_image()
    kp, desc = extract(img, method="sift")
    assert len(kp) > 0
    assert desc is not None
    assert desc.shape[1] == 128


def test_extract_unknown_method():
    img = _make_textured_image()
    with pytest.raises(ValueError, match="Unknown feature method"):
        extract(img, method="nonexistent")


def test_extract_blank_image():
    img = np.zeros((100, 100), dtype=np.uint8)
    kp, desc = extract(img, method="sift")
    assert len(kp) == 0
