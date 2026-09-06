import os
import tempfile

import cv2
import numpy as np
import pytest

from src.io import load_image, validate_image, load_pair


@pytest.fixture
def sample_image_path():
    img = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        cv2.imwrite(f.name, img)
        yield f.name
    os.unlink(f.name)


def test_load_image(sample_image_path):
    img = load_image(sample_image_path)
    assert img is not None
    assert img.shape == (100, 100)


def test_load_image_invalid():
    with pytest.raises(FileNotFoundError):
        load_image("/nonexistent/path.png")


def test_validate_image_valid():
    img = np.zeros((50, 50), dtype=np.uint8)
    assert validate_image(img) is True


def test_validate_image_none():
    assert validate_image(None) is False


def test_validate_image_empty():
    img = np.array([], dtype=np.uint8)
    assert validate_image(img) is False


def test_load_pair(sample_image_path):
    ref, mov = load_pair(sample_image_path, sample_image_path)
    assert ref.shape == (100, 100)
    assert mov.shape == (100, 100)
