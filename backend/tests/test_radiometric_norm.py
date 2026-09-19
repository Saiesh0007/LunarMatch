import pytest
import numpy as np
from app.services.radiometric_norm import match_histograms_to


def test_identical_images_unchanged():
    """src == ref, method 'hist' produces output approximately equal to input."""
    rng = np.random.default_rng(26166)
    img = rng.integers(30, 220, size=(128, 128), dtype=np.uint8)

    out = match_histograms_to(img, img, method="hist")
    assert np.allclose(out, img, atol=2)


def test_darkened_src_matches():
    """src darkened by factor 0.5 -> after hist matching, mean(output) converges to mean(ref) within 5%."""
    rng = np.random.default_rng(26166)
    ref = rng.integers(60, 200, size=(128, 128), dtype=np.uint8)
    src = (ref * 0.5).astype(np.uint8)

    out = match_histograms_to(src, ref, method="hist")

    mean_ref = float(ref.mean())
    mean_out = float(out.mean())
    diff_pct = abs(mean_out - mean_ref) / mean_ref
    assert diff_pct < 0.05, f"Mean did not converge within 5%: ref={mean_ref}, out={mean_out}, diff={diff_pct:.4f}"


def test_method_none():
    """method 'none' returns src unchanged."""
    img = np.array([[10, 20], [30, 40]], dtype=np.uint8)
    ref = np.array([[100, 150], [200, 250]], dtype=np.uint8)

    out = match_histograms_to(img, ref, method="none")
    assert out is img


def test_clahe_only():
    """method 'clahe' preserves shape and increases contrast/std on low-contrast image."""
    # Low contrast image centered at 128
    img = np.full((128, 128), 128, dtype=np.uint8)
    img[32:96, 32:96] = 135
    ref = img.copy()

    std_before = float(img.std())
    out = match_histograms_to(img, ref, method="clahe")
    std_after = float(out.std())

    assert out.shape == img.shape
    assert std_after > std_before


def test_dtype_preserved():
    """uint8 in -> uint8 out; float32 in -> float32 out; uint16 in -> uint16 out."""
    rng = np.random.default_rng(26166)
    src_u8 = rng.integers(0, 255, (64, 64), dtype=np.uint8)
    ref_u8 = rng.integers(0, 255, (64, 64), dtype=np.uint8)
    assert match_histograms_to(src_u8, ref_u8).dtype == np.uint8

    src_f32 = rng.uniform(0.0, 1.0, (64, 64)).astype(np.float32)
    ref_f32 = rng.uniform(0.0, 1.0, (64, 64)).astype(np.float32)
    assert match_histograms_to(src_f32, ref_f32).dtype == np.float32

    src_u16 = rng.integers(0, 5000, (64, 64), dtype=np.uint16)
    ref_u16 = rng.integers(0, 5000, (64, 64), dtype=np.uint16)
    assert match_histograms_to(src_u16, ref_u16).dtype == np.uint16


def test_clahe_plus_hist_cross_modal():
    """Critical Note 2: Exercise clahe+hist path with synthetic cross-modal data."""
    rng = np.random.default_rng(26166)
    # Optical-like modality
    optical = rng.integers(40, 220, (128, 128), dtype=np.uint8)
    # SAR-like modality with speckle and high dynamic range
    sar = (rng.exponential(scale=30.0, size=(128, 128)) + 20.0).clip(0, 255).astype(np.uint8)

    out = match_histograms_to(sar, optical, method="clahe+hist")
    assert out.shape == sar.shape
    assert out.dtype == sar.dtype
    # Check that the mean of the transformed SAR converges toward the optical reference
    mean_sar_before = float(sar.mean())
    mean_opt = float(optical.mean())
    mean_out = float(out.mean())
    assert abs(mean_out - mean_opt) < abs(mean_sar_before - mean_opt)
