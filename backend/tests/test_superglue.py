"""Tests for the SuperGlue Sinkhorn optimal-transport matcher simulation."""

import cv2
import numpy as np
import pytest

from app.vision.superglue_matcher import (
    SuperGlueMatcher,
    _log_sinkhorn,
    _logsumexp,
    _sinusoidal_position_encoding,
)
from app.models.schemas import MatchPairModel


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def make_keypoints(n: int, seed: int = 0, w: int = 512, h: int = 512):
    rng = np.random.RandomState(seed)
    return [
        cv2.KeyPoint(
            x=float(rng.randint(10, w - 10)),
            y=float(rng.randint(10, h - 10)),
            size=float(rng.uniform(3.0, 20.0)),
            angle=float(rng.uniform(0.0, 360.0)),
            response=float(rng.uniform(0.01, 0.5)),
            octave=int(rng.randint(0, 4)),
        )
        for _ in range(n)
    ]


def make_descriptors(n: int, dim: int = 128, seed: int = 0, normalize: bool = True):
    rng = np.random.RandomState(seed)
    desc = rng.randn(n, dim).astype(np.float32)
    if normalize:
        norms = np.linalg.norm(desc, axis=1, keepdims=True)
        desc /= np.where(norms < 1e-8, 1.0, norms)
    return desc


# ─────────────────────────────────────────────────────────────────────────────
# _logsumexp
# ─────────────────────────────────────────────────────────────────────────────

def test_logsumexp_matches_scipy():
    """_logsumexp should agree with scipy.special.logsumexp to 1e-9."""
    from scipy.special import logsumexp as scipy_lse
    rng = np.random.RandomState(42)
    x = rng.randn(8, 12)
    np.testing.assert_allclose(_logsumexp(x, axis=0), scipy_lse(x, axis=0), atol=1e-9)
    np.testing.assert_allclose(_logsumexp(x, axis=1), scipy_lse(x, axis=1), atol=1e-9)


def test_logsumexp_numerically_stable():
    """Large values must not overflow."""
    x = np.array([[1e5, 1e5 + 1.0, 1e5 + 2.0]], dtype=np.float64)
    result = _logsumexp(x, axis=1)
    assert np.isfinite(result).all()


# ─────────────────────────────────────────────────────────────────────────────
# _sinusoidal_position_encoding
# ─────────────────────────────────────────────────────────────────────────────

def test_position_encoding_shape():
    kps = make_keypoints(20)
    enc = _sinusoidal_position_encoding(kps, img_width=512, img_height=512, dim=64)
    assert enc.shape == (20, 64)
    assert enc.dtype == np.float32


def test_position_encoding_empty():
    enc = _sinusoidal_position_encoding([], img_width=512, img_height=512, dim=64)
    assert enc.shape == (0, 64)


def test_position_encoding_deterministic():
    kps = make_keypoints(10, seed=7)
    enc1 = _sinusoidal_position_encoding(kps, 512, 512)
    enc2 = _sinusoidal_position_encoding(kps, 512, 512)
    np.testing.assert_array_equal(enc1, enc2)


def test_position_encoding_dim_error():
    with pytest.raises(ValueError, match="divisible by 4"):
        _sinusoidal_position_encoding(make_keypoints(3), 512, 512, dim=6)


# ─────────────────────────────────────────────────────────────────────────────
# _log_sinkhorn
# ─────────────────────────────────────────────────────────────────────────────

def test_sinkhorn_doubly_stochastic():
    """After convergence, row and column marginals should be ≈ 1.0 each."""
    rng = np.random.RandomState(0)
    log_alpha = rng.randn(6, 6)
    log_P = _log_sinkhorn(log_alpha, n_iters=200)
    P = np.exp(log_P)
    np.testing.assert_allclose(P.sum(axis=1), np.ones(6), atol=1e-4)
    np.testing.assert_allclose(P.sum(axis=0), np.ones(6), atol=1e-4)


def test_sinkhorn_output_shape():
    log_alpha = np.zeros((5, 7))
    log_P = _log_sinkhorn(log_alpha)
    assert log_P.shape == (5, 7)


def test_sinkhorn_finite():
    """No NaN / Inf in output even with near-zero entries."""
    log_alpha = np.full((4, 4), -1000.0)
    log_P = _log_sinkhorn(log_alpha, n_iters=50)
    assert np.isfinite(log_P).all()


# ─────────────────────────────────────────────────────────────────────────────
# SuperGlueMatcher.match — basic contract
# ─────────────────────────────────────────────────────────────────────────────

class TestSuperGlueMatcherBasic:
    def setup_method(self):
        self.matcher = SuperGlueMatcher(seed=26166)
        self.kps_ref = make_keypoints(30, seed=1)
        self.kps_mov = make_keypoints(30, seed=2)
        self.desc_ref = make_descriptors(30, seed=1)
        self.desc_mov = make_descriptors(30, seed=2)

    def test_returns_list_of_match_pair_models(self):
        matches, _ = self.matcher.match(
            self.kps_ref, self.desc_ref, self.kps_mov, self.desc_mov
        )
        assert isinstance(matches, list)
        for m in matches:
            assert isinstance(m, MatchPairModel)

    def test_candidate_count(self):
        _, candidate_count = self.matcher.match(
            self.kps_ref, self.desc_ref, self.kps_mov, self.desc_mov
        )
        assert candidate_count == 30 * 30

    def test_match_indices_in_range(self):
        matches, _ = self.matcher.match(
            self.kps_ref, self.desc_ref, self.kps_mov, self.desc_mov
        )
        for m in matches:
            assert 0 <= m.ref_idx < 30
            assert 0 <= m.mov_idx < 30

    def test_distances_in_zero_one(self):
        """Distance = 1 - P[i,j] must lie in [0, 1]."""
        matches, _ = self.matcher.match(
            self.kps_ref, self.desc_ref, self.kps_mov, self.desc_mov
        )
        for m in matches:
            assert 0.0 <= m.distance <= 1.0

    def test_no_duplicate_ref_indices(self):
        """MNN ensures each ref kp appears at most once."""
        matches, _ = self.matcher.match(
            self.kps_ref, self.desc_ref, self.kps_mov, self.desc_mov
        )
        ref_idxs = [m.ref_idx for m in matches]
        assert len(ref_idxs) == len(set(ref_idxs))

    def test_no_duplicate_mov_indices(self):
        matches, _ = self.matcher.match(
            self.kps_ref, self.desc_ref, self.kps_mov, self.desc_mov
        )
        mov_idxs = [m.mov_idx for m in matches]
        assert len(mov_idxs) == len(set(mov_idxs))


# ─────────────────────────────────────────────────────────────────────────────
# Determinism — seed 26166
# ─────────────────────────────────────────────────────────────────────────────

def test_superglue_deterministic_seed_26166():
    """Two runs with seed=26166 must produce identical matches."""
    kps_r = make_keypoints(25, seed=10)
    kps_m = make_keypoints(25, seed=11)
    desc_r = make_descriptors(25, seed=10)
    desc_m = make_descriptors(25, seed=11)

    m1, c1 = SuperGlueMatcher(seed=26166).match(kps_r, desc_r, kps_m, desc_m)
    m2, c2 = SuperGlueMatcher(seed=26166).match(kps_r, desc_r, kps_m, desc_m)

    assert c1 == c2
    assert len(m1) == len(m2)
    for a, b in zip(m1, m2):
        assert a.ref_idx == b.ref_idx
        assert a.mov_idx == b.mov_idx
        assert a.distance == pytest.approx(b.distance, abs=1e-9)


def test_different_seeds_may_differ():
    """Different seeds should generally produce different results."""
    kps_r = make_keypoints(20, seed=5)
    kps_m = make_keypoints(20, seed=6)
    desc_r = make_descriptors(20, seed=5)
    desc_m = make_descriptors(20, seed=6)

    m1, _ = SuperGlueMatcher(seed=26166).match(kps_r, desc_r, kps_m, desc_m)
    m2, _ = SuperGlueMatcher(seed=99999).match(kps_r, desc_r, kps_m, desc_m)
    # Seeds differ → projections differ → augmented descriptors differ
    # At least one attribute must differ (distances if nothing else)
    distances1 = [m.distance for m in m1]
    distances2 = [m.distance for m in m2]
    assert distances1 != distances2 or len(m1) != len(m2)


# ─────────────────────────────────────────────────────────────────────────────
# Edge cases
# ─────────────────────────────────────────────────────────────────────────────

def test_empty_ref_keypoints():
    matcher = SuperGlueMatcher()
    kps_m = make_keypoints(10)
    desc_m = make_descriptors(10)
    matches, count = matcher.match([], np.empty((0, 128), np.float32), kps_m, desc_m)
    assert matches == []
    assert count == 0


def test_empty_mov_keypoints():
    matcher = SuperGlueMatcher()
    kps_r = make_keypoints(10)
    desc_r = make_descriptors(10)
    matches, count = matcher.match(kps_r, desc_r, [], np.empty((0, 128), np.float32))
    assert matches == []
    assert count == 0


def test_single_keypoint_each_side():
    """1×1 score matrix must not crash and should yield 0 or 1 matches."""
    kps_r = make_keypoints(1, seed=0)
    kps_m = make_keypoints(1, seed=1)
    desc_r = make_descriptors(1, seed=0)
    desc_m = make_descriptors(1, seed=1)
    matcher = SuperGlueMatcher(match_threshold=0.0)  # accept any match
    matches, count = matcher.match(kps_r, desc_r, kps_m, desc_m)
    assert count == 1
    assert len(matches) in (0, 1)


def test_identical_descriptors_high_confidence():
    """Identical descriptor on both sides at same position → high confidence match."""
    kp = cv2.KeyPoint(x=256.0, y=256.0, size=8.0, angle=0.0)
    desc = make_descriptors(1, seed=42)
    matcher = SuperGlueMatcher(match_threshold=0.0)
    matches, _ = matcher.match([kp], desc, [kp], desc)
    # Should get exactly 1 match with very low distance (high confidence)
    assert len(matches) == 1
    assert matches[0].distance <= 0.5  # P close to 1 → distance close to 0


def test_low_overlap_graceful():
    """Very different descriptors (low overlap) should still return without error."""
    rng = np.random.RandomState(0)
    kps_r = make_keypoints(15, seed=0)
    kps_m = make_keypoints(15, seed=1)
    desc_r = np.eye(15, 128, dtype=np.float32)  # orthogonal rows
    desc_m = -np.eye(15, 128, dtype=np.float32)  # anti-parallel
    matcher = SuperGlueMatcher(match_threshold=0.5)  # strict
    matches, _ = matcher.match(kps_r, desc_r, kps_m, desc_m)
    # Anti-parallel descriptors → low P → few or no matches above threshold
    assert isinstance(matches, list)


# ─────────────────────────────────────────────────────────────────────────────
# Dustbin rejection
# ─────────────────────────────────────────────────────────────────────────────

def test_dustbin_rejects_bad_matches():
    """Raise the threshold: fewer matches than with threshold=0."""
    kps_r = make_keypoints(20, seed=33)
    kps_m = make_keypoints(20, seed=44)
    desc_r = make_descriptors(20, seed=33)
    desc_m = make_descriptors(20, seed=44)

    strict = SuperGlueMatcher(match_threshold=0.9, seed=26166)
    lenient = SuperGlueMatcher(match_threshold=0.0, seed=26166)

    m_strict, _ = strict.match(kps_r, desc_r, kps_m, desc_m)
    m_lenient, _ = lenient.match(kps_r, desc_r, kps_m, desc_m)

    assert len(m_strict) <= len(m_lenient)


# ─────────────────────────────────────────────────────────────────────────────
# Sinkhorn convergence quality
# ─────────────────────────────────────────────────────────────────────────────

def test_more_sinkhorn_iters_tighter_marginals():
    """More iterations → row/col marginals closer to uniform."""
    rng = np.random.RandomState(0)
    log_alpha = rng.randn(10, 10)

    few_iters = np.exp(_log_sinkhorn(log_alpha, n_iters=5))
    many_iters = np.exp(_log_sinkhorn(log_alpha, n_iters=500))

    err_few = np.abs(few_iters.sum(axis=1) - 1.0).max()
    err_many = np.abs(many_iters.sum(axis=1) - 1.0).max()

    assert err_many < err_few
