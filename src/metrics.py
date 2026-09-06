"""
LunarMatch — Quantitative Metrics & Evaluation Module
SIH 2026 Problem Statement 26166

This module calculates real, non-fabricated quantitative evaluation metrics:
1. Reprojection Error & RMSE (Root Mean Square Error)
2. Inlier Counts, Ratios, and Filter Retentions
3. Spatial Coverage & Uniformity Integration
4. Composite Registration Confidence & Fail-Safe Diagnostic Reason Generation
5. Formatted Metric Summaries for UI and Logging
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

from src.spatial import _to_numpy_points, compute_spatial_coverage


def transform_points(
    points: Any,
    transform_matrix: np.ndarray,
    model_type: str = "homography",
) -> np.ndarray:
    """
    Applies a 2D geometric transformation matrix (Homography or Affine) to points.

    Parameters:
    -----------
    points : Any
        Array of (x, y) coordinates with shape (N, 2).
    transform_matrix : np.ndarray
        3x3 matrix for homography/affine or 2x3 matrix for affine.
    model_type : str
        'homography' or 'affine'.

    Returns:
    --------
    transformed_points : np.ndarray
        Array of transformed (x, y) coordinates with shape (N, 2).
    """
    pts = _to_numpy_points(points)
    if pts.shape[0] == 0:
        return np.empty((0, 2), dtype=np.float64)

    H = np.asarray(transform_matrix, dtype=np.float64)
    n_pts = pts.shape[0]

    # Convert to homogeneous coordinates: (N, 3) -> [x, y, 1]
    homogeneous_pts = np.hstack([pts, np.ones((n_pts, 1), dtype=np.float64)])

    if model_type.lower() in ("affine", "similarity", "rigid"):
        if H.shape == (2, 3):
            # 2x3 Affine
            transformed = (H @ homogeneous_pts.T).T
            return transformed
        elif H.shape == (3, 3):
            transformed = (H @ homogeneous_pts.T).T
            # Drop homogeneous coordinate
            return transformed[:, :2]
        else:
            raise ValueError(f"Expected 2x3 or 3x3 matrix for affine, got {H.shape}")

    elif model_type.lower() in ("homography", "perspective", "projective"):
        if H.shape != (3, 3):
            raise ValueError(f"Expected 3x3 matrix for homography, got {H.shape}")

        transformed_h = (H @ homogeneous_pts.T).T  # Shape (N, 3)
        w = transformed_h[:, 2:3]

        # Guard against division by zero / negative w
        w_safe = np.where(np.abs(w) < 1e-10, 1e-10, w)
        transformed_xy = transformed_h[:, :2] / w_safe
        return transformed_xy

    else:
        raise ValueError(f"Unsupported model_type: '{model_type}'. Use 'homography' or 'affine'.")


def compute_reprojection_errors(
    points_ref: Any,
    points_mov: Any,
    transform_matrix: Optional[np.ndarray],
    model_type: str = "homography",
) -> Dict[str, Any]:
    """
    Computes point-wise Euclidean reprojection errors and summary statistics:
    e_i = || p_ref,i - T(p_mov,i) ||_2

    Parameters:
    -----------
    points_ref : Any
        Ground-truth or matched points in reference coordinates (N, 2).
    points_mov : Any
        Moving image points before transformation (N, 2).
    transform_matrix : Optional[np.ndarray]
        Transformation matrix mapping moving -> reference.
    model_type : str
        'homography' or 'affine'.

    Returns:
    --------
    stats : Dict[str, Any]
        - rmse (Optional[float]): Root Mean Square Error in pixels
        - mae (Optional[float]): Mean Absolute Error / Mean Reprojection Error in pixels
        - median_error (Optional[float]): Median error in pixels
        - max_error (Optional[float]): Maximum single-point error in pixels
        - std_error (Optional[float]): Standard deviation of error
        - point_errors (np.ndarray): (N,) per-point Euclidean distance errors
    """
    pts_ref = _to_numpy_points(points_ref)
    pts_mov = _to_numpy_points(points_mov)

    if pts_ref.shape[0] != pts_mov.shape[0]:
        raise ValueError(
            f"Point count mismatch: points_ref has {pts_ref.shape[0]}, points_mov has {pts_mov.shape[0]}"
        )

    n_pts = pts_ref.shape[0]
    if n_pts == 0 or transform_matrix is None:
        return {
            "rmse": None,
            "mae": None,
            "median_error": None,
            "max_error": None,
            "std_error": None,
            "point_errors": np.empty((0,), dtype=np.float64),
        }

    if not np.all(np.isfinite(pts_ref)) or not np.all(np.isfinite(pts_mov)):
        raise ValueError("points_ref and points_mov must contain only finite values")

    pts_mov_projected = transform_points(pts_mov, transform_matrix, model_type=model_type)
    if not np.all(np.isfinite(pts_mov_projected)):
        raise ValueError("transform produced non-finite projected points")

    diffs = pts_ref - pts_mov_projected
    squared_errors = np.sum(diffs**2, axis=1)
    point_errors = np.sqrt(squared_errors)

    rmse = float(np.sqrt(np.mean(squared_errors)))
    mae = float(np.mean(point_errors))
    median_error = float(np.median(point_errors))
    max_error = float(np.max(point_errors))
    std_error = float(np.std(point_errors))

    return {
        "rmse": round(rmse, 4),
        "mae": round(mae, 4),
        "median_error": round(median_error, 4),
        "max_error": round(max_error, 4),
        "std_error": round(std_error, 4),
        "point_errors": point_errors,
    }


def assess_registration_confidence(
    num_inliers: int,
    inlier_ratio: float,
    spatial_coverage: float,
    rmse: Optional[float] = None,
) -> Tuple[float, str, List[str]]:
    """
    Calculates a multi-factor confidence score [0.0, 1.0], category status,
    and diagnostic feedback for registration quality.

    Parameters:
    -----------
    num_inliers : int
        Count of geometrically consistent matches from RANSAC.
    inlier_ratio : float
        inliers / filtered_matches in [0.0, 1.0].
    spatial_coverage : float
        occupied_grid_cells / total_grid_cells in [0.0, 1.0].
    rmse : Optional[float]
        Root mean square reprojection error in pixels.

    Returns:
    --------
    confidence_score : float
        Overall quality score [0.0, 1.0].
    status : str
        'RELIABLE', 'LOW_CONFIDENCE', or 'FAILED'.
    diagnostic_reasons : List[str]
        List of actionable warnings or failure causes.
    """
    diagnostics = []

    # 1. Inlier Count Score (0 to 30+ inliers)
    if num_inliers >= 30:
        inlier_score = 1.0
    elif num_inliers >= 15:
        inlier_score = 0.7 + 0.3 * ((num_inliers - 15) / 15.0)
    elif num_inliers >= 6:
        inlier_score = 0.3 + 0.4 * ((num_inliers - 6) / 9.0)
    else:
        inlier_score = 0.05 * num_inliers

    if num_inliers < 6:
        diagnostics.append(f"Critical: Insufficient inliers ({num_inliers} found, minimum 6 required).")
    elif num_inliers < 15:
        diagnostics.append(f"Warning: Low inlier count ({num_inliers} inliers). Registration may be sensitive.")

    # 2. Inlier Ratio Score (0.0 to 0.7)
    if inlier_ratio >= 0.50:
        ratio_score = 1.0
    elif inlier_ratio >= 0.30:
        ratio_score = 0.6 + 0.4 * ((inlier_ratio - 0.30) / 0.20)
    elif inlier_ratio >= 0.15:
        ratio_score = 0.3 + 0.3 * ((inlier_ratio - 0.15) / 0.15)
    else:
        ratio_score = max(0.0, inlier_ratio * 2.0)

    if inlier_ratio < 0.15:
        diagnostics.append(f"Warning: Poor inlier ratio ({inlier_ratio:.1%}). High false-match rate in initial matching.")

    # 3. Spatial Coverage Score (0.0 to 0.6+)
    if spatial_coverage >= 0.50:
        coverage_score = 1.0
    elif spatial_coverage >= 0.30:
        coverage_score = 0.6 + 0.4 * ((spatial_coverage - 0.30) / 0.20)
    else:
        coverage_score = max(0.0, spatial_coverage * 2.0)

    if spatial_coverage < 0.25:
        diagnostics.append(f"Warning: Low spatial coverage ({spatial_coverage:.1%}). Matches are heavily clustered.")

    # 4. RMSE Score
    if rmse is not None:
        if rmse <= 1.0:
            rmse_score = 1.0
        elif rmse <= 2.5:
            rmse_score = 0.8 + 0.2 * ((2.5 - rmse) / 1.5)
        elif rmse <= 5.0:
            rmse_score = 0.4 + 0.4 * ((5.0 - rmse) / 2.5)
        else:
            rmse_score = max(0.0, 0.4 - (rmse - 5.0) * 0.1)

        if rmse > 4.0:
            diagnostics.append(f"Warning: High reprojection error (RMSE = {rmse:.2f} px). Alignment may contain distortion.")
    else:
        rmse_score = 0.5  # Neutral if not computable

    # Weighted Composite Score
    # Weights: Inliers (0.35), Ratio (0.25), Spatial Coverage (0.20), RMSE (0.20)
    composite = (
        0.35 * inlier_score
        + 0.25 * ratio_score
        + 0.20 * coverage_score
        + 0.20 * rmse_score
    )
    confidence = float(np.clip(composite, 0.0, 1.0))

    # Classification
    if num_inliers < 4 or (num_inliers < 6 and inlier_ratio < 0.15):
        status = "FAILED"
    elif confidence >= 0.65 and num_inliers >= 12 and spatial_coverage >= 0.25:
        status = "RELIABLE"
    else:
        status = "LOW_CONFIDENCE"

    if not diagnostics:
        diagnostics.append("Registration is stable and well-distributed.")

    return round(confidence, 4), status, diagnostics


def calculate_metrics(
    num_keypoints_ref: int,
    num_keypoints_mov: int,
    num_candidate_matches: int,
    num_filtered_matches: int,
    num_inliers: int,
    spatial_coverage_before: float,
    spatial_coverage_after: float,
    rmse: Optional[float] = None,
    runtime_seconds: float = 0.0,
    mae: Optional[float] = None,
    median_error: Optional[float] = None,
    max_error: Optional[float] = None,
    model_type: str = "homography",
) -> Dict[str, Any]:
    """
    Computes a comprehensive metrics dictionary adhering strictly to
    SIH 2026 PS 26166 evaluation requirements without hardcoded numbers.

    Returns:
    --------
    metrics : Dict[str, Any]
        Standard evaluation dictionary for pipeline and UI consumption.
    """
    counts = {
        "num_keypoints_ref": num_keypoints_ref,
        "num_keypoints_mov": num_keypoints_mov,
        "num_candidate_matches": num_candidate_matches,
        "num_filtered_matches": num_filtered_matches,
        "num_inliers": num_inliers,
    }
    if any(int(value) != value or value < 0 for value in counts.values()):
        raise ValueError("match and keypoint counts must be non-negative integers")
    if num_filtered_matches > num_candidate_matches:
        raise ValueError("num_filtered_matches cannot exceed num_candidate_matches")
    if num_inliers > num_filtered_matches:
        raise ValueError("num_inliers cannot exceed num_filtered_matches")
    if not 0.0 <= spatial_coverage_before <= 1.0 or not 0.0 <= spatial_coverage_after <= 1.0:
        raise ValueError("spatial coverage values must be within [0, 1]")

    inlier_ratio = (
        float(num_inliers / float(num_filtered_matches))
        if num_filtered_matches > 0
        else 0.0
    )
    inlier_ratio = min(1.0, max(0.0, inlier_ratio))

    candidate_filter_retention = (
        float(num_filtered_matches / float(num_candidate_matches))
        if num_candidate_matches > 0
        else 0.0
    )

    confidence, status, diagnostics = assess_registration_confidence(
        num_inliers=num_inliers,
        inlier_ratio=inlier_ratio,
        spatial_coverage=spatial_coverage_after,
        rmse=rmse,
    )

    return {
        # Feature Extraction
        "num_keypoints_ref": int(num_keypoints_ref),
        "num_keypoints_mov": int(num_keypoints_mov),
        # Matching & Filtering
        "num_candidate_matches": int(num_candidate_matches),
        "num_filtered_matches": int(num_filtered_matches),
        "candidate_filter_retention": round(candidate_filter_retention, 4),
        # Geometric Verification (RANSAC)
        "num_inliers": int(num_inliers),
        "inlier_ratio": round(inlier_ratio, 4),
        "model_type": str(model_type),
        # Spatial Distribution
        "spatial_coverage_before": round(float(spatial_coverage_before), 4),
        "spatial_coverage_after": round(float(spatial_coverage_after), 4),
        # Reprojection Error / RMSE
        "rmse": rmse,
        "mae": mae,
        "median_error": median_error,
        "max_error": max_error,
        # Execution & Confidence
        "runtime_seconds": round(float(runtime_seconds), 4),
        "registration_confidence": confidence,
        "status": status,
        "diagnostics": diagnostics,
    }


def format_metrics_summary(metrics: Dict[str, Any]) -> str:
    """
    Formats the metrics dictionary into an aligned, human-readable terminal/log report.
    """
    rmse_str = f"{metrics['rmse']:.3f} px" if metrics.get("rmse") is not None else "N/A"
    inlier_ratio_str = f"{metrics.get('inlier_ratio', 0.0):.1%}"
    cov_str = f"{metrics.get('spatial_coverage_after', 0.0):.1%}"
    conf_str = f"{metrics.get('registration_confidence', 0.0):.1%}"

    lines = [
        "============================================================",
        "             LunarMatch Evaluation Summary                  ",
        "============================================================",
        f" Status:                  {metrics.get('status', 'UNKNOWN')}",
        f" Registration Confidence: {conf_str}",
        f" Total Execution Time:    {metrics.get('runtime_seconds', 0.0):.3f}s",
        "------------------------------------------------------------",
        f" Keypoints (Ref / Mov):   {metrics.get('num_keypoints_ref', 0)} / {metrics.get('num_keypoints_mov', 0)}",
        f" Candidate Matches:       {metrics.get('num_candidate_matches', 0)}",
        f" Filtered Matches:        {metrics.get('num_filtered_matches', 0)} ({metrics.get('candidate_filter_retention', 0.0):.1%} kept)",
        f" RANSAC Inliers:          {metrics.get('num_inliers', 0)} ({inlier_ratio_str} inlier ratio)",
        f" Spatial Coverage:        {cov_str} (Initial: {metrics.get('spatial_coverage_before', 0.0):.1%})",
        f" Reprojection RMSE:       {rmse_str}",
        "------------------------------------------------------------",
        " Diagnostic Feedback:",
    ]
    for diag in metrics.get("diagnostics", []):
        lines.append(f"  • {diag}")
    lines.append("============================================================")

    return "\n".join(lines)
