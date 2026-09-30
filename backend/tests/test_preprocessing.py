import numpy as np
import pytest
from app.vision.preprocessing import normalize_intensity, apply_clahe, denoise_image, preprocess_lunar_image
from app.models.schemas import PreprocessingConfig

def test_normalize_intensity():
    arr = np.array([[10, 20], [30, 40]], dtype=np.uint8)
    norm = normalize_intensity(arr)
    assert norm.min() == 0
    assert norm.max() == 255
    assert norm.dtype == np.uint8

def test_clahe_enhancement():
    arr = np.full((64, 64), 128, dtype=np.uint8)
    # create center gradient
    arr[20:40, 20:40] = 60
    enhanced = apply_clahe(arr, clip_limit=2.0, tile_grid_size=8)
    assert enhanced.shape == (64, 64)
    assert enhanced.dtype == np.uint8

def test_preprocess_lunar_image_pipeline():
    arr = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
    cfg = PreprocessingConfig(normalize=True, clahe=True, denoise=True)
    out, meta = preprocess_lunar_image(arr, cfg)
    assert out.shape == (100, 100)
    assert meta["normalized"] is True
    assert meta["clahe_applied"] is True
    assert meta["denoised"] is True
