import math
from typing import Dict, Any, Tuple, List, Optional
import cv2
import numpy as np
from ..models.schemas import (
    SensorType,
    FeatureMethod,
    GeometricModel,
    RegistrationStatus,
    ConfidenceLevel,
    MetricMode,
    RegistrationMetrics,
    SpatialGridStats,
    MatchPairModel
)
from ..models.requests import PipelineRunRequest
from ..vision.spatial import SpatialBalancing
from ..vision.registration import ImageRegistration
from ..vision.metrics import MetricsCalculator
from ..utils.logging import logger

class DeterministicSimulator:
    """
    Deterministic simulation engine for advanced/future research algorithms.
    Fixed seed = 26166 ensures perfectly reproducible presentation execution.
    
    Logically models:
    - Cross-sensor domain gap (e.g. OHRC optical vs IIRS hyperspectral)
    - Radiometric degradation on correspondence count
    - Grid distribution and coverage calculation
    - Guaranteed reproducible metric outputs tagged with metric_mode="DEMO"
    """

    def __init__(self, seed: int = 26166):
        self.seed = seed

    def run_simulation(
        self,
        ref_img: np.ndarray,
        mov_img: np.ndarray,
        request: PipelineRunRequest,
    ) -> Tuple[
        RegistrationStatus,
        RegistrationMetrics,
        SpatialGridStats,
        List[MatchPairModel],
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
        Optional[str]
    ]:
        """
        Execute mathematically grounded deterministic simulation for research pipeline demonstration.
        """
        rng = np.random.RandomState(self.seed)
        h_ref, w_ref = ref_img.shape[:2]
        h_mov, w_mov = mov_img.shape[:2]

        # 1. Compute empirical radiometric difference between images
        mean_ref = float(np.mean(ref_img))
        mean_mov = float(np.mean(mov_img))
        illum_delta = abs(mean_ref - mean_mov) / 255.0  # 0.0 to 1.0

        # Sensor modality penalty
        is_multimodal = (request.reference_sensor != request.moving_sensor)
        modality_factor = 0.72 if is_multimodal else 1.0

        # Base keypoints
        base_kps_ref = int(1400 + rng.randint(-50, 150))
        base_kps_mov = int(1350 + rng.randint(-60, 120))

        # Matches scale down logically with illumination difference
        match_retention = max(0.15, (1.0 - 0.65 * illum_delta) * modality_factor)
        candidate_count = int(base_kps_ref * 0.22 * match_retention)
        filtered_count = int(candidate_count * (1.2 - request.ratio_threshold * 0.45))
        filtered_count = max(4, filtered_count)

        # Inliers derived logically
        inlier_rate = max(0.12, (0.75 - 0.35 * illum_delta) * modality_factor)
        inlier_count = int(filtered_count * inlier_rate)
        inlier_count = max(2, inlier_count)

        # Deterministically synthesize realistic correspondence point clouds
        # Centered around crater features with smooth spatial distribution
        pts_ref: List[List[float]] = []
        pts_mov: List[List[float]] = []
        matches: List[MatchPairModel] = []

        # Synthetic ground truth affine transformation
        angle_deg = 3.2
        scale = 1.02
        tx = 12.0
        ty = -8.0
        rad = math.radians(angle_deg)
        cos_a, sin_a = math.cos(rad) * scale, math.sin(rad) * scale
        center_x, center_y = w_ref / 2.0, h_ref / 2.0

        # Create matches distributed across quadrants
        num_synth = max(filtered_count, 40)
        for i in range(num_synth):
            # Deterministic pseudo-random point on reference image
            rx = rng.uniform(0.08 * w_ref, 0.92 * w_ref)
            ry = rng.uniform(0.08 * h_ref, 0.92 * h_ref)

            # Apply transform to get ideal moving point
            dx = rx - center_x
            dy = ry - center_y
            mx_ideal = center_x + (cos_a * dx - sin_a * dy) + tx
            my_ideal = center_y + (sin_a * dx + cos_a * dy) + ty

            # Add subtle jitter
            is_in = (i < inlier_count)
            jitter_scale = 1.2 if is_in else rng.uniform(15.0, 50.0)
            mx = mx_ideal + rng.normal(0, jitter_scale)
            my = my_ideal + rng.normal(0, jitter_scale)

            # Match model
            dist = float(rng.uniform(40.0, 110.0) if is_in else rng.uniform(120.0, 240.0))
            matches.append(
                MatchPairModel(
                    ref_idx=i,
                    mov_idx=i,
                    distance=round(dist, 2),
                    ref_pt=[round(rx, 2), round(ry, 2)],
                    mov_pt=[round(mx, 2), round(my, 2)],
                    is_inlier=is_in,
                    is_spatially_selected=False,
                )
            )

        # 2. Perform Spatial Balancing
        inliers_only = [m for m in matches if m.is_inlier]
        spatially_balanced, spatial_stats = SpatialBalancing.balance(
            inliers_only,
            w_ref,
            h_ref,
            grid_size=request.grid_size,
            max_per_cell=request.max_features_per_cell,
        )

        # 3. Form transformation matrix
        # 3x3 Homography representation
        H = np.array([
            [cos_a, -sin_a, center_x * (1 - cos_a) + center_y * sin_a + tx],
            [sin_a,  cos_a, center_y * (1 - cos_a) - center_x * sin_a + ty],
            [0.0,    0.0,   1.0],
        ], dtype=np.float32)

        # 4. Synthesize registered, overlay, difference image
        registered_img, overlay_img, difference_img = ImageRegistration.warp_and_render(
            ref_img,
            mov_img,
            H,
            model_type=GeometricModel.HOMOGRAPHY,
        )

        # 5. Evaluate Metrics & Fail-safe
        runtime_ms = 42.0 + rng.uniform(5.0, 15.0)
        status, metrics, failure_reason = MetricsCalculator.evaluate_registration(
            kps_ref_count=base_kps_ref,
            kps_mov_count=base_kps_mov,
            candidate_count=candidate_count,
            filtered_count=filtered_count,
            inliers=spatially_balanced if request.spatial_balancing else inliers_only,
            matrix=H,
            spatial_coverage_before=spatial_stats.coverage_percentage_before,
            spatial_coverage_after=spatial_stats.coverage_percentage_after,
            runtime_ms=runtime_ms,
            is_matrix_stable=True,
            matrix_msg="Deterministic simulation matrix is verified stable",
            model_type=request.geometric_model,
            metric_mode=MetricMode.DEMO,
            simulation_seed=self.seed,
            force_fail_safe=request.fail_safe_override,
        )

        logger.info(f"Demo pipeline completed [Seed {self.seed}] Status: {status.value}")
        return (
            status,
            metrics,
            spatial_stats,
            matches,
            registered_img,
            overlay_img,
            difference_img,
            H,
            failure_reason,
        )
