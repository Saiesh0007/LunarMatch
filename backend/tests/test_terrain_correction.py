import pytest
import numpy as np
from app.services.terrain_correction import apply_cosine_correction


def test_flat_dem_identity_correction():
    """Correction all 1.0 -> mean_before and mean_after are equal."""
    img = np.full((100, 100), 120, dtype=np.uint8)
    corr = np.ones((100, 100), dtype=np.float32)

    res = apply_cosine_correction(img, corr)
    assert np.isclose(res["mean_before"], 120.0)
    assert np.isclose(res["mean_after"], 120.0)
    assert np.array_equal(res["image"], img)


def test_brightness_normalized():
    """Two halves with different brightness converge toward each other when differential correction is applied."""
    img = np.zeros((100, 100), dtype=np.uint8)
    img[:, :50] = 80   # darker half
    img[:, 50:] = 160  # brighter half

    # Correction compensates: boost dark side (1.5), attenuate bright side (0.75)
    corr = np.ones((100, 100), dtype=np.float32)
    corr[:, :50] = 1.5   # 80 * 1.5 = 120
    corr[:, 50:] = 0.75  # 160 * 0.75 = 120

    res = apply_cosine_correction(img, corr)
    corr_img = res["image"]
    mean_left = corr_img[:, :50].mean()
    mean_right = corr_img[:, 50:].mean()

    # The means should converge
    assert abs(mean_left - mean_right) < abs(80.0 - 160.0)
    assert np.isclose(mean_left, mean_right, atol=2.0)


def test_masked_region_excluded():
    """Mean and std are computed over the masked region only."""
    img = np.zeros((100, 100), dtype=np.uint8)
    img[:50, :] = 200  # unmasked
    img[50:, :] = 50   # masked out

    mask = np.zeros((100, 100), dtype=bool)
    mask[:50, :] = True  # only top half is lit

    corr = np.ones((100, 100), dtype=np.float32)
    res = apply_cosine_correction(img, corr, mask=mask)

    assert np.isclose(res["mean_before"], 200.0)
    assert np.isclose(res["mean_after"], 200.0)
    # Masked region in returned image is 0
    assert np.all(res["image"][~mask] == 0)


def test_clip_hits_counted():
    """Correction 2.0 on bright image -> hits > 0."""
    img = np.full((100, 100), 200, dtype=np.uint8)
    corr = np.full((100, 100), 2.0, dtype=np.float32)  # 200 * 2.0 = 400 > 255

    res = apply_cosine_correction(img, corr)
    assert res["clip_hits"] == 100 * 100
    assert np.all(res["image"] == 255)


def test_dtype_preserved():
    """uint8 -> uint8, float32 -> float32."""
    img_u8 = np.full((50, 50), 100, dtype=np.uint8)
    corr = np.ones((50, 50), dtype=np.float32)
    res_u8 = apply_cosine_correction(img_u8, corr)
    assert res_u8["image"].dtype == np.uint8

    img_f32 = np.full((50, 50), 0.5, dtype=np.float32)
    res_f32 = apply_cosine_correction(img_f32, corr)
    assert res_f32["image"].dtype == np.float32
