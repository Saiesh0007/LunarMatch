"""Hyp-Net descriptor modulation service.

Paper: Hyp-Net (arXiv 2601.12325v1) — Multi-Sensor Matching with
       Hypernetworks. Lightweight module that computes adaptive per-
       channel scaling and shifting from global context, applied to
       a descriptor.
"""

from typing import Dict, Tuple
import numpy as np
import scipy.special

_WEIGHTS_CACHE: Dict[int, Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = {}


def _get_weights(dim: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Get deterministic placeholder weights for descriptor dimension D.

    Weights are deterministic placeholders seeded from 26166. When
    trained Hyp-Net weights become available (post-shortlist), replace
    W_s, W_t, b_s, b_t with the loaded tensors. The stage interface
    is identical.
    """
    if dim not in _WEIGHTS_CACHE:
        # Note: use 26166 and 26166+1 as separate seeds so the two matrices
        # are independent. Do NOT reuse the same RNG object.
        W_s = np.random.default_rng(26166).standard_normal((dim, dim)) * 0.1
        b_s = np.zeros(dim, dtype=np.float64)

        W_t = np.random.default_rng(26166 + 1).standard_normal((dim, dim)) * 0.1
        b_t = np.zeros(dim, dtype=np.float64)
        _WEIGHTS_CACHE[dim] = (W_s, b_s, W_t, b_t)
    return _WEIGHTS_CACHE[dim]


def _compute_global_context(descriptors: np.ndarray) -> np.ndarray:
    """Compute global context as mean over keypoints.

    Args:
        descriptors: shape (N, D) — N keypoints, D dims.

    Returns:
        shape (D,) — mean vector across keypoints.
    """
    if descriptors.size == 0 or descriptors.shape[0] == 0:
        dim = descriptors.shape[1] if descriptors.ndim > 1 else 0
        return np.zeros(dim, dtype=descriptors.dtype if descriptors.size > 0 else np.float32)
    return descriptors.mean(axis=0)


compute_global_context = _compute_global_context


def modulate(descriptors: np.ndarray, global_context: np.ndarray) -> np.ndarray:
    """Modulate descriptors using global context via adaptive scale and shift.

    Paper: Hyp-Net (arXiv 2601.12325v1) — Multi-Sensor Matching with
           Hypernetworks. Lightweight module that computes adaptive per-
           channel scaling and shifting from global context, applied to
           a descriptor.

    Weights are deterministic placeholders seeded from 26166. When
    trained Hyp-Net weights become available (post-shortlist), replace
    W_s, W_t, b_s, b_t with the loaded tensors. The stage interface
    is identical.

    Args:
        descriptors: shape (N, D) — N keypoints, D dims.
        global_context: shape (D,) — one summary vector for the image.

    Returns:
        shape (N, D), same dtype as descriptors.
    """
    if descriptors.size == 0 or descriptors.shape[0] == 0:
        return descriptors.copy()

    D = descriptors.shape[1]
    W_s, b_s, W_t, b_t = _get_weights(D)

    scale = scipy.special.expit(W_s @ global_context + b_s)  # (D,)
    shift = np.tanh(W_t @ global_context + b_t)              # (D,)

    out = descriptors * scale[np.newaxis, :] + shift[np.newaxis, :]
    return out.astype(descriptors.dtype)
