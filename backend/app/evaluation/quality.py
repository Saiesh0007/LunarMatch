from typing import Any, Optional, Sequence, Tuple

import cv2
import numpy as np


def _is_finite_float(value: Any) -> bool:
    """Return True only when value is a real, finite number (rejects None/inf/nan)."""
    if value is None:
        return False
    try:
        return bool(np.isfinite(float(value)))
    except (TypeError, ValueError):
        return False


ACCEPTANCE_CRITERIA = {
    "overlap_ratio": (">=", 0.10),
    "inlier_count": (">=", 30),
    "inlier_ratio": (">=", 0.15),
    "spatial_coverage": (">=", 0.40),
    "rmse_pixels": ("<=", 2.0),
    "homography_determinant": ("in_range", (0.5, 2.0)),
    "condition_number_H": ("<=", 1.0e6),
}

# Without a known scale (cross-resolution pair, no GSD) the determinant only has to describe a
# plausible similarity-like map: positive (no mirroring), bounded linear scale and anisotropy.
UNKNOWN_SCALE_RANGE = (0.02, 50.0)
MAX_ANISOTROPY = 3.0


def footprint_coverage(
    ref_points: Sequence[Sequence[float]],
    transform_matrix: Optional[np.ndarray],
    moving_shape: Tuple[int, int],
    reference_shape: Tuple[int, int],
    grid_size: int = 6,
) -> Optional[float]:
    """Fraction of reference grid cells inside the moving image's footprint that hold an inlier.

    A fine moving image registered into a coarser reference covers only part of the
    reference, so coverage of the whole reference grid is capped by the footprint
    rather than by how well the matches are spread. Returns None when the footprint
    cannot be computed (no matrix, or it covers no cell centre).
    """
    if transform_matrix is None or not len(ref_points):
        return None
    H = np.asarray(transform_matrix, dtype=np.float64)
    if H.shape == (2, 3):
        H = np.vstack([H, [0.0, 0.0, 1.0]])
    if H.shape != (3, 3) or not np.all(np.isfinite(H)):
        return None
    mh, mw = moving_shape[:2]
    rh, rw = reference_shape[:2]
    corners = np.float64([[0, 0], [mw - 1, 0], [mw - 1, mh - 1], [0, mh - 1]]).reshape(-1, 1, 2)
    poly = cv2.perspectiveTransform(corners, H).reshape(-1, 2).astype(np.float32)
    cw, ch = rw / grid_size, rh / grid_size
    footprint_cells = set()
    for r in range(grid_size):
        for c in range(grid_size):
            if cv2.pointPolygonTest(poly, ((c + 0.5) * cw, (r + 0.5) * ch), False) >= 0:
                footprint_cells.add((r, c))
    if not footprint_cells:
        return None
    occupied = {(min(grid_size - 1, max(0, int(y // ch))), min(grid_size - 1, max(0, int(x // cw))))
                for x, y in ref_points}
    return len(occupied & footprint_cells) / len(footprint_cells)


def evaluate_registration(
    overlap_ratio: float,
    inlier_count: int,
    inlier_ratio: float,
    spatial_coverage: float,
    rmse_pixels: float,
    transform_matrix: np.ndarray,
    expected_scale: Optional[float] = None,
) -> dict[str, Any]:
    """Evaluate registration against explicit acceptance thresholds.

    Args:
        overlap_ratio: Estimated footprint overlap fraction.
        inlier_count: Number of geometrically verified inliers.
        inlier_ratio: Inliers divided by candidate matches.
        spatial_coverage: Fraction of spatial grid covered by inliers.
        rmse_pixels: Reprojection RMSE in pixels.
        transform_matrix: Estimated affine or homography matrix.
        expected_scale: Expected moving->reference linear pixel scale (gsd_moving / gsd_reference).
            The determinant range is scaled by its square. None means the scale is unknown:
            the determinant must then be positive, imply a linear scale within
            UNKNOWN_SCALE_RANGE, and the linear part must not be more anisotropic than MAX_ANISOTROPY.
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
    criteria = dict(ACCEPTANCE_CRITERIA)
    if expected_scale is not None and _is_finite_float(expected_scale) and expected_scale > 0:
        low, high = criteria["homography_determinant"][1]
        criteria["homography_determinant"] = ("in_range", (low * expected_scale ** 2, high * expected_scale ** 2))
    else:
        low_s, high_s = UNKNOWN_SCALE_RANGE
        criteria["homography_determinant"] = ("in_range", (low_s ** 2, high_s ** 2))
    anisotropy = float("inf")
    if matrix.shape in ((3, 3), (2, 3)):
        sv = np.linalg.svd(matrix[:2, :2], compute_uv=False)
        anisotropy = float(sv[0] / sv[1]) if sv[1] > 0 else float("inf")

    checklist = {}
    failed = []
    for name, (operator, threshold) in criteria.items():
        value = values[name]
        if value is None or not _is_finite_float(value):
            passed = False
        elif name == "homography_determinant" and expected_scale is None and anisotropy > MAX_ANISOTROPY:
            value, passed = float(value), False
        else:
            value = float(value)
            if operator == ">=":
                passed = bool(value >= threshold)
            elif operator == "<=":
                passed = bool(value <= threshold)
            else:
                low, high = threshold
                passed = bool(low <= value <= high)
        checklist[name] = {"value": value, "threshold": threshold, "pass": passed}
        if name == "homography_determinant":
            checklist[name]["expected_scale"] = expected_scale
            checklist[name]["anisotropy"] = anisotropy
        if not passed:
            failed.append(name)
    decision = "ACCEPTED" if not failed else "REGISTRATION_NOT_RELIABLE"
    reason = "All registration quality criteria passed." if not failed else "Failed criteria: " + ", ".join(failed)
    return {"decision": decision, "checklist": checklist, "failed_criteria": failed, "reason": reason}
