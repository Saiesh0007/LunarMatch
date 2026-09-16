"""SuperGlue-style Sinkhorn optimal-transport matcher.

This is a **deterministic simulation** of the SuperGlue algorithm
(Sarlin et al., CVPR 2020).  It reproduces the *architecture* faithfully
without requiring PyTorch or pre-trained neural-network weights:

  1. Sinusoidal position encoding — encodes (x, y, scale, orientation) into a
     high-dimensional vector just as a GNN encoder would.
  2. Score matrix — cosine similarity between augmented descriptors, scaled by
     a learned temperature parameter (simulated as a fixed constant τ = 0.1).
  3. Dustbin augmentation — appends one "dustbin" row and column so unmatched
     keypoints can be routed to the dustbin rather than forced into a bad match.
  4. Sinkhorn iterations — iterative row- and column-normalisation on the
     log-domain score matrix to approximate the optimal transport assignment.
  5. Hard assignment — argmax over the converged soft-assignment matrix;
     mutual-nearest-neighbour filter removes asymmetric assignments.

Scientific honesty: every run tagged metric_mode=SIMULATED, seed=26166.
No neural weights are used.  Results are physically consistent but not
equivalent to actual SuperGlue inference.

Ref: "SuperGlue: Learning Feature Matching with Graph Neural Networks",
     Sarlin et al., CVPR 2020.  https://arxiv.org/abs/1911.11763
"""

from typing import List, Tuple, Optional
import numpy as np
import cv2

from ..models.schemas import MatchPairModel
from ..utils.logging import logger

# ─────────────────────────────────────────────────────────────────────────────
# Constants that mirror typical SuperGlue hyper-parameters
# ─────────────────────────────────────────────────────────────────────────────
_SINKHORN_ITERS: int = 100        # iterations until convergence (paper uses 100)
_TEMPERATURE: float = 0.1         # score-scaling temperature τ
_DUSTBIN_SCORE: float = 1.0       # initial dustbin logit (learned in real SG)
_POS_ENC_DIM: int = 64            # sinusoidal encoding dimension (must be even)
_SEED: int = 26166                 # SIH 2026 deterministic seed


# ─────────────────────────────────────────────────────────────────────────────
# Position encoding
# ─────────────────────────────────────────────────────────────────────────────

def _sinusoidal_position_encoding(
    keypoints: List[cv2.KeyPoint],
    img_width: int,
    img_height: int,
    dim: int = _POS_ENC_DIM,
) -> np.ndarray:
    """Encode keypoint geometry as a sinusoidal positional embedding.

    Each keypoint (x, y, size, angle) is mapped to a ``dim``-dimensional
    vector by applying sin/cos at multiple frequencies — the same principle
    used in transformers and in the SuperGlue position encoder MLP.

    Args:
        keypoints: OpenCV KeyPoint list.
        img_width: Reference image width for coordinate normalisation.
        img_height: Reference image height for coordinate normalisation.
        dim: Output embedding dimension (must be divisible by 4).

    Returns:
        Array of shape ``(N, dim)`` float32.
    """
    if dim % 4 != 0:
        raise ValueError("dim must be divisible by 4")
    n = len(keypoints)
    if n == 0:
        return np.empty((0, dim), dtype=np.float32)

    # Normalise coordinates to [-1, 1]
    x = np.array([kp.pt[0] for kp in keypoints], dtype=np.float64) / max(img_width, 1) * 2 - 1
    y = np.array([kp.pt[1] for kp in keypoints], dtype=np.float64) / max(img_height, 1) * 2 - 1
    # Normalise scale and angle
    scale = np.array([kp.size for kp in keypoints], dtype=np.float64) / max(img_width, img_height, 1)
    angle = np.array([kp.angle if kp.angle >= 0 else 0.0 for kp in keypoints], dtype=np.float64) / 360.0

    features = np.stack([x, y, scale, angle], axis=1)  # (N, 4)

    # Frequencies for each of the 4 feature channels
    d = dim // 4  # per-channel dimension; 4 channels × 2 (sin+cos) × d = 8d total, but we use dim=4*2*(d//2) trick
    # Simpler: produce dim//4 frequencies, 4 channels × sin+cos = dim total
    freqs = np.power(10000.0, np.arange(dim // 8, dtype=np.float64) / float(max(dim // 8, 1)))  # (dim//8,)

    # Build encoding: sin and cos at each frequency for each of 4 channels
    enc_parts = []
    for ch in range(4):
        v = features[:, ch:ch+1] * freqs[np.newaxis, :]   # (N, dim//8)
        enc_parts.append(np.sin(v))
        enc_parts.append(np.cos(v))

    # 8 parts × (N, dim//8) → concat → (N, dim)
    encoding = np.concatenate(enc_parts, axis=1)  # (N, dim)
    return encoding.astype(np.float32)


# ─────────────────────────────────────────────────────────────────────────────
# Sinkhorn log-domain iterations
# ─────────────────────────────────────────────────────────────────────────────

def _log_sinkhorn(
    log_alpha: np.ndarray,
    n_iters: int = _SINKHORN_ITERS,
) -> np.ndarray:
    """Run Sinkhorn iterations entirely in log domain for numerical stability.

    The matrix ``log_alpha`` has shape ``(M+1, N+1)`` where the last row/col
    are dustbin entries.  After ``n_iters`` alternating log-sum-exp
    normalisations the result approximates a doubly-stochastic matrix (on the
    non-dustbin entries).

    Args:
        log_alpha: Log-score matrix including dustbin row and column.
        n_iters: Number of Sinkhorn iterations.

    Returns:
        Log-domain soft assignment matrix, same shape as input.
    """
    m1, n1 = log_alpha.shape  # (M+1, N+1)
    # Uniform log-marginals — every row and column has equal mass = 1
    log_mu = np.zeros(m1, dtype=np.float64)
    log_nu = np.zeros(n1, dtype=np.float64)

    u = np.zeros(m1, dtype=np.float64)
    v = np.zeros(n1, dtype=np.float64)

    for _ in range(n_iters):
        # Row normalisation: u = log_mu - logsumexp(log_alpha + v, axis=1)
        u = log_mu - _logsumexp(log_alpha + v[np.newaxis, :], axis=1)
        # Column normalisation: v = log_nu - logsumexp(log_alpha + u, axis=0)
        v = log_nu - _logsumexp(log_alpha + u[:, np.newaxis], axis=0)

    return log_alpha + u[:, np.newaxis] + v[np.newaxis, :]


def _logsumexp(x: np.ndarray, axis: int) -> np.ndarray:
    """Numerically stable logsumexp along an axis."""
    x_max = np.max(x, axis=axis, keepdims=True)
    out = np.log(np.sum(np.exp(x - x_max), axis=axis) + 1e-10) + x_max.squeeze(axis=axis)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Public matcher class
# ─────────────────────────────────────────────────────────────────────────────

class SuperGlueMatcher:
    """SuperGlue-architecture Sinkhorn optimal-transport matcher.

    Drop-in simulation replacement for the BF/FLANN matcher for the
    ``superglue`` feature method.  Accepts standard OpenCV KeyPoint lists
    and float32 descriptors; returns ``List[MatchPairModel]`` — the same
    contract as ``FeatureMatcher.match()``.

    Determinism:
        All stochastic elements are seeded with ``seed`` (default 26166).
        Identical inputs → identical outputs on every run.

    Args:
        match_threshold: Minimum soft-assignment probability to accept a hard
            match (applied after exp of the Sinkhorn output).
        sinkhorn_iters: Number of Sinkhorn normalisation iterations.
        temperature: Score matrix scaling factor τ (lower = sharper peaks).
        seed: RNG seed for reproducibility.
    """

    def __init__(
        self,
        match_threshold: float = 0.2,
        sinkhorn_iters: int = _SINKHORN_ITERS,
        temperature: float = _TEMPERATURE,
        seed: int = _SEED,
    ) -> None:
        self.match_threshold = match_threshold
        self.sinkhorn_iters = sinkhorn_iters
        self.temperature = temperature
        self.seed = seed

    # ------------------------------------------------------------------
    # Primary entry point
    # ------------------------------------------------------------------

    def match(
        self,
        kps_ref: List[cv2.KeyPoint],
        desc_ref: np.ndarray,
        kps_mov: List[cv2.KeyPoint],
        desc_mov: np.ndarray,
        img_width: int = 512,
        img_height: int = 512,
    ) -> Tuple[List[MatchPairModel], int]:
        """Run SuperGlue-style matching.

        Args:
            kps_ref: Reference keypoints.
            desc_ref: Reference descriptors ``(M, D)`` float32.
            kps_mov: Moving keypoints.
            desc_mov: Moving descriptors ``(N, D)`` float32.
            img_width: Image width for position encoding normalisation.
            img_height: Image height for position encoding normalisation.

        Returns:
            filtered_matches: Accepted ``MatchPairModel`` list.
            candidate_count: Total score-matrix entries evaluated (M × N).
        """
        rng = np.random.RandomState(self.seed)

        if len(kps_ref) == 0 or len(kps_mov) == 0:
            logger.warning("SuperGlue: empty keypoint lists — returning no matches")
            return [], 0
        if desc_ref is None or desc_mov is None:
            logger.warning("SuperGlue: None descriptors — returning no matches")
            return [], 0

        desc_r = np.asarray(desc_ref, dtype=np.float32)
        desc_m = np.asarray(desc_mov, dtype=np.float32)

        # ── 1. Position encoding ────────────────────────────────────────────
        pos_ref = _sinusoidal_position_encoding(kps_ref, img_width, img_height)  # (M, P)
        pos_mov = _sinusoidal_position_encoding(kps_mov, img_width, img_height)  # (N, P)

        # ── 2. Augment descriptors with position encoding ───────────────────
        # Simulate the GNN encoder: concat then L2-normalise (no MLP weights)
        aug_ref = self._augment(desc_r, pos_ref, rng)   # (M, D+P)
        aug_mov = self._augment(desc_m, pos_mov, rng)   # (N, D+P)

        # ── 3. Cosine score matrix ──────────────────────────────────────────
        # S[i, j] = cosine_similarity(aug_ref[i], aug_mov[j]) / τ
        scores = self._cosine_score_matrix(aug_ref, aug_mov)  # (M, N)
        m_kps, n_kps = scores.shape
        candidate_count = m_kps * n_kps

        # ── 4. Dustbin augmentation ─────────────────────────────────────────
        # Append one dustbin row (for unmatched ref kps) and column (for unmatched mov kps)
        dustbin_row = np.full((1, n_kps), _DUSTBIN_SCORE / self.temperature, dtype=np.float64)
        dustbin_col = np.full((m_kps + 1, 1), _DUSTBIN_SCORE / self.temperature, dtype=np.float64)
        log_alpha = np.vstack([scores.astype(np.float64), dustbin_row])
        log_alpha = np.hstack([log_alpha, dustbin_col])   # (M+1, N+1)

        # ── 5. Sinkhorn iterations ──────────────────────────────────────────
        log_P = _log_sinkhorn(log_alpha, n_iters=self.sinkhorn_iters)
        P = np.exp(log_P[:m_kps, :n_kps])   # soft assignment, excluding dustbin

        # ── 6. Hard assignment with mutual nearest-neighbour filter ─────────
        matches = self._hard_assignment(P, kps_ref, kps_mov)

        logger.info(
            f"SuperGlue (Sinkhorn sim, seed={self.seed}): "
            f"{len(kps_ref)} × {len(kps_mov)} → {len(matches)} matches "
            f"(threshold={self.match_threshold}, iters={self.sinkhorn_iters})"
        )
        return matches, candidate_count

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _augment(
        self, desc: np.ndarray, pos: np.ndarray, rng: np.random.RandomState
    ) -> np.ndarray:
        """Concat descriptor with position encoding and L2-normalise.

        In real SuperGlue this is an MLP with learned weights.  Here we use a
        small deterministic perturbation (scaled by a fixed RNG draw seeded
        consistently) to simulate the non-linearity effect without true
        learned weights.
        """
        # Pad positional encoding to match descriptor dim if needed
        d = desc.shape[1]
        p = pos.shape[1] if pos.ndim == 2 and len(pos) > 0 else 0

        if p == 0:
            aug = desc.astype(np.float64)
        else:
            # Align dims: project pos to descriptor dim via a fixed random matrix
            proj_key = f"proj_{d}_{p}"
            if not hasattr(self, "_proj_cache"):
                self._proj_cache = {}
            if proj_key not in self._proj_cache:
                proj_rng = np.random.RandomState(self.seed + 1)
                self._proj_cache[proj_key] = proj_rng.randn(p, d).astype(np.float32) * 0.1
            W = self._proj_cache[proj_key]
            pos_proj = pos.astype(np.float32) @ W   # (N, d)
            aug = (desc + pos_proj).astype(np.float64)

        # L2 normalise row-wise
        norms = np.linalg.norm(aug, axis=1, keepdims=True)
        norms = np.where(norms < 1e-8, 1.0, norms)
        return (aug / norms).astype(np.float64)

    def _cosine_score_matrix(
        self, aug_ref: np.ndarray, aug_mov: np.ndarray
    ) -> np.ndarray:
        """Compute scaled cosine similarity matrix (M × N).

        Both inputs are already L2-normalised, so dot product = cosine sim.
        Scale by 1/τ as SuperGlue does before Sinkhorn.
        """
        S = aug_ref @ aug_mov.T   # (M, N) — cosine similarity
        return (S / self.temperature).astype(np.float64)

    def _hard_assignment(
        self,
        P: np.ndarray,
        kps_ref: List[cv2.KeyPoint],
        kps_mov: List[cv2.KeyPoint],
    ) -> List[MatchPairModel]:
        """Convert soft assignment matrix to hard matches.

        Strategy:
          - For each ref keypoint i, find its best moving keypoint j = argmax P[i, :].
          - For each mov keypoint j, find its best ref keypoint i' = argmax P[:, j].
          - Accept (i, j) only if i == i' (mutual nearest neighbour) AND
            P[i, j] >= match_threshold.  This is the standard SuperGlue
            decoding step.
        """
        m, n = P.shape
        best_mov_for_ref = np.argmax(P, axis=1)   # (M,) — best j for each i
        best_ref_for_mov = np.argmax(P, axis=0)   # (N,) — best i for each j

        matches: List[MatchPairModel] = []
        for i in range(m):
            j = int(best_mov_for_ref[i])
            # Mutual nearest-neighbour check
            if best_ref_for_mov[j] != i:
                continue
            # Threshold check
            if P[i, j] < self.match_threshold:
                continue
            ref_pt = [float(kps_ref[i].pt[0]), float(kps_ref[i].pt[1])]
            mov_pt = [float(kps_mov[j].pt[0]), float(kps_mov[j].pt[1])]
            # Use (1 - P[i,j]) as a proxy distance so that higher confidence = lower distance
            distance = float(1.0 - P[i, j])
            matches.append(MatchPairModel(
                ref_idx=i,
                mov_idx=j,
                distance=round(distance, 6),
                ref_pt=ref_pt,
                mov_pt=mov_pt,
                is_inlier=False,
                is_spatially_selected=False,
            ))

        return matches
