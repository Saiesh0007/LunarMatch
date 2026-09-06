"""
LunarMatch — Spatial Balancing & Spatial Coverage Module
SIH 2026 Problem Statement 26166

This module handles:
1. Spatial coverage quantification across the lunar image coordinate space.
2. Grid-based spatial balancing to avoid correspondence clustering in high-contrast/high-texture areas (e.g. crater rims).
3. Advanced Adaptive Non-Maximal Suppression (ANMS) for optimal continuous spatial spread.
4. Distribution analytics and UI visualization helper structures.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np


def _to_numpy_points(points: Any) -> np.ndarray:
    """
    Converts various point representations to a standard (N, 2) float64 numpy array.
    Supports:
    - numpy ndarrays of shape (N, 2)
    - list of [x, y] or (x, y) tuples
    - objects with .pt attribute (e.g., cv2.KeyPoint)
    """
    if points is None:
        return np.empty((0, 2), dtype=np.float64)

    if isinstance(points, np.ndarray):
        if points.size == 0:
            return np.empty((0, 2), dtype=np.float64)
        if points.ndim == 2 and points.shape[1] == 2:
            return points.astype(np.float64)
        if points.ndim == 3 and points.shape[1] == 1 and points.shape[2] == 2:
            # OpenCV shape convention e.g. (N, 1, 2)
            return points.reshape(-1, 2).astype(np.float64)
        raise ValueError(f"Expected points array of shape (N, 2) or (N, 1, 2), got {points.shape}")

    if isinstance(points, (list, tuple)):
        if len(points) == 0:
            return np.empty((0, 2), dtype=np.float64)
        # Check if elements are cv2.KeyPoint or have .pt attribute
        first = points[0]
        if hasattr(first, "pt"):
            return np.array([[float(p.pt[0]), float(p.pt[1])] for p in points], dtype=np.float64)
        if isinstance(first, (list, tuple, np.ndarray)) and len(first) == 2:
            return np.array([[float(p[0]), float(p[1])] for p in points], dtype=np.float64)

    raise TypeError(f"Unsupported points type: {type(points)}")


def compute_grid_indices(
    points: np.ndarray,
    image_shape: Tuple[int, int],
    grid: Tuple[int, int] = (4, 4),
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Maps 2D (x, y) points into 2D grid cell indices (row_idx, col_idx).

    Parameters:
    -----------
    points : np.ndarray
        Array of (x, y) coordinates with shape (N, 2).
    image_shape : Tuple[int, int]
        (height, width) of the reference image.
    grid : Tuple[int, int]
        (rows, cols) defining grid division, default (4, 4).

    Returns:
    --------
    row_indices : np.ndarray of int
        Row index in [0, rows - 1] for each point.
    col_indices : np.ndarray of int
        Column index in [0, cols - 1] for each point.
    """
    pts = _to_numpy_points(points)
    if pts.shape[0] == 0:
        return np.empty((0,), dtype=np.int64), np.empty((0,), dtype=np.int64)

    height, width = image_shape
    if height <= 0 or width <= 0:
        raise ValueError(f"Invalid image_shape: {image_shape}. Dimensions must be > 0.")

    rows, cols = grid
    if rows <= 0 or cols <= 0:
        raise ValueError(f"Invalid grid: {grid}. Grid rows and cols must be > 0.")

    x_coords = pts[:, 0]
    y_coords = pts[:, 1]

    cell_w = width / float(cols)
    cell_h = height / float(rows)

    # Compute cell column and row with boundary clamping
    col_idx = np.floor(x_coords / cell_w).astype(np.int64)
    row_idx = np.floor(y_coords / cell_h).astype(np.int64)

    col_idx = np.clip(col_idx, 0, cols - 1)
    row_idx = np.clip(row_idx, 0, rows - 1)

    return row_idx, col_idx


def compute_spatial_coverage(
    points: Any,
    image_shape: Tuple[int, int],
    grid: Tuple[int, int] = (4, 4),
) -> Dict[str, Any]:
    """
    Computes spatial distribution metrics for a set of points across an image.

    Parameters:
    -----------
    points : Any
        Keypoints or coordinates (N, 2) on the image.
    image_shape : Tuple[int, int]
        (height, width) of the image space.
    grid : Tuple[int, int]
        (rows, cols) grid resolution, default (4, 4).

    Returns:
    --------
    metrics : Dict[str, Any]
        - total_points (int): count of points
        - total_cells (int): rows * cols
        - occupied_cells (int): number of cells with at least 1 point
        - coverage_ratio (float): occupied_cells / total_cells in [0.0, 1.0]
        - grid_occupancy (np.ndarray): (rows, cols) count of points per cell
        - distribution_entropy (float): normalized entropy of point distribution [0.0, 1.0]
        - bounding_box_ratio (float): bounding box area / image area [0.0, 1.0]
        - is_well_distributed (bool): True if coverage_ratio >= 0.5 and total_points >= 4
    """
    pts = _to_numpy_points(points)
    rows, cols = grid
    total_cells = rows * cols
    height, width = image_shape

    if pts.shape[0] == 0:
        return {
            "total_points": 0,
            "total_cells": total_cells,
            "occupied_cells": 0,
            "coverage_ratio": 0.0,
            "grid_occupancy": np.zeros((rows, cols), dtype=np.int64),
            "distribution_entropy": 0.0,
            "bounding_box_ratio": 0.0,
            "is_well_distributed": False,
        }

    row_indices, col_indices = compute_grid_indices(pts, image_shape, grid)

    # Calculate grid counts
    grid_occupancy = np.zeros((rows, cols), dtype=np.int64)
    for r, c in zip(row_indices, col_indices):
        grid_occupancy[r, c] += 1

    occupied_cells = int(np.count_nonzero(grid_occupancy))
    coverage_ratio = float(occupied_cells / float(total_cells))

    # Normalized Shannon Entropy across all cells
    total_pts = float(pts.shape[0])
    probabilities = grid_occupancy.flatten() / total_pts
    # Filter positive probabilities
    pos_probs = probabilities[probabilities > 0]
    if len(pos_probs) > 1 and total_cells > 1:
        entropy = -np.sum(pos_probs * np.log2(pos_probs))
        max_entropy = np.log2(total_cells)
        distribution_entropy = float(np.clip(entropy / max_entropy, 0.0, 1.0))
    elif len(pos_probs) == 1:
        distribution_entropy = 0.0
    else:
        distribution_entropy = 0.0

    # Bounding box coverage
    min_x, max_x = np.min(pts[:, 0]), np.max(pts[:, 0])
    min_y, max_y = np.min(pts[:, 1]), np.max(pts[:, 1])
    bbox_w = max(0.0, max_x - min_x)
    bbox_h = max(0.0, max_y - min_y)
    bbox_area = bbox_w * bbox_h
    image_area = float(width * height)
    bbox_ratio = float(np.clip(bbox_area / image_area, 0.0, 1.0)) if image_area > 0 else 0.0

    is_well_distributed = bool(coverage_ratio >= 0.50 and pts.shape[0] >= 4)

    return {
        "total_points": int(pts.shape[0]),
        "total_cells": int(total_cells),
        "occupied_cells": int(occupied_cells),
        "coverage_ratio": float(coverage_ratio),
        "grid_occupancy": grid_occupancy,
        "distribution_entropy": float(distribution_entropy),
        "bounding_box_ratio": float(bbox_ratio),
        "is_well_distributed": is_well_distributed,
    }


def anms_spatial_balance(
    points_ref: Any,
    points_mov: Optional[Any] = None,
    target_count: int = 100,
    c_robust: float = 0.9,
    scores: Optional[Union[np.ndarray, List[float]]] = None,
) -> Dict[str, Any]:
    """
    Adaptive Non-Maximal Suppression (ANMS) for continuous, radius-optimal spatial distribution.
    Computes suppression radius r_i = min_j ||p_i - p_j|| subject to score_j > c_robust * score_i.
    Points with the largest suppression radius represent the most distinct, uniformly spaced keypoints.

    Parameters:
    -----------
    points_ref : Any
        (N, 2) reference points.
    points_mov : Optional[Any]
        (N, 2) moving points.
    target_count : int
        Desired number of well-distributed points to retain.
    c_robust : float
        Robustness coefficient (default 0.9).
    scores : Optional[Union[np.ndarray, List[float]]]
        Point response strengths (higher is better).

    Returns:
    --------
    result : Dict[str, Any]
        Selected indices, balanced points, and radii.
    """
    pts_ref = _to_numpy_points(points_ref)
    n_pts = pts_ref.shape[0]

    has_mov = points_mov is not None
    pts_mov = _to_numpy_points(points_mov) if has_mov else None

    if n_pts == 0:
        return {
            "selected_indices": np.empty((0,), dtype=np.int64),
            "selected_mask": np.zeros((0,), dtype=bool),
            "balanced_pts_ref": np.empty((0, 2), dtype=np.float64),
            "balanced_pts_mov": np.empty((0, 2), dtype=np.float64) if has_mov else None,
            "num_before": 0,
            "num_after": 0,
            "suppression_radii": np.empty((0,), dtype=np.float64),
        }

    if n_pts <= target_count:
        all_idx = np.arange(n_pts, dtype=np.int64)
        return {
            "selected_indices": all_idx,
            "selected_mask": np.ones(n_pts, dtype=bool),
            "balanced_pts_ref": pts_ref,
            "balanced_pts_mov": pts_mov,
            "num_before": int(n_pts),
            "num_after": int(n_pts),
            "suppression_radii": np.full(n_pts, np.inf, dtype=np.float64),
        }

    if scores is not None:
        strength = np.asarray(scores, dtype=np.float64).flatten()
    else:
        # Default equal response strength
        strength = np.ones(n_pts, dtype=np.float64)

    # Sort descending by strength
    order = np.argsort(-strength)
    sorted_pts = pts_ref[order]
    sorted_strength = strength[order]

    # Compute suppression radius for each point
    radii = np.full(n_pts, np.inf, dtype=np.float64)

    # Vectorized pairwise distance calculation for efficient ANMS
    for i in range(1, n_pts):
        # Candidates that have significantly higher strength: strength[j] > c_robust * strength[i]
        stronger_mask = sorted_strength[:i] > (c_robust * sorted_strength[i])
        if np.any(stronger_mask):
            stronger_pts = sorted_pts[:i][stronger_mask]
            dists = np.sqrt(np.sum((stronger_pts - sorted_pts[i]) ** 2, axis=1))
            radii[i] = np.min(dists)

    # Select top target_count points with highest suppression radii
    top_radii_order = np.argsort(-radii)[:target_count]
    selected_sorted_indices = order[top_radii_order]
    selected_indices = np.sort(selected_sorted_indices)

    selected_mask = np.zeros(n_pts, dtype=bool)
    selected_mask[selected_indices] = True

    return {
        "selected_indices": selected_indices,
        "selected_mask": selected_mask,
        "balanced_pts_ref": pts_ref[selected_indices],
        "balanced_pts_mov": pts_mov[selected_indices] if (has_mov and pts_mov is not None) else None,
        "num_before": int(n_pts),
        "num_after": int(len(selected_indices)),
        "suppression_radii": radii[top_radii_order],
    }


def spatially_balance(
    points_ref: Any,
    points_mov: Optional[Any] = None,
    image_shape: Optional[Tuple[int, int]] = None,
    grid: Tuple[int, int] = (4, 4),
    max_per_cell: int = 10,
    scores: Optional[Union[np.ndarray, List[float]]] = None,
    score_order: str = "ascending",
    method: str = "grid",
    target_count: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Spatially balances correspondences across the lunar image coordinate space.
    Supports:
    - 'grid': Uniform cell capping (default SIH baseline).
    - 'anms': Adaptive Non-Maximal Suppression (advanced continuous spread).

    Parameters:
    -----------
    points_ref : Any
        Reference image points (N, 2) or keypoints.
    points_mov : Optional[Any]
        Moving image points (N, 2) or keypoints matching points_ref.
    image_shape : Optional[Tuple[int, int]]
        (height, width) of the reference image.
    grid : Tuple[int, int]
        (rows, cols) grid resolution, default (4, 4).
    max_per_cell : int
        Maximum points to keep per cell in 'grid' method.
    scores : Optional[Union[np.ndarray, List[float]]]
        Quality scores (descriptor distance or Lowe ratio or response).
    score_order : str
        'ascending' (lower score is better) or 'descending' (higher is better).
    method : str
        'grid' or 'anms'.
    target_count : Optional[int]
        Target count when method='anms' (defaults to rows * cols * max_per_cell).

    Returns:
    --------
    result : Dict[str, Any]
        Dictionary with selected indices, balanced coordinates, and coverage before/after.
    """
    pts_ref = _to_numpy_points(points_ref)
    n_pts = pts_ref.shape[0]

    has_mov = points_mov is not None
    pts_mov = _to_numpy_points(points_mov) if has_mov else None

    if has_mov and pts_mov is not None and pts_mov.shape[0] != n_pts:
        raise ValueError(
            f"Point count mismatch: points_ref has {n_pts} points, points_mov has {pts_mov.shape[0]}"
        )

    rows, cols = grid

    # Handle empty case
    if n_pts == 0:
        empty_mask = np.zeros((0,), dtype=bool)
        empty_indices = np.empty((0,), dtype=np.int64)
        empty_occ = np.zeros((rows, cols), dtype=np.int64)
        return {
            "selected_indices": empty_indices,
            "selected_mask": empty_mask,
            "balanced_pts_ref": np.empty((0, 2), dtype=np.float64),
            "balanced_pts_mov": np.empty((0, 2), dtype=np.float64) if has_mov else None,
            "num_before": 0,
            "num_after": 0,
            "coverage_before": 0.0,
            "coverage_after": 0.0,
            "grid_occupancy_before": empty_occ,
            "grid_occupancy_after": empty_occ,
            "reduction_ratio": 0.0,
            "method": method,
        }

    # Infer image_shape if not provided
    if image_shape is None:
        max_x = max(1.0, float(np.max(pts_ref[:, 0])) * 1.05)
        max_y = max(1.0, float(np.max(pts_ref[:, 1])) * 1.05)
        image_shape = (int(np.ceil(max_y)), int(np.ceil(max_x)))

    cov_before_stats = compute_spatial_coverage(pts_ref, image_shape, grid)
    cov_before = cov_before_stats["coverage_ratio"]
    occ_before = cov_before_stats["grid_occupancy"]

    if method.lower() == "anms":
        k_target = target_count if target_count is not None else (rows * cols * max_per_cell)
        anms_res = anms_spatial_balance(
            points_ref=pts_ref,
            points_mov=pts_mov,
            target_count=k_target,
            scores=scores if score_order == "descending" else None,
        )
        selected_indices = anms_res["selected_indices"]
        selected_mask = anms_res["selected_mask"]
        balanced_pts_ref = anms_res["balanced_pts_ref"]
        balanced_pts_mov = anms_res["balanced_pts_mov"]

    else:
        # Standard Grid-Based Balancing (Default)
        if max_per_cell <= 0:
            raise ValueError(f"max_per_cell must be >= 1, got {max_per_cell}")

        row_indices, col_indices = compute_grid_indices(pts_ref, image_shape, grid)

        if scores is not None:
            scores_arr = np.asarray(scores, dtype=np.float64).flatten()
            if scores_arr.shape[0] != n_pts:
                raise ValueError(f"scores length ({scores_arr.shape[0]}) must match points ({n_pts})")
        else:
            scores_arr = np.arange(n_pts, dtype=np.float64)
            score_order = "ascending"

        cell_bins: Dict[Tuple[int, int], List[int]] = {}
        for idx, (r, c) in enumerate(zip(row_indices, col_indices)):
            cell_key = (int(r), int(c))
            if cell_key not in cell_bins:
                cell_bins[cell_key] = []
            cell_bins[cell_key].append(idx)

        selected_indices_list: List[int] = []
        for cell_key, indices in cell_bins.items():
            if len(indices) <= max_per_cell:
                selected_indices_list.extend(indices)
            else:
                cell_scores = scores_arr[indices]
                if score_order.lower() == "descending":
                    sorted_rel_order = np.argsort(-cell_scores)
                else:
                    sorted_rel_order = np.argsort(cell_scores)

                retained_for_cell = [indices[i] for i in sorted_rel_order[:max_per_cell]]
                selected_indices_list.extend(retained_for_cell)

        selected_indices = np.array(sorted(selected_indices_list), dtype=np.int64)
        selected_mask = np.zeros(n_pts, dtype=bool)
        selected_mask[selected_indices] = True
        balanced_pts_ref = pts_ref[selected_indices]
        balanced_pts_mov = pts_mov[selected_indices] if (has_mov and pts_mov is not None) else None

    # Compute coverage after balancing
    cov_after_stats = compute_spatial_coverage(balanced_pts_ref, image_shape, grid)
    cov_after = cov_after_stats["coverage_ratio"]
    occ_after = cov_after_stats["grid_occupancy"]

    reduction_ratio = float(len(selected_indices) / float(n_pts)) if n_pts > 0 else 0.0

    return {
        "selected_indices": selected_indices,
        "selected_mask": selected_mask,
        "balanced_pts_ref": balanced_pts_ref,
        "balanced_pts_mov": balanced_pts_mov,
        "num_before": int(n_pts),
        "num_after": int(len(selected_indices)),
        "coverage_before": float(cov_before),
        "coverage_after": float(cov_after),
        "grid_occupancy_before": occ_before,
        "grid_occupancy_after": occ_after,
        "reduction_ratio": float(reduction_ratio),
        "method": method,
    }


def get_grid_visualization_boxes(
    image_shape: Tuple[int, int],
    grid: Tuple[int, int] = (4, 4),
) -> List[Dict[str, Any]]:
    """
    Generates bounding box coordinates for each grid cell to facilitate UI overlay rendering.

    Returns:
    --------
    cells : List[Dict[str, Any]]
        List of dicts with:
        - row (int), col (int)
        - xmin (float), ymin (float), xmax (float), ymax (float)
    """
    height, width = image_shape
    rows, cols = grid
    cell_w = width / float(cols)
    cell_h = height / float(rows)

    boxes = []
    for r in range(rows):
        for c in range(cols):
            boxes.append(
                {
                    "row": r,
                    "col": c,
                    "xmin": float(c * cell_w),
                    "ymin": float(r * cell_h),
                    "xmax": float((c + 1) * cell_w),
                    "ymax": float((r + 1) * cell_h),
                }
            )
    return boxes
