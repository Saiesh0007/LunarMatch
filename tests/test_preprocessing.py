import numpy as np

from src.preprocessing import (
    to_grayscale,
    normalize_intensity,
    enhance_contrast,
    denoise,
    preprocess,
)


def test_to_grayscale_color():
    img = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
    gray = to_grayscale(img)
    assert gray.ndim == 2
    assert gray.shape == (50, 50)


def test_to_grayscale_already_gray():
    img = np.random.randint(0, 255, (50, 50), dtype=np.uint8)
    gray = to_grayscale(img)
    assert gray.ndim == 2
    assert np.array_equal(gray, img)


def test_normalize_intensity():
    img = np.array([[10, 50], [100, 200]], dtype=np.uint8)
    norm = normalize_intensity(img)
    assert norm.min() == 0
    assert norm.max() == 255


def test_normalize_constant():
    img = np.full((10, 10), 128, dtype=np.uint8)
    norm = normalize_intensity(img)
    assert norm.max() == 0


def test_enhance_contrast():
    img = np.random.randint(0, 255, (50, 50), dtype=np.uint8)
    enhanced = enhance_contrast(img)
    assert enhanced.shape == img.shape
    assert enhanced.dtype == np.uint8


def test_denoise():
    img = np.random.randint(0, 255, (50, 50), dtype=np.uint8)
    denoised = denoise(img)
    assert denoised.shape == img.shape


def test_preprocess_chain():
    img = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
    result, steps = preprocess(img)
    assert result.ndim == 2
    assert "grayscale" in steps
    assert "normalize" in steps
    assert "clahe" in steps


def test_preprocess_no_denoise_by_default():
    img = np.random.randint(0, 255, (50, 50), dtype=np.uint8)
    _, steps = preprocess(img)
    assert "denoise" not in steps
