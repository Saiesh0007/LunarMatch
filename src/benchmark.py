"""
LunarMatch — Controlled Benchmark & Evaluation Suite
SIH 2026 Problem Statement 26166 — Member 5 (Siddharth)

This module implements Phase 5 benchmarking:
1. Controlled transformation experiments (Illumination, Scale, Rotation, Translation).
2. Ground-truth transformation verification and error measurement.
3. Comparison between Raw Matches vs Grid Balancing vs ANMS Balancing.
4. Structured CSV/JSON export for SIH presentation evidence.
"""

import json
import os
import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from src.metrics import calculate_metrics, compute_reprojection_errors, transform_points
from src.spatial import compute_spatial_coverage, spatially_balance


def create_ground_truth_transform(
    rotation_deg: float = 0.0,
    scale: float = 1.0,
    translation: Tuple[float, float] = (0.0, 0.0),
    center: Tuple[float, float] = (200.0, 200.0),
) -> np.ndarray:
    """
    Creates an exact ground-truth 3x3 transformation matrix for controlled testing.

    Parameters:
    -----------
    rotation_deg : float
        Rotation in degrees around center.
    scale : float
        Uniform scale factor.
    translation : Tuple[float, float]
        (tx, ty) displacement in pixels.
    center : Tuple[float, float]
        (cx, cy) rotation center.

    Returns:
    --------
    H_gt : np.ndarray
        3x3 transformation matrix mapping moving -> reference.
    """
    rad = np.deg2rad(rotation_deg)
    cos_a = np.cos(rad)
    sin_a = np.sin(rad)
    cx, cy = center
    tx, ty = translation

    # T_center * T_trans * S * R * T_neg_center
    # Mapping point p in moving image to p_ref in reference image:
    # p_ref = S * R * (p - c) + c + t
    # In matrix form:
    H = np.array(
        [
            [scale * cos_a, -scale * sin_a, cx * (1.0 - scale * cos_a) + cy * scale * sin_a + tx],
            [scale * sin_a, scale * cos_a, cy * (1.0 - scale * cos_a) - cx * scale * sin_a + ty],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float64,
    )
    return H


def generate_synthetic_points_pair(
    num_points: int = 100,
    image_shape: Tuple[int, int] = (400, 400),
    transform_matrix: Optional[np.ndarray] = None,
    cluster_ratio: float = 0.7,
    noise_std: float = 0.5,
    seed: int = 42,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Generates realistic point distributions with lunar crater-like clustering
    and precise ground-truth correspondence coordinates.

    Parameters:
    -----------
    num_points : int
        Total point correspondences to generate.
    image_shape : Tuple[int, int]
        (height, width) of the image.
    transform_matrix : Optional[np.ndarray]
        Ground-truth transformation matrix (default: 15 deg rotation, 1.1x scale).
    cluster_ratio : float
        Fraction of points densely concentrated in one region (simulating a crater rim).
    noise_std : float
        Standard deviation of Gaussian coordinate measurement noise.

    Returns:
    --------
    pts_ref : np.ndarray (N, 2)
    pts_mov : np.ndarray (N, 2)
    H_gt : np.ndarray (3, 3)
    """
    rng = np.random.default_rng(seed)
    height, width = image_shape

    if transform_matrix is None:
        transform_matrix = create_ground_truth_transform(
            rotation_deg=10.0, scale=1.05, translation=(12.0, 8.0), center=(width / 2.0, height / 2.0)
        )

    n_clustered = int(num_points * cluster_ratio)
    n_spread = num_points - n_clustered

    # Clustered points around simulated crater (e.g. at [100, 100])
    crater_center = np.array([width * 0.25, height * 0.25])
    pts_cluster = crater_center + rng.normal(0.0, width * 0.06, size=(n_clustered, 2))

    # Spread points across entire image
    pts_spread = rng.uniform([width * 0.05, height * 0.05], [width * 0.95, height * 0.95], size=(n_spread, 2))

    pts_mov = np.vstack([pts_cluster, pts_spread])
    # Clamp inside bounds
    pts_mov[:, 0] = np.clip(pts_mov[:, 0], 5.0, width - 5.0)
    pts_mov[:, 1] = np.clip(pts_mov[:, 1], 5.0, height - 5.0)

    # Project to reference coordinate space with exact ground-truth H
    pts_ref_exact = transform_points(pts_mov, transform_matrix, model_type="homography")

    # Add realistic sensor localization noise
    noise = rng.normal(0.0, noise_std, size=pts_ref_exact.shape) if noise_std > 0 else 0.0
    pts_ref = pts_ref_exact + noise

    return pts_ref, pts_mov, transform_matrix


def run_benchmark_experiment(
    experiment_name: str,
    pts_ref: np.ndarray,
    pts_mov: np.ndarray,
    H_gt: np.ndarray,
    image_shape: Tuple[int, int] = (400, 400),
    grid: Tuple[int, int] = (4, 4),
    max_per_cell: int = 5,
) -> Dict[str, Any]:
    """
    Executes a controlled benchmark comparing:
    1. Raw (Unbalanced) Matches
    2. Grid Spatially Balanced Matches
    3. ANMS Spatially Balanced Matches

    Calculates exact RMSE against Ground Truth H_gt.
    """
    t_start = time.time()
    n_total = pts_ref.shape[0]

    # 1. Raw / Unbalanced Metrics
    raw_cov = compute_spatial_coverage(pts_ref, image_shape, grid)
    raw_errors = compute_reprojection_errors(pts_ref, pts_mov, H_gt, model_type="homography")

    # 2. Grid-Balanced
    grid_res = spatially_balance(
        points_ref=pts_ref,
        points_mov=pts_mov,
        image_shape=image_shape,
        grid=grid,
        max_per_cell=max_per_cell,
        method="grid",
    )
    grid_errors = compute_reprojection_errors(
        grid_res["balanced_pts_ref"], grid_res["balanced_pts_mov"], H_gt, model_type="homography"
    )

    # 3. ANMS-Balanced
    anms_res = spatially_balance(
        points_ref=pts_ref,
        points_mov=pts_mov,
        image_shape=image_shape,
        grid=grid,
        method="anms",
        target_count=grid["rows"] * grid["cols"] * max_per_cell if isinstance(grid, dict) else grid[0] * grid[1] * max_per_cell,
    )
    anms_errors = compute_reprojection_errors(
        anms_res["balanced_pts_ref"], anms_res["balanced_pts_mov"], H_gt, model_type="homography"
    )

    elapsed = time.time() - t_start

    return {
        "experiment_name": experiment_name,
        "total_points": int(n_total),
        "raw": {
            "num_points": int(n_total),
            "coverage_ratio": round(raw_cov["coverage_ratio"], 4),
            "distribution_entropy": round(raw_cov["distribution_entropy"], 4),
            "rmse_gt": raw_errors["rmse"],
        },
        "grid_balanced": {
            "num_points": int(grid_res["num_after"]),
            "coverage_ratio": round(grid_res["coverage_after"], 4),
            "reduction_ratio": round(grid_res["reduction_ratio"], 4),
            "rmse_gt": grid_errors["rmse"],
        },
        "anms_balanced": {
            "num_points": int(anms_res["num_after"]),
            "coverage_ratio": round(anms_res["coverage_after"], 4),
            "reduction_ratio": round(anms_res["reduction_ratio"], 4),
            "rmse_gt": anms_errors["rmse"],
        },
        "coverage_gain_grid": round(grid_res["coverage_after"] - raw_cov["coverage_ratio"], 4),
        "coverage_gain_anms": round(anms_res["coverage_after"] - raw_cov["coverage_ratio"], 4),
        "runtime_seconds": round(elapsed, 4),
    }


def run_full_robustness_benchmark_suite(
    image_shape: Tuple[int, int] = (400, 400),
    output_dir: Optional[str] = "outputs/metrics",
) -> Dict[str, Any]:
    """
    Runs the full SIH PS 26166 robustness test battery:
    - Pure Translation
    - Rotation (15 deg, 30 deg)
    - Scale (0.8x downscale, 1.25x upscale)
    - Combined Scale + Rotation + Translation
    - Severe Clustering (90% crater clustering)
    """
    experiments = []

    # 1. Pure Translation
    H_trans = create_ground_truth_transform(rotation_deg=0.0, scale=1.0, translation=(20.0, 15.0))
    p_ref, p_mov, _ = generate_synthetic_points_pair(120, image_shape, H_trans, cluster_ratio=0.6)
    res_trans = run_benchmark_experiment("Translation (+20, +15px)", p_ref, p_mov, H_trans, image_shape)
    experiments.append(res_trans)

    # 2. Rotation 15 deg
    H_rot15 = create_ground_truth_transform(rotation_deg=15.0, scale=1.0, translation=(5.0, 5.0))
    p_ref, p_mov, _ = generate_synthetic_points_pair(120, image_shape, H_rot15, cluster_ratio=0.7)
    res_rot15 = run_benchmark_experiment("Rotation (15 deg)", p_ref, p_mov, H_rot15, image_shape)
    experiments.append(res_rot15)

    # 3. Scale 1.25x
    H_scale = create_ground_truth_transform(rotation_deg=0.0, scale=1.25, translation=(0.0, 0.0))
    p_ref, p_mov, _ = generate_synthetic_points_pair(120, image_shape, H_scale, cluster_ratio=0.65)
    res_scale = run_benchmark_experiment("Scale (1.25x)", p_ref, p_mov, H_scale, image_shape)
    experiments.append(res_scale)

    # 4. Multimodal Geometric (Scale + Rotation + Translation)
    H_combo = create_ground_truth_transform(rotation_deg=25.0, scale=1.15, translation=(15.0, -10.0))
    p_ref, p_mov, _ = generate_synthetic_points_pair(150, image_shape, H_combo, cluster_ratio=0.75)
    res_combo = run_benchmark_experiment("Combined (25 deg, 1.15x, +15/-10px)", p_ref, p_mov, H_combo, image_shape)
    experiments.append(res_combo)

    # 5. Severe Crater Clustering (90% in one crater)
    H_clust = create_ground_truth_transform(rotation_deg=5.0, scale=1.0, translation=(0.0, 0.0))
    p_ref, p_mov, _ = generate_synthetic_points_pair(200, image_shape, H_clust, cluster_ratio=0.90)
    res_clust = run_benchmark_experiment("Severe Crater Clustering (90%)", p_ref, p_mov, H_clust, image_shape)
    experiments.append(res_clust)

    summary = {
        "suite_name": "LunarMatch SIH 2026 Robustness Benchmark",
        "total_experiments": len(experiments),
        "experiments": experiments,
        "average_grid_coverage_gain": round(
            float(np.mean([e["coverage_gain_grid"] for e in experiments])), 4
        ),
        "average_anms_coverage_gain": round(
            float(np.mean([e["coverage_gain_anms"] for e in experiments])), 4
        ),
    }

    # Save to file if output_dir specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        json_path = os.path.join(output_dir, "benchmark_results.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

    return summary
