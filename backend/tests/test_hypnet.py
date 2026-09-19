"""Unit tests for Hyp-Net descriptor modulation service.

Paper: Hyp-Net (arXiv 2601.12325v1) — Multi-Sensor Matching with
       Hypernetworks.
"""

import numpy as np
import pytest
from app.services.hypnet import modulate, _compute_global_context


def test_shape_preserved():
    """descriptors (100, 216), global_context (216,) -> output shape (100, 216)."""
    rng = np.random.default_rng(42)
    descriptors = rng.standard_normal((100, 216)).astype(np.float32)
    global_context = _compute_global_context(descriptors)
    assert global_context.shape == (216,)

    output = modulate(descriptors, global_context)
    assert output.shape == (100, 216)


def test_zero_context_identity_form():
    """With global_context all zeros and b_s=b_t=0:
       scale = sigmoid(0) = 0.5
       shift = tanh(0) = 0
     so output = 0.5 * input. Assert this mathematically.
     Note: with W matrices nonzero, W @ 0 = 0 regardless, so the
     result is exactly 0.5 * input.
    """
    rng = np.random.default_rng(42)
    descriptors = rng.standard_normal((50, 216)).astype(np.float64)
    zero_context = np.zeros(216, dtype=np.float64)

    output = modulate(descriptors, zero_context)
    expected = 0.5 * descriptors
    np.testing.assert_allclose(output, expected, rtol=1e-7, atol=1e-9)


def test_determinism():
    """Same input twice -> byte-identical output."""
    rng = np.random.default_rng(123)
    descriptors = rng.standard_normal((80, 216)).astype(np.float32)
    ctx = _compute_global_context(descriptors)

    out1 = modulate(descriptors, ctx)
    out2 = modulate(descriptors, ctx)

    np.testing.assert_array_equal(out1, out2)
    assert out1.tobytes() == out2.tobytes()


def test_different_context_different_output():
    """Two different global_context vectors -> different modulations."""
    rng = np.random.default_rng(456)
    descriptors = rng.standard_normal((60, 216)).astype(np.float32)

    ctx1 = np.ones(216, dtype=np.float32) * 0.5
    ctx2 = -np.ones(216, dtype=np.float32) * 0.5

    out1 = modulate(descriptors, ctx1)
    out2 = modulate(descriptors, ctx2)

    assert not np.allclose(out1, out2)
    diff = np.abs(out1 - out2).max()
    assert diff > 1e-3


def test_dtype_preserved():
    """float32 in -> float32 out, float64 in -> float64 out."""
    rng = np.random.default_rng(789)
    desc_f32 = rng.standard_normal((40, 216)).astype(np.float32)
    ctx_f32 = desc_f32.mean(axis=0)
    out_f32 = modulate(desc_f32, ctx_f32)
    assert out_f32.dtype == np.float32

    desc_f64 = rng.standard_normal((40, 216)).astype(np.float64)
    ctx_f64 = desc_f64.mean(axis=0)
    out_f64 = modulate(desc_f64, ctx_f64)
    assert out_f64.dtype == np.float64
