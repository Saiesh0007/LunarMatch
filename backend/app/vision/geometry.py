from typing import List, Tuple, Optional
import cv2
import numpy as np
from ..models.schemas import GeometricModel, MatchPairModel
from ..utils.logging import logger

class GeometricVerification:
    """Robust transformation estimation using RANSAC for Affine and Homography models."""

    @staticmethod
    def estimate(
        matches: List[MatchPairModel],
        model_type: GeometricModel = GeometricModel.HOMOGRAPHY,
        ransac_threshold: float = 3.0,
    ) -> Tuple[Optional[np.ndarray], List[MatchPairModel], List[bool], bool, str]:
        """
        Estimate transformation mapping from Moving to Reference coordinates.
        Reference = fixed coordinate system, Moving = image that gets transformed.
        Returns:
            matrix: 3x3 Homography or 2x3 Affine (or None if failed)
            inliers: List of MatchPairModel flagged as inliers
            inlier_mask: boolean mask across input matches
            is_stable: boolean stability indicator
            diagnostic: technical message
        """
        min_required = 4 if model_type == GeometricModel.HOMOGRAPHY else 3
        if len(matches) < min_required:
            return None, [], [False] * len(matches), False, f"Insufficient matches: {len(matches)} < {min_required} required"

        pts_mov = np.float32([m.mov_pt for m in matches]).reshape(-1, 1, 2)
        pts_ref = np.float32([m.ref_pt for m in matches]).reshape(-1, 1, 2)

        matrix = None
        mask = None

        if model_type == GeometricModel.HOMOGRAPHY:
            matrix, mask = cv2.findHomography(
                pts_mov,
                pts_ref,
                method=cv2.RANSAC,
                ransacReprojThreshold=ransac_threshold,
                maxIters=2000,
                confidence=0.995,
            )
        else:
            matrix, mask = cv2.estimateAffine2D(
                pts_mov,
                pts_ref,
                method=cv2.RANSAC,
                ransacReprojThreshold=ransac_threshold,
                maxIters=2000,
                confidence=0.995,
            )

        if matrix is None or mask is None:
            return None, [], [False] * len(matches), False, "RANSAC convergence failed to find valid consensus set"

        inlier_mask = [bool(m[0]) for m in mask]
        inliers: List[MatchPairModel] = []
        for i, is_in in enumerate(inlier_mask):
            matches[i].is_inlier = is_in
            if is_in:
                inliers.append(matches[i])

        # Validate transformation matrix stability
        is_stable, stability_msg = GeometricVerification._check_matrix_stability(matrix, model_type)
        if not is_stable:
            logger.warning(f"Geometric matrix instability detected: {stability_msg}")

        logger.info(
            f"Geometric Verification ({model_type.value}): {len(inliers)} inliers / {len(matches)} "
            f"matches (threshold={ransac_threshold}px, stable={is_stable})"
        )
        return matrix, inliers, inlier_mask, is_stable, stability_msg

    @staticmethod
    def _check_matrix_stability(matrix: np.ndarray, model_type: GeometricModel) -> Tuple[bool, str]:
        """Check conditioning, scaling, and determinant to avoid singular or degenerate warps."""
        try:
            if model_type == GeometricModel.HOMOGRAPHY:
                # Normalizing H so H[2, 2] == 1
                if abs(matrix[2, 2]) < 1e-7:
                    return False, "Singular homography denominator (H[2,2] ~ 0)"
                H_norm = matrix / matrix[2, 2]
                det = np.linalg.det(H_norm[:2, :2])
                if det <= 0.05 or det > 20.0:
                    return False, f"Extreme perspective scaling or reflection (det={det:.3f})"
                cond = np.linalg.cond(H_norm)
                if cond > 1e5:
                    return False, f"Ill-conditioned homography matrix (condition number={cond:.1e})"
            else:
                det = np.linalg.det(matrix[:2, :2])
                if det <= 0.05 or det > 20.0:
                    return False, f"Degenerate affine determinant (det={det:.3f})"
            return True, "Transformation matrix is mathematically stable"
        except Exception as e:
            return False, f"Matrix stability check exception: {str(e)}"


def magsac_plus_plus(
    src_pts: np.ndarray,
    dst_pts: np.ndarray,
    model: str = "affine",
    sigma_max: float = 3.0,
    max_iters: int = 10000,
    confidence: float = 0.99,
    random_seed: int = 0,
) -> Tuple[Optional[np.ndarray], np.ndarray, dict]:
    """Estimate a geometric model with OpenCV's USAC MAGSAC backend.

    Args:
        src_pts: Source points with shape ``(N, 2)``.
        dst_pts: Destination points with shape ``(N, 2)``.
        model: ``affine``, ``homography``, or ``similarity``.
        sigma_max: Upper bound for the inlier noise scale in pixels.
        max_iters: Maximum robust-estimation iterations.
        confidence: Desired confidence for the robust estimator.
        random_seed: Seed for OpenCV's deterministic random sampler.
    Returns:
        Model parameters, boolean inlier mask, and MAGSAC diagnostics.
    Raises:
        ValueError: If inputs or estimator parameters are invalid.
    """
    src = np.asarray(src_pts, dtype=np.float32)
    dst = np.asarray(dst_pts, dtype=np.float32)
    if src.ndim != 2 or dst.ndim != 2 or src.shape != dst.shape or src.shape[1] != 2:
        raise ValueError("src_pts and dst_pts must both have shape (N, 2)")
    if sigma_max <= 0 or max_iters < 1 or not 0.0 < confidence < 1.0:
        raise ValueError("invalid MAGSAC parameters")
    model_name = model.value if hasattr(model, "value") else str(model).lower()
    minimum = 4 if model_name == "homography" else 3 if model_name in ("affine", "similarity") else 0
    if minimum == 0:
        raise ValueError(f"unsupported model: {model_name}")
    if len(src) < minimum:
        return None, np.zeros(len(src), dtype=bool), {"failure_reason": f"insufficient points: {len(src)} < {minimum}"}
    if not hasattr(cv2, "USAC_MAGSAC"):
        return None, np.zeros(len(src), dtype=bool), {"failure_reason": "OpenCV USAC_MAGSAC is unavailable"}

    cv2.setRNGSeed(int(random_seed))
    if model_name == "homography":
        params, raw_mask = cv2.findHomography(src, dst, method=cv2.USAC_MAGSAC, ransacReprojThreshold=float(sigma_max), maxIters=int(max_iters), confidence=float(confidence))
    elif model_name == "similarity":
        params, raw_mask = cv2.estimateAffinePartial2D(src, dst, method=cv2.USAC_MAGSAC, ransacReprojThreshold=float(sigma_max), maxIters=int(max_iters), confidence=float(confidence), refineIters=10)
    else:
        params, raw_mask = cv2.estimateAffine2D(src, dst, method=cv2.USAC_MAGSAC, ransacReprojThreshold=float(sigma_max), maxIters=int(max_iters), confidence=float(confidence), refineIters=10)
    if params is None or raw_mask is None:
        return None, np.zeros(len(src), dtype=bool), {"failure_reason": "USAC_MAGSAC failed to find a model", "backend": "opencv_usac_magsac"}

    mask = np.asarray(raw_mask, dtype=bool).reshape(-1)
    if model_name == "homography":
        homogeneous = np.column_stack((src, np.ones(len(src), dtype=np.float32)))
        projected = homogeneous @ params.T
        projected = projected[:, :2] / np.maximum(np.abs(projected[:, 2:3]), 1e-8)
    else:
        projected = cv2.transform(src.reshape(-1, 1, 2), params).reshape(-1, 2)
    residuals = np.linalg.norm(projected - dst, axis=1)
    inlier_residuals = residuals[mask]
    best_sigma = float(np.clip(np.median(inlier_residuals) / 0.6745 if len(inlier_residuals) else sigma_max, 1e-6, sigma_max))
    weights = np.exp(-0.5 * (residuals / best_sigma) ** 2).astype(np.float32)
    weighted_rms = float(np.sqrt(np.sum(weights * residuals ** 2) / max(np.sum(weights), 1e-6)))
    diagnostics = {
        "backend": "opencv_usac_magsac",
        "n_hypotheses_tried": int(max_iters),
        "best_sigma": best_sigma,
        "best_score": float(np.sum(weights)),
        "n_inliers_at_best_sigma": int(np.count_nonzero(mask)),
        "weighted_rms_px": weighted_rms,
        "weights": weights.tolist(),
        "residuals_px": residuals.tolist(),
    }
    return params, mask, diagnostics
