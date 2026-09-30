"""SuperGlue feature matcher.

Supports both:
  1. PyTorch CPU inference using learned SuperGlue graph neural network weights.
  2. Deterministic Sinkhorn optimal-transport matcher simulation (reproducing
     the architecture without requiring external weights).
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import numpy as np
import torch

from .superglue_model import SuperGlue
from ..models.schemas import MatchPairModel
from ..utils.logging import logger

# ─────────────────────────────────────────────────────────────────────────────
# Constants that mirror typical SuperGlue hyper-parameters
# ─────────────────────────────────────────────────────────────────────────────
_SINKHORN_ITERS: int = 100        # iterations until convergence (paper uses 100)
_TEMPERATURE: float = 0.1         # score-scaling temperature tau
_DUSTBIN_SCORE: float = 1.0       # initial dustbin logit
_POS_ENC_DIM: int = 64            # sinusoidal encoding dimension (must be even)
_SEED: int = 26166                 # SIH 2026 deterministic seed


# ─────────────────────────────────────────────────────────────────────────────
# Position encoding & math helpers (exported for testing)
# ─────────────────────────────────────────────────────────────────────────────

def _sinusoidal_position_encoding(
    keypoints: List[cv2.KeyPoint],
    img_width: int,
    img_height: int,
    dim: int = _POS_ENC_DIM,
) -> np.ndarray:
    """Encode keypoint geometry as a sinusoidal positional embedding."""
    if dim % 4 != 0:
        raise ValueError("dim must be divisible by 4")
    n = len(keypoints)
    if n == 0:
        return np.empty((0, dim), dtype=np.float32)

    x = np.array([kp.pt[0] for kp in keypoints], dtype=np.float64) / max(img_width, 1) * 2 - 1
    y = np.array([kp.pt[1] for kp in keypoints], dtype=np.float64) / max(img_height, 1) * 2 - 1
    scale = np.array([kp.size for kp in keypoints], dtype=np.float64) / max(img_width, img_height, 1)
    angle = np.array([kp.angle if kp.angle >= 0 else 0.0 for kp in keypoints], dtype=np.float64) / 360.0

    features = np.stack([x, y, scale, angle], axis=1)  # (N, 4)

    freqs = np.power(10000.0, np.arange(dim // 8, dtype=np.float64) / float(max(dim // 8, 1)))

    enc_parts = []
    for ch in range(4):
        v = features[:, ch:ch + 1] * freqs[np.newaxis, :]
        enc_parts.append(np.sin(v))
        enc_parts.append(np.cos(v))

    encoding = np.concatenate(enc_parts, axis=1)
    return encoding.astype(np.float32)


def _logsumexp(x: np.ndarray, axis: int) -> np.ndarray:
    """Numerically stable logsumexp along an axis."""
    x_max = np.max(x, axis=axis, keepdims=True)
    out = np.log(np.sum(np.exp(x - x_max), axis=axis) + 1e-10) + x_max.squeeze(axis=axis)
    return out


def _log_sinkhorn(
    log_alpha: np.ndarray,
    n_iters: int = _SINKHORN_ITERS,
) -> np.ndarray:
    """Run Sinkhorn iterations entirely in log domain for numerical stability."""
    m1, n1 = log_alpha.shape
    log_mu = np.zeros(m1, dtype=np.float64)
    log_nu = np.zeros(n1, dtype=np.float64)

    u = np.zeros(m1, dtype=np.float64)
    v = np.zeros(n1, dtype=np.float64)

    for _ in range(n_iters):
        u = log_mu - _logsumexp(log_alpha + v[np.newaxis, :], axis=1)
        v = log_nu - _logsumexp(log_alpha + u[:, np.newaxis], axis=0)

    return log_alpha + u[:, np.newaxis] + v[np.newaxis, :]


# ─────────────────────────────────────────────────────────────────────────────
# SuperGlue Matcher
# ─────────────────────────────────────────────────────────────────────────────

class SuperGlueMatcher:
    """SuperGlue feature matcher supporting both learned PyTorch model inference
    and Sinkhorn optimal-transport simulation.
    """

    def __init__(
        self,
        sp_weights: str = "",
        sg_weights: str = "",
        match_threshold: float = 0.2,
        sinkhorn_iters: int = _SINKHORN_ITERS,
        temperature: float = _TEMPERATURE,
        seed: int = _SEED,
    ) -> None:
        self.match_threshold = match_threshold
        self.sinkhorn_iters = sinkhorn_iters
        self.temperature = temperature
        self.seed = seed

        self.sp_weights_path = Path(sp_weights) if sp_weights else None
        self.sg_weights_path = (
            Path(sg_weights)
            if sg_weights
            else (Path(__file__).resolve().parent.parent.parent / "weights" / "superglue_outdoor.pth")
        )

        self.model: Optional[SuperGlue] = None
        self.device = torch.device("cpu")

        if sg_weights or self.sg_weights_path.exists():
            if not self.sg_weights_path.exists():
                raise FileNotFoundError(f"SuperGlue weights not found: {self.sg_weights_path}")
            torch.manual_seed(seed)
            try:
                torch.use_deterministic_algorithms(True)
            except Exception:
                pass

            config = {
                "weights_path": str(self.sg_weights_path),
                "descriptor_dim": 256,
                "weights": "outdoor",
                "sinkhorn_iterations": 20,
                "match_threshold": match_threshold,
            }
            self.model = SuperGlue(config)
            self.model.to(self.device)
            self.model.eval()

    # ------------------------------------------------------------------
    # Dispatching Match Entry Point
    # ------------------------------------------------------------------

    def match(
        self,
        arg1: Any,
        arg2: Any,
        arg3: Any,
        arg4: Any,
        arg5: Any = 512,
        arg6: Any = 512,
    ) -> Union[Tuple[List[MatchPairModel], int], Dict[str, Any]]:
        """Match keypoints between reference and moving images.

        Supports two interfaces:
        1. Simulated Sinkhorn interface:
           match(kps_ref, desc_ref, kps_mov, desc_mov, img_width=512, img_height=512)
           -> (List[MatchPairModel], candidate_count: int)

        2. Neural / Array interface:
           match(kp_a, desc_a, kp_b, desc_b, img_a_shape=(H, W), img_b_shape=(H, W))
           -> {"matches": (N, 2) ndarray, "scores": (N,) ndarray, "ms": float}
        """
        # Distinguish between convention 1 (List of KeyPoints) and convention 2 (ndarray coordinates + shape tuples)
        if isinstance(arg1, list) or not isinstance(arg5, (tuple, list)):
            return self._match_simulation(
                kps_ref=arg1,
                desc_ref=arg2,
                kps_mov=arg3,
                desc_mov=arg4,
                img_width=int(arg5) if isinstance(arg5, (int, float)) else 512,
                img_height=int(arg6) if isinstance(arg6, (int, float)) else 512,
            )
        else:
            return self._match_neural(
                kp_a=arg1,
                desc_a=arg2,
                kp_b=arg3,
                desc_b=arg4,
                img_a_shape=arg5,
                img_b_shape=arg6,
            )

    # ------------------------------------------------------------------
    # Neural Mode (PyTorch)
    # ------------------------------------------------------------------

    def _match_neural(
        self,
        kp_a: np.ndarray,
        desc_a: np.ndarray,
        kp_b: np.ndarray,
        desc_b: np.ndarray,
        img_a_shape: Tuple[int, ...],
        img_b_shape: Tuple[int, ...],
    ) -> Dict[str, Any]:
        t0 = time.perf_counter()

        if kp_a is None or kp_b is None or len(kp_a) == 0 or len(kp_b) == 0:
            return {
                "matches": np.empty((0, 2), dtype=int),
                "scores": np.empty((0,), dtype=np.float32),
                "ms": 0.0,
            }

        h_a, w_a = img_a_shape[:2]
        h_b, w_b = img_b_shape[:2]

        if desc_a.shape[1] < 256:
            pad_a = 256 - desc_a.shape[1]
            desc_a_padded = np.pad(desc_a, ((0, 0), (0, pad_a)), mode="constant").astype(np.float32)
        else:
            desc_a_padded = desc_a[:, :256].astype(np.float32)

        if desc_b.shape[1] < 256:
            pad_b = 256 - desc_b.shape[1]
            desc_b_padded = np.pad(desc_b, ((0, 0), (0, pad_b)), mode="constant").astype(np.float32)
        else:
            desc_b_padded = desc_b[:, :256].astype(np.float32)

        kpts0_t = torch.from_numpy(kp_a.astype(np.float32)).unsqueeze(0).to(self.device)
        kpts1_t = torch.from_numpy(kp_b.astype(np.float32)).unsqueeze(0).to(self.device)

        desc0_t = torch.from_numpy(desc_a_padded).unsqueeze(0).transpose(1, 2).to(self.device)
        desc1_t = torch.from_numpy(desc_b_padded).unsqueeze(0).transpose(1, 2).to(self.device)

        scores0 = torch.ones(kpts0_t.shape[:2], device=self.device)
        scores1 = torch.ones(kpts1_t.shape[:2], device=self.device)

        dummy_img0 = torch.empty((1, 1, h_a, w_a), device=self.device)
        dummy_img1 = torch.empty((1, 1, h_b, w_b), device=self.device)

        data = {
            "keypoints0": kpts0_t,
            "keypoints1": kpts1_t,
            "descriptors0": desc0_t,
            "descriptors1": desc1_t,
            "scores0": scores0,
            "scores1": scores1,
            "image0": dummy_img0,
            "image1": dummy_img1,
        }

        with torch.no_grad():
            pred = self.model(data)
            matches0 = pred["matches0"][0].cpu().numpy()
            conf0 = pred["matching_scores0"][0].cpu().numpy()

        valid = matches0 > -1
        idx_a = np.where(valid)[0]
        idx_b = matches0[valid]
        match_scores = conf0[valid]

        if len(idx_a) > 0:
            matches_arr = np.column_stack([idx_a, idx_b])
        else:
            matches_arr = np.empty((0, 2), dtype=int)

        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        return {
            "matches": matches_arr,
            "scores": match_scores.astype(np.float32),
            "ms": round(elapsed_ms, 2),
        }

    # ------------------------------------------------------------------
    # Simulation Mode (Sinkhorn optimal transport)
    # ------------------------------------------------------------------

    def _match_simulation(
        self,
        kps_ref: List[cv2.KeyPoint],
        desc_ref: np.ndarray,
        kps_mov: List[cv2.KeyPoint],
        desc_mov: np.ndarray,
        img_width: int = 512,
        img_height: int = 512,
    ) -> Tuple[List[MatchPairModel], int]:
        rng = np.random.RandomState(self.seed)

        if len(kps_ref) == 0 or len(kps_mov) == 0:
            logger.warning("SuperGlue: empty keypoint lists — returning no matches")
            return [], 0
        if desc_ref is None or desc_mov is None:
            logger.warning("SuperGlue: None descriptors — returning no matches")
            return [], 0

        desc_r = np.asarray(desc_ref, dtype=np.float32)
        desc_m = np.asarray(desc_mov, dtype=np.float32)

        pos_ref = _sinusoidal_position_encoding(kps_ref, img_width, img_height)
        pos_mov = _sinusoidal_position_encoding(kps_mov, img_width, img_height)

        aug_ref = self._augment(desc_r, pos_ref, rng)
        aug_mov = self._augment(desc_m, pos_mov, rng)

        scores = self._cosine_score_matrix(aug_ref, aug_mov)
        m_kps, n_kps = scores.shape
        candidate_count = m_kps * n_kps

        dustbin_row = np.full((1, n_kps), _DUSTBIN_SCORE / self.temperature, dtype=np.float64)
        dustbin_col = np.full((m_kps + 1, 1), _DUSTBIN_SCORE / self.temperature, dtype=np.float64)
        log_alpha = np.vstack([scores.astype(np.float64), dustbin_row])
        log_alpha = np.hstack([log_alpha, dustbin_col])

        log_P = _log_sinkhorn(log_alpha, n_iters=self.sinkhorn_iters)
        P = np.exp(log_P[:m_kps, :n_kps])

        matches = self._hard_assignment(P, kps_ref, kps_mov)

        logger.info(
            f"SuperGlue (Sinkhorn sim, seed={self.seed}): "
            f"{len(kps_ref)} x {len(kps_mov)} -> {len(matches)} matches "
            f"(threshold={self.match_threshold}, iters={self.sinkhorn_iters})"
        )
        return matches, candidate_count

    def _augment(
        self, desc: np.ndarray, pos: np.ndarray, rng: np.random.RandomState
    ) -> np.ndarray:
        d = desc.shape[1]
        p = pos.shape[1] if pos.ndim == 2 and len(pos) > 0 else 0

        if p == 0:
            aug = desc.astype(np.float64)
        else:
            proj_key = f"proj_{d}_{p}"
            if not hasattr(self, "_proj_cache"):
                self._proj_cache = {}
            if proj_key not in self._proj_cache:
                proj_rng = np.random.RandomState(self.seed + 1)
                self._proj_cache[proj_key] = proj_rng.randn(p, d).astype(np.float32) * 0.1
            W = self._proj_cache[proj_key]
            pos_proj = pos.astype(np.float32) @ W
            aug = (desc + pos_proj).astype(np.float64)

        norms = np.linalg.norm(aug, axis=1, keepdims=True)
        norms = np.where(norms < 1e-8, 1.0, norms)
        return (aug / norms).astype(np.float64)

    def _cosine_score_matrix(
        self, aug_ref: np.ndarray, aug_mov: np.ndarray
    ) -> np.ndarray:
        S = aug_ref @ aug_mov.T
        return (S / self.temperature).astype(np.float64)

    def _hard_assignment(
        self,
        P: np.ndarray,
        kps_ref: List[cv2.KeyPoint],
        kps_mov: List[cv2.KeyPoint],
    ) -> List[MatchPairModel]:
        m, n = P.shape
        best_mov_for_ref = np.argmax(P, axis=1)
        best_ref_for_mov = np.argmax(P, axis=0)

        matches: List[MatchPairModel] = []
        for i in range(m):
            j = int(best_mov_for_ref[i])
            if best_ref_for_mov[j] != i:
                continue
            if P[i, j] < self.match_threshold:
                continue
            ref_pt = [float(kps_ref[i].pt[0]), float(kps_ref[i].pt[1])]
            mov_pt = [float(kps_mov[j].pt[0]), float(kps_mov[j].pt[1])]
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
