from typing import List, Tuple, Optional
import numpy as np
from ..models.schemas import (
    MatchPairModel,
    RegistrationMetrics,
    RegistrationStatus,
    ConfidenceLevel,
    MetricMode,
    GeometricModel
)
from ..utils.logging import logger

class MetricsCalculator:
    """
    Computes rigorous quantitative metrics and transparent confidence ratings.
    Never uses hardcoded figures; all numbers are calculated from inliers and geometry.
    """

    @staticmethod
    def calculate_reprojection_rmse(
        inliers: List[MatchPairModel],
        matrix: Optional[np.ndarray],
        model_type: GeometricModel = GeometricModel.HOMOGRAPHY,
    ) -> Optional[float]:
        """
        Calculate Root Mean Square Error (RMSE) in pixels over all confirmed inliers.
        RMSE = sqrt( (1/M) * sum( || x_ref - T(x_mov) ||^2 ) )
        """
        if matrix is None or not inliers or len(inliers) == 0:
            return None

        try:
            pts_mov = np.float32([m.mov_pt for m in inliers]).reshape(-1, 1, 2)
            pts_ref = np.float32([m.ref_pt for m in inliers]).reshape(-1, 2)

            if model_type == GeometricModel.HOMOGRAPHY:
                pts_transformed = cv2_perspective_transform(pts_mov, matrix).reshape(-1, 2)
            else:
                pts_transformed = cv2_affine_transform(pts_mov, matrix).reshape(-1, 2)

            residuals = np.linalg.norm(pts_ref - pts_transformed, axis=1)
            rmse = float(np.sqrt(np.mean(residuals ** 2)))
            return round(rmse, 3)
        except Exception as e:
            logger.error(f"Error computing RMSE: {e}")
            return None

    @staticmethod
    def evaluate_registration(
        kps_ref_count: int,
        kps_mov_count: int,
        candidate_count: int,
        filtered_count: int,
        inliers: List[MatchPairModel],
        matrix: Optional[np.ndarray],
        spatial_coverage_before: float,
        spatial_coverage_after: float,
        runtime_ms: float,
        is_matrix_stable: bool,
        matrix_msg: str,
        model_type: GeometricModel = GeometricModel.HOMOGRAPHY,
        metric_mode: MetricMode = MetricMode.MEASURED,
        simulation_seed: Optional[int] = None,
        force_fail_safe: bool = False,
        raw_inlier_count: Optional[int] = None,
    ) -> Tuple[RegistrationStatus, RegistrationMetrics, Optional[str]]:
        """
        Evaluate full quantitative metrics and apply fail-safe criteria.
        Returns:
            status: RegistrationStatus (SUCCESSFUL, LOW_CONFIDENCE, NOT_RELIABLE, FAILED)
            metrics: RegistrationMetrics with full data and explanation
            failure_reason: String reason if NOT_RELIABLE or FAILED
        """
        inlier_count = raw_inlier_count if raw_inlier_count is not None else len(inliers)
        inlier_ratio = (inlier_count / filtered_count * 100.0) if filtered_count > 0 else 0.0
        inlier_ratio = round(inlier_ratio, 2)
        spatial_coverage = round(spatial_coverage_after, 2)

        rmse = MetricsCalculator.calculate_reprojection_rmse(inliers, matrix, model_type)

        # Fail-safe condition checks
        rejection_reasons = []
        if force_fail_safe:
            rejection_reasons.append("Manual fail-safe verification trigger active")
        if matrix is None:
            rejection_reasons.append("Geometric transformation matrix could not be computed")
        elif not is_matrix_stable:
            rejection_reasons.append(f"Transformation matrix instability: {matrix_msg}")
        if inlier_count < 8:
            rejection_reasons.append(f"Insufficient RANSAC inliers ({inlier_count} < 8 minimum threshold)")
        if inlier_ratio < 10.0:
            rejection_reasons.append(f"Inlier ratio too low ({inlier_ratio}% < 10% minimum threshold)")
        if spatial_coverage < 15.0:
            rejection_reasons.append(f"Poor spatial distribution (coverage {spatial_coverage}% < 15% threshold)")
        if rmse is not None and rmse > 10.0:
            rejection_reasons.append(f"Excessive reprojection error (RMSE {rmse}px > 10.0px)")

        # Determine status & confidence
        if rejection_reasons:
            status = RegistrationStatus.NOT_RELIABLE
            confidence_level = ConfidenceLevel.REJECTED
            confidence_score = 0.0
            explanation = "REGISTRATION NOT RELIABLE: " + "; ".join(rejection_reasons)
            rmse_reported = None  # Report N/A when rejected per guidelines
            failure_reason = "; ".join(rejection_reasons)
        else:
            # Score computation based on inliers, ratio, coverage, RMSE
            c_inliers = min(1.0, inlier_count / 50.0)
            c_ratio = min(1.0, inlier_ratio / 50.0)
            c_cov = min(1.0, spatial_coverage / 60.0)
            c_rmse = max(0.0, 1.0 - (rmse / 5.0)) if rmse is not None else 0.5
            
            # Weighted confidence score (quality index)
            confidence_score = round(0.35 * c_inliers + 0.25 * c_ratio + 0.25 * c_cov + 0.15 * c_rmse, 3)

            if confidence_score >= 0.70 and inlier_count >= 25 and (rmse is None or rmse <= 3.5):
                status = RegistrationStatus.SUCCESSFUL
                confidence_level = ConfidenceLevel.HIGH
                explanation = "High-confidence registration with strong spatial distribution and tight reprojection error."
            elif confidence_score >= 0.45 and inlier_count >= 14:
                status = RegistrationStatus.SUCCESSFUL
                confidence_level = ConfidenceLevel.MEDIUM
                explanation = "Acceptable registration alignment meeting baseline operational bounds."
            else:
                status = RegistrationStatus.LOW_CONFIDENCE
                confidence_level = ConfidenceLevel.LOW
                explanation = "Marginal alignment quality; recommended for manual visual review before critical use."
            
            rmse_reported = rmse
            failure_reason = None

        metrics = RegistrationMetrics(
            metric_mode=metric_mode,
            simulation_seed=simulation_seed,
            keypoints_reference=kps_ref_count,
            keypoints_moving=kps_mov_count,
            candidate_matches=candidate_count,
            filtered_matches=filtered_count,
            ransac_inliers=inlier_count,
            inlier_ratio=inlier_ratio,
            spatial_coverage=spatial_coverage,
            spatial_coverage_before=round(spatial_coverage_before, 2),
            rmse_px=rmse_reported,
            runtime_ms=round(runtime_ms, 1),
            confidence_level=confidence_level,
            confidence_score=confidence_score,
            confidence_explanation=explanation,
        )

        return status, metrics, failure_reason

def cv2_perspective_transform(pts: np.ndarray, H: np.ndarray) -> np.ndarray:
    """Apply 3x3 homography to array of 2D points (N, 1, 2)."""
    import cv2
    return cv2.perspectiveTransform(pts, H)

def cv2_affine_transform(pts: np.ndarray, M: np.ndarray) -> np.ndarray:
    """Apply 2x3 affine matrix to array of 2D points (N, 1, 2)."""
    import cv2
    # cv2.transform accepts 2x3 matrix
    return cv2.transform(pts, M)
