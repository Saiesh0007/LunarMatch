from typing import Any

import numpy as np


ACCEPTANCE_CRITERIA = {
    "overlap_ratio": (">=", 0.10),
    "inlier_count": (">=", 30),
    "inlier_ratio": (">=", 0.15),
    "spatial_coverage": (">=", 0.40),
    "rmse_pixels": ("<=", 2.0),
    "homography_determinant": ("in_range", (0.5, 2.0)),
    "condition_number_H": ("<=", 1.0e6),
}


def evaluate_registration(
    overlap_ratio: float,
    inlier_count: int,
    inlier_ratio: float,
    spatial_coverage: float,
    rmse_pixels: float,
    transform_matrix: np.ndarray,
) -> dict[str, Any]:
    """Evaluate registration against explicit acceptance thresholds.

    Args:
        overlap_ratio: Estimated footprint overlap fraction.
        inlier_count: Number of geometrically verified inliers.
        inlier_ratio: Inliers divided by candidate matches.
        spatial_coverage: Fraction of spatial grid covered by inliers.
        rmse_pixels: Reprojection RMSE in pixels.
        transform_matrix: Estimated affine or homography matrix.
    Returns:
        Decision, per-criterion checklist, failed criteria, and explanation.
    Raises:
        None: Invalid or non-finite values fail their corresponding checks safely.
    """
    matrix = np.asarray(transform_matrix, dtype=np.float64) if transform_matrix is not None else np.empty((0, 0))
    determinant = float("nan")
    condition_number = float("inf")
    if matrix.shape == (3, 3):
        determinant = float(np.linalg.det(matrix[:2, :2]))
        condition_number = float(np.linalg.cond(matrix))
    elif matrix.shape == (2, 3):
        determinant = float(np.linalg.det(matrix[:, :2]))
        condition_number = float(np.linalg.cond(matrix[:, :2]))

    values = {
        "overlap_ratio": overlap_ratio,
        "inlier_count": inlier_count,
        "inlier_ratio": inlier_ratio,
        "spatial_coverage": spatial_coverage,
        "rmse_pixels": rmse_pixels,
        "homography_determinant": determinant,
        "condition_number_H": condition_number,
    }
    checklist = {}
    failed = []
    for name, (operator, threshold) in ACCEPTANCE_CRITERIA.items():
        value = float(values[name])
        if operator == ">=":
            passed = bool(np.isfinite(value) and value >= threshold)
        elif operator == "<=":
            passed = bool(np.isfinite(value) and value <= threshold)
        else:
            low, high = threshold
            passed = bool(np.isfinite(value) and low <= value <= high)
        checklist[name] = {"value": value, "threshold": threshold, "pass": passed}
        if not passed:
            failed.append(name)
    decision = "ACCEPTED" if not failed else "REGISTRATION_NOT_RELIABLE"
    reason = "All registration quality criteria passed." if not failed else "Failed criteria: " + ", ".join(failed)
    return {"decision": decision, "checklist": checklist, "failed_criteria": failed, "reason": reason}
