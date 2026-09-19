"""Thin-Plate Spline (TPS) non-rigid deformation correction.

Papers:
- SCDF (arXiv 2608.22300v1), Sec. III-E: "thin-plate splines suit dense elastic fields."
  Cites Bookstein 1989, "Principal warps: Thin-plate splines and the decomposition
  of deformations."
- Mohammadi et al. (d3eb99b9...), Sec. 2.2.1.
"""
from typing import Callable, Optional, Tuple
import cv2
import numpy as np
from scipy.interpolate import RBFInterpolator


def fit_tps(
    src_pts: np.ndarray,
    dst_pts: np.ndarray,
    regularization: float = 0.0,
) -> Optional[Callable[[np.ndarray], np.ndarray]]:
    """Fit a Thin-Plate Spline (TPS) transformation from src_pts to dst_pts.

    Uses scipy.interpolate.RBFInterpolator with kernel='thin_plate_spline'
    and smoothing=regularization. Fits element-wise across coordinate axes.

    Args:
        src_pts: (N, 2) float64 source pixel coordinates.
        dst_pts: (N, 2) float64 destination pixel coordinates.
        regularization: Smoothing regularization parameter (default: 0.0).

    Returns:
        Callable f(pts) -> transformed coordinates (M, 2), or None if N < 10
        (minimum inliers required for TPS numerical stability).
    """
    src_arr = np.asarray(src_pts, dtype=np.float64)
    dst_arr = np.asarray(dst_pts, dtype=np.float64)

    if src_arr.ndim != 2 or dst_arr.ndim != 2:
        return None
    if src_arr.shape[1] != 2 or dst_arr.shape[1] != 2:
        return None
    if len(src_arr) < 10 or len(dst_arr) < 10 or src_arr.shape[0] != dst_arr.shape[0]:
        return None

    # Deduplicate exact coincident source points to avoid singular matrix
    _, u_idx = np.unique(np.round(src_arr, decimals=6), axis=0, return_index=True)
    if len(u_idx) < 10:
        return None
    src_u = src_arr[u_idx]
    dst_u = dst_arr[u_idx]

    # 1. Base affine model (decomposition: Bookstein 1989 / SCDF Sec. III-E)
    M, _ = cv2.estimateAffine2D(src_u, dst_u)
    if M is None:
        M, _ = cv2.estimateAffinePartial2D(src_u, dst_u)
    if M is None:
        return None

    base_train = cv2.transform(src_u.reshape(-1, 1, 2), M).reshape(-1, 2)
    res_u = dst_u - base_train

    # If residuals are essentially zero (identity or perfect affine), return exact affine
    if np.max(np.abs(res_u)) < 1e-9:
        def affine_fn(pts: np.ndarray) -> np.ndarray:
            p = np.asarray(pts, dtype=np.float64)
            is_1d = (p.ndim == 1)
            p2d = p.reshape(1, -1) if is_1d else p
            out = cv2.transform(p2d.reshape(-1, 1, 2), M).reshape(-1, 2)
            return out[0] if is_1d else out
        return affine_fn

    # 2. Cross-validate residual shrinkage alpha on an internal split
    N = len(src_u)
    inner_split = int(0.8 * N)
    rng = np.random.default_rng(26166)
    perm = rng.permutation(N)
    tr_idx, val_idx = perm[:inner_split], perm[inner_split:]

    smooth = float(regularization) if regularization > 0 else 1.0
    try:
        rbf_x_in = RBFInterpolator(src_u[tr_idx], res_u[tr_idx, 0], kernel="thin_plate_spline", smoothing=smooth)
        rbf_y_in = RBFInterpolator(src_u[tr_idx], res_u[tr_idx, 1], kernel="thin_plate_spline", smoothing=smooth)

        val_base = base_train[val_idx]
        val_disp = np.column_stack([rbf_x_in(src_u[val_idx]), rbf_y_in(src_u[val_idx])])
        val_target = dst_u[val_idx]

        num = np.sum(val_disp * (val_target - val_base))
        den = np.sum(val_disp ** 2)
        alpha = float(np.clip(num / max(den, 1e-8), 0.0, 1.0)) if den > 1e-8 else 0.0

        rbf_x = RBFInterpolator(src_u, res_u[:, 0], kernel="thin_plate_spline", smoothing=smooth)
        rbf_y = RBFInterpolator(src_u, res_u[:, 1], kernel="thin_plate_spline", smoothing=smooth)
    except Exception:
        return None

    def tps_fn(pts: np.ndarray) -> np.ndarray:
        p = np.asarray(pts, dtype=np.float64)
        is_1d = (p.ndim == 1)
        p2d = p.reshape(1, -1) if is_1d else p
        base = cv2.transform(p2d.reshape(-1, 1, 2), M).reshape(-1, 2)
        disp = np.column_stack([rbf_x(p2d), rbf_y(p2d)])
        res = base + alpha * disp
        return res[0] if is_1d else res

    return tps_fn


def apply_tps(
    tps_fn: Callable[[np.ndarray], np.ndarray],
    image: np.ndarray,
    out_shape: Tuple[int, int],
) -> np.ndarray:
    """Warp image using an inverse TPS mapping via cv2.remap.

    Coordinate Mapping & Inverse Warp Semantics:
    cv2.remap requires backward/inverse coordinates for each destination pixel:
    for every output pixel (x, y) in the grid, map_x[y, x] and map_y[y, x] specify
    the corresponding source coordinate in the input image.
    Because a standard forward TPS maps source -> destination, to warp an image
    using cv2.remap, one must fit the inverse TPS from dst_pts -> src_pts.
    apply_tps evaluates this inverse mapping across the dense destination grid
    and warps the image using bicubic interpolation and reflection padding.

    Args:
        tps_fn: Callable mapping destination coordinates (N, 2) to source coordinates (N, 2).
        image: Input image (H, W) or (H, W, C).
        out_shape: Output image shape as (height, width).

    Returns:
        Warped image with shape (out_shape[0], out_shape[1], ...) using
        cv2.INTER_CUBIC and cv2.BORDER_REFLECT.
    """
    H_out, W_out = int(out_shape[0]), int(out_shape[1])
    grid_x, grid_y = np.meshgrid(
        np.arange(W_out, dtype=np.float32),
        np.arange(H_out, dtype=np.float32),
    )
    coords = np.column_stack([grid_x.ravel(), grid_y.ravel()])
    src_coords = tps_fn(coords)

    map_x = src_coords[:, 0].reshape(H_out, W_out).astype(np.float32)
    map_y = src_coords[:, 1].reshape(H_out, W_out).astype(np.float32)

    return cv2.remap(
        image,
        map_x,
        map_y,
        interpolation=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REFLECT,
    )
