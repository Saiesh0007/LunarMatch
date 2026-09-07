from typing import List, Tuple, Dict, Any, Optional
import cv2
import numpy as np
from ..models.schemas import MatcherType, MatchPairModel
from ..utils.logging import logger

class FeatureMatcher:
    """Feature matching with BFMatcher and FLANN + Lowe's ratio test filter."""

    def __init__(self, matcher_type: MatcherType = MatcherType.BF, ratio_threshold: float = 0.75):
        self.matcher_type = matcher_type
        self.ratio_threshold = ratio_threshold

        if matcher_type == MatcherType.FLANN:
            index_params = dict(algorithm=1, trees=5)  # FLANN_INDEX_KDTREE = 1
            search_params = dict(checks=50)
            self.matcher = cv2.FlannBasedMatcher(index_params, search_params)
        else:
            self.matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)

    def match(
        self,
        kps_ref: List[cv2.KeyPoint],
        desc_ref: np.ndarray,
        kps_mov: List[cv2.KeyPoint],
        desc_mov: np.ndarray,
    ) -> Tuple[List[MatchPairModel], int]:
        """
        Execute 2-NN matching and Lowe's ratio filtering.
        Returns:
            filtered_matches: List of MatchPairModel passing ratio test
            candidate_count: Total raw candidate pairs found by 2-NN
        """
        if desc_ref is None or desc_mov is None or len(desc_ref) < 2 or len(desc_mov) < 2:
            logger.warning("Insufficient descriptors for matching")
            return [], 0

        # Ensure float32 for FLANN / SIFT L2
        desc1 = desc_ref.astype(np.float32)
        desc2 = desc_mov.astype(np.float32)

        raw_knn_matches = self.matcher.knnMatch(desc1, desc2, k=2)
        candidate_count = len(raw_knn_matches)

        filtered_matches: List[MatchPairModel] = []

        for match_pair in raw_knn_matches:
            if len(match_pair) < 2:
                continue
            m, n = match_pair[0], match_pair[1]
            if m.distance < self.ratio_threshold * n.distance:
                ref_pt = [float(kps_ref[m.queryIdx].pt[0]), float(kps_ref[m.queryIdx].pt[1])]
                mov_pt = [float(kps_mov[m.trainIdx].pt[0]), float(kps_mov[m.trainIdx].pt[1])]
                filtered_matches.append(
                    MatchPairModel(
                        ref_idx=int(m.queryIdx),
                        mov_idx=int(m.trainIdx),
                        distance=float(m.distance),
                        ref_pt=ref_pt,
                        mov_pt=mov_pt,
                        is_inlier=False,
                        is_spatially_selected=False,
                    )
                )

        logger.info(
            f"Matching ({self.matcher_type.value}): {candidate_count} candidates -> "
            f"{len(filtered_matches)} filtered (ratio={self.ratio_threshold})"
        )
        return filtered_matches, candidate_count
