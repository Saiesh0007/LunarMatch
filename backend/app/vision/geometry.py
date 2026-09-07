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
