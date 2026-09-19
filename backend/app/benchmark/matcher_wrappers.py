"""Matcher wrappers for benchmarking SuperGlue, LightGlue, and LoFTR.

All wrappers accept the same standardized inputs (keypoints and descriptors extracted
by RIFT2, except detector-free LoFTR which detects its own correspondence field) so
that the comparison is honest, matcher-vs-matcher.
"""
from __future__ import annotations

import os
import ssl
import time
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn

# Fix local SSL verification issues when fetching checkpoints if needed
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except Exception:
    pass

_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
_WEIGHTS_DIR = _BACKEND_DIR / "weights"


# ==============================================================================
# SuperGlue PyTorch Architecture (MagicLeap)
# ==============================================================================
def _make_mlp(channels: list[int], do_bn: bool = True) -> nn.Sequential:
    layers = []
    for i in range(1, len(channels)):
        layers.append(nn.Conv1d(channels[i - 1], channels[i], kernel_size=1, bias=True))
        if i < (len(channels) - 1):
            if do_bn:
                layers.append(nn.BatchNorm1d(channels[i]))
            layers.append(nn.ReLU())
    return nn.Sequential(*layers)


class _KeypointEncoder(nn.Module):
    def __init__(self, feature_dim: int, layers: list[int]):
        super().__init__()
        self.encoder = _make_mlp([3] + layers + [feature_dim])

    def forward(self, kpts: torch.Tensor, scores: torch.Tensor) -> torch.Tensor:
        inputs = [kpts.transpose(1, 2), scores.unsqueeze(1)]
        return self.encoder(torch.cat(inputs, dim=1))


class _MultiHeadedAttention(nn.Module):
    def __init__(self, num_heads: int, d_model: int):
        super().__init__()
        assert d_model % num_heads == 0
        self.dim = d_model // num_heads
        self.num_heads = num_heads
        self.merge = nn.Conv1d(d_model, d_model, kernel_size=1)
        self.proj = nn.ModuleList([deepcopy(self.merge) for _ in range(3)])

    def forward(self, query: torch.Tensor, key: torch.Tensor, value: torch.Tensor) -> torch.Tensor:
        batch_dim = query.size(0)
        query, key, value = [
            l(x).view(batch_dim, self.dim, self.num_heads, -1)
            for l, x in zip(self.proj, (query, key, value))
        ]
        dim = query.shape[1]
        scores = torch.einsum("bdhn,bdhm->bhnm", query, key) / (dim ** 0.5)
        prob = torch.nn.functional.softmax(scores, dim=-1)
        x = torch.einsum("bhnm,bdhm->bdhn", prob, value)
        return self.merge(x.contiguous().view(batch_dim, self.dim * self.num_heads, -1))


class _AttentionalPropagation(nn.Module):
    def __init__(self, feature_dim: int, num_heads: int):
        super().__init__()
        self.attn = _MultiHeadedAttention(num_heads, feature_dim)
        self.mlp = _make_mlp([feature_dim * 2, feature_dim * 2, feature_dim])

    def forward(self, x: torch.Tensor, source: torch.Tensor) -> torch.Tensor:
        message = self.attn(x, source, source)
        return self.mlp(torch.cat([x, message], dim=1))


class _AttentionalGNN(nn.Module):
    def __init__(self, feature_dim: int, layer_names: list[str]):
        super().__init__()
        self.layers = nn.ModuleList([
            _AttentionalPropagation(feature_dim, 4)
            for _ in range(len(layer_names))
        ])
        self.names = layer_names

    def forward(self, desc0: torch.Tensor, desc1: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        for layer, name in zip(self.layers, self.names):
            src0, src1 = (desc1, desc0) if name == "cross" else (desc0, desc1)
            delta0, delta1 = layer(desc0, src0), layer(desc1, src1)
            desc0, desc1 = (desc0 + delta0), (desc1 + delta1)
        return desc0, desc1


def _log_sinkhorn_iterations(Z: torch.Tensor, log_mu: torch.Tensor, log_nu: torch.Tensor, iters: int) -> torch.Tensor:
    u = torch.zeros_like(log_mu)
    v = torch.zeros_like(log_nu)
    for _ in range(iters):
        u = log_mu - torch.logsumexp(Z + v.unsqueeze(1), dim=2)
        v = log_nu - torch.logsumexp(Z + u.unsqueeze(2), dim=1)
    return Z + u.unsqueeze(2) + v.unsqueeze(1)


def _log_optimal_transport(scores: torch.Tensor, alpha: torch.Tensor, iters: int) -> torch.Tensor:
    b, m, n = scores.shape
    one = scores.new_tensor(1)
    ms, ns = (m * one).to(scores), (n * one).to(scores)

    bins0 = alpha.expand(b, m, 1)
    bins1 = alpha.expand(b, 1, n)
    alpha = alpha.expand(b, 1, 1)

    couplings = torch.cat([torch.cat([scores, bins0], -1),
                           torch.cat([bins1, alpha], -1)], 1)

    norm = - (ms + ns).log()
    log_mu = torch.cat([norm.expand(m), ns.log()[None] + norm])
    log_nu = torch.cat([norm.expand(n), ms.log()[None] + norm])
    log_mu, log_nu = log_mu[None].expand(b, -1), log_nu[None].expand(b, -1)

    Z = _log_sinkhorn_iterations(couplings, log_mu, log_nu, iters)
    Z = Z - norm
    return Z


class _SuperGlueModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.kenc = _KeypointEncoder(256, [32, 64, 128, 256])
        self.gnn = _AttentionalGNN(256, ["self", "cross"] * 9)
        self.final_proj = nn.Conv1d(256, 256, kernel_size=1, bias=True)
        self.bin_score = nn.Parameter(torch.tensor(1.0))

    def forward(self, kpts0: torch.Tensor, desc0: torch.Tensor,
                kpts1: torch.Tensor, desc1: torch.Tensor) -> torch.Tensor:
        scores0 = torch.ones(kpts0.shape[:2], device=kpts0.device)
        scores1 = torch.ones(kpts1.shape[:2], device=kpts1.device)
        desc0 = desc0 + self.kenc(kpts0, scores0)
        desc1 = desc1 + self.kenc(kpts1, scores1)
        desc0, desc1 = self.gnn(desc0, desc1)
        mdesc0, mdesc1 = self.final_proj(desc0), self.final_proj(desc1)
        scores = torch.einsum("bdn,bdm->bnm", mdesc0, mdesc1) / (256.0 ** 0.5)
        return _log_optimal_transport(scores, self.bin_score, 20)


# Module-level model caches
_SUPERGLUE_MODEL: Optional[_SuperGlueModel] = None
_LIGHTGLUE_MODEL: Optional[Any] = None
_LOFTR_MODEL: Optional[Any] = None


def _get_superglue(device: str = "cpu") -> _SuperGlueModel:
    global _SUPERGLUE_MODEL
    if _SUPERGLUE_MODEL is None:
        weights_path = _WEIGHTS_DIR / "superglue_outdoor.pth"
        if not weights_path.exists():
            raise FileNotFoundError(f"Weight file not found: {weights_path}")
        model = _SuperGlueModel()
        model.load_state_dict(torch.load(str(weights_path), map_location=device))
        model.to(device)
        model.eval()
        _SUPERGLUE_MODEL = model
    return _SUPERGLUE_MODEL


def _get_lightglue(device: str = "cpu") -> Any:
    global _LIGHTGLUE_MODEL
    if _LIGHTGLUE_MODEL is None:
        import kornia.feature as kf
        weights_path = _WEIGHTS_DIR / "superpoint_lightglue.pth"
        lg = kf.LightGlue(features="superpoint")
        if weights_path.exists():
            try:
                lg.load_state_dict(torch.load(str(weights_path), map_location=device), strict=False)
            except Exception:
                pass
        lg.to(device)
        lg.eval()
        _LIGHTGLUE_MODEL = lg
    return _LIGHTGLUE_MODEL


def _get_loftr(device: str = "cpu") -> Any:
    global _LOFTR_MODEL
    if _LOFTR_MODEL is None:
        import kornia.feature as kf
        loftr = kf.LoFTR(pretrained="outdoor")
        loftr.to(device)
        loftr.eval()
        _LOFTR_MODEL = loftr
    return _LOFTR_MODEL


# ==============================================================================
# Public Wrappers
# ==============================================================================
def superglue_match(
    kp_a: np.ndarray,
    desc_a: np.ndarray,
    kp_b: np.ndarray,
    desc_b: np.ndarray,
    img_a_shape: Tuple[int, ...],
    img_b_shape: Tuple[int, ...],
    device: str = "cpu",
) -> Dict[str, Any]:
    """Match features using SuperGlue (outdoor pretrained weights).

    RIFT2 descriptors (216-D) are zero-padded to 256-D to match SuperGlue's
    expected dimensionality. Keypoints are normalized to image coordinates [-1, 1].

    Returns:
      {
        "matches": np.ndarray of shape (N, 2),
        "time_ms": float,
        "reason": str | None,
      }
    """
    t0 = time.perf_counter()
    try:
        if len(kp_a) == 0 or len(kp_b) == 0:
            return {"matches": np.empty((0, 2), dtype=int), "time_ms": 0.0, "reason": "empty keypoints"}

        sg = _get_superglue(device)

        # Normalize keypoints to [-1, 1]
        h_a, w_a = img_a_shape[:2]
        h_b, w_b = img_b_shape[:2]
        kpts0_norm = kp_a.copy().astype(np.float32)
        kpts0_norm[:, 0] = 2.0 * (kpts0_norm[:, 0] + 0.5) / float(w_a) - 1.0
        kpts0_norm[:, 1] = 2.0 * (kpts0_norm[:, 1] + 0.5) / float(h_a) - 1.0

        kpts1_norm = kp_b.copy().astype(np.float32)
        kpts1_norm[:, 0] = 2.0 * (kpts1_norm[:, 0] + 0.5) / float(w_b) - 1.0
        kpts1_norm[:, 1] = 2.0 * (kpts1_norm[:, 1] + 0.5) / float(h_b) - 1.0

        # Pad 216-D RIFT2 descriptors with zeros to 256-D
        if desc_a.shape[1] < 256:
            pad_a = 256 - desc_a.shape[1]
            desc_a_padded = np.pad(desc_a, ((0, 0), (0, pad_a)), mode="constant")
        else:
            desc_a_padded = desc_a[:, :256]

        if desc_b.shape[1] < 256:
            pad_b = 256 - desc_b.shape[1]
            desc_b_padded = np.pad(desc_b, ((0, 0), (0, pad_b)), mode="constant")
        else:
            desc_b_padded = desc_b[:, :256]

        # Convert to torch tensors (float32)
        kpts0_t = torch.from_numpy(kpts0_norm).float().unsqueeze(0).to(device)
        desc0_t = torch.from_numpy(desc_a_padded.T).float().unsqueeze(0).to(device)
        kpts1_t = torch.from_numpy(kpts1_norm).float().unsqueeze(0).to(device)
        desc1_t = torch.from_numpy(desc_b_padded.T).float().unsqueeze(0).to(device)

        with torch.no_grad():
            scores = sg(kpts0_t, desc0_t, kpts1_t, desc1_t)
            m0, idx0 = scores[:, :-1, :-1].max(dim=2)
            m1, idx1 = scores[:, :-1, :-1].max(dim=1)
            n0 = kpts0_norm.shape[0]
            mutual = idx1.gather(1, idx0) == torch.arange(n0, device=device).unsqueeze(0)
            valid = mutual & (m0.exp() > 0.2)
            matches_arr = torch.stack([
                torch.arange(n0, device=device)[valid[0]],
                idx0[0][valid[0]]
            ], dim=-1).cpu().numpy()

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return {"matches": matches_arr, "time_ms": round(elapsed_ms, 1), "reason": None}

    except Exception as err:
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return {"matches": None, "time_ms": round(elapsed_ms, 1), "reason": str(err)}


def lightglue_match(
    kp_a: np.ndarray,
    desc_a: np.ndarray,
    kp_b: np.ndarray,
    desc_b: np.ndarray,
    img_a_shape: Tuple[int, ...],
    img_b_shape: Tuple[int, ...],
    device: str = "cpu",
) -> Dict[str, Any]:
    """Match features using LightGlue (SuperPoint-pretrained weights).

    RIFT2 descriptors (216-D) are zero-padded to 256-D.

    Returns:
      {
        "matches": np.ndarray of shape (N, 2),
        "time_ms": float,
        "reason": str | None,
      }
    """
    t0 = time.perf_counter()
    try:
        if len(kp_a) == 0 or len(kp_b) == 0:
            return {"matches": np.empty((0, 2), dtype=int), "time_ms": 0.0, "reason": "empty keypoints"}

        lg = _get_lightglue(device)

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

        data = {
            "image0": {
                "keypoints": torch.from_numpy(kp_a.astype(np.float32)).unsqueeze(0).to(device),
                "descriptors": torch.from_numpy(desc_a_padded).unsqueeze(0).to(device),
                "image_size": torch.tensor([[w_a, h_a]], dtype=torch.float32, device=device),
            },
            "image1": {
                "keypoints": torch.from_numpy(kp_b.astype(np.float32)).unsqueeze(0).to(device),
                "descriptors": torch.from_numpy(desc_b_padded).unsqueeze(0).to(device),
                "image_size": torch.tensor([[w_b, h_b]], dtype=torch.float32, device=device),
            },
        }

        with torch.no_grad():
            out = lg(data)
            matches_arr = out["matches"][0].cpu().numpy()

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return {"matches": matches_arr, "time_ms": round(elapsed_ms, 1), "reason": None}

    except Exception as err:
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return {"matches": None, "time_ms": round(elapsed_ms, 1), "reason": str(err)}


def loftr_match(
    kp_a: np.ndarray,
    desc_a: np.ndarray,
    kp_b: np.ndarray,
    desc_b: np.ndarray,
    img_a_shape: Tuple[int, ...],
    img_b_shape: Tuple[int, ...],
    device: str = "cpu",
    img_a: Optional[np.ndarray] = None,
    img_b: Optional[np.ndarray] = None,
) -> Dict[str, Any]:
    """Match images using LoFTR (Local Feature TRansformer).

    NOTE: LoFTR is detector-free and operates directly on raw image pixel grids,
    ignoring input keypoint coordinates and descriptors. It detects and matches its
    own dense correspondence field.

    Returns:
      {
        "matches": np.ndarray of shape (N, 2),
        "kpts0": np.ndarray of shape (N, 2),
        "kpts1": np.ndarray of shape (N, 2),
        "time_ms": float,
        "reason": str | None,
      }
    """
    t0 = time.perf_counter()
    try:
        if img_a is None or img_b is None:
            return {"matches": None, "time_ms": 0.0, "reason": "LoFTR requires raw images (detector-free)"}

        loftr = _get_loftr(device)

        t_ref = torch.from_numpy(img_a.astype(np.float32)).unsqueeze(0).unsqueeze(0) / 255.0
        t_mov = torch.from_numpy(img_b.astype(np.float32)).unsqueeze(0).unsqueeze(0) / 255.0
        t_ref, t_mov = t_ref.to(device), t_mov.to(device)

        with torch.no_grad():
            out = loftr({"image0": t_ref, "image1": t_mov})
            mkpts0 = out["keypoints0"].cpu().numpy()
            mkpts1 = out["keypoints1"].cpu().numpy()

        n_matches = len(mkpts0)
        idx_pairs = np.column_stack([np.arange(n_matches), np.arange(n_matches)]) if n_matches > 0 else np.empty((0, 2), dtype=int)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        return {
            "matches": idx_pairs,
            "kpts0": mkpts0,
            "kpts1": mkpts1,
            "time_ms": round(elapsed_ms, 1),
            "reason": None,
        }

    except Exception as err:
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return {"matches": None, "time_ms": round(elapsed_ms, 1), "reason": str(err)}
