import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
import cv2

from ..config import settings
from ..models.requests import RobustnessExperimentRequest, PipelineRunRequest
from ..models.responses import (
    RobustnessExperimentResponse,
    RobustnessPointResult,
    RegistrationStatus
)
from ..simulation.scenario_generator import apply_controlled_variation
from ..services.image_service import image_service
from ..services.pipeline_service import pipeline_service
from ..utils.file_utils import save_json
from ..utils.logging import logger

class ExperimentService:
    """Orchestrates controlled robustness laboratory profiling over controlled variations."""

    def __init__(self):
        self.experiments_dir = settings.EXPERIMENTS_DIR

    def run_robustness_experiment(self, req: RobustnessExperimentRequest) -> RobustnessExperimentResponse:
        """Run parameter sweep over illumination, scale, rotation, or translation."""
        exp_id = f"exp_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        base_path = image_service.resolve_image_path(req.base_image_id)
        base_img = cv2.imread(str(base_path), cv2.IMREAD_GRAYSCALE)
        if base_img is None:
            raise ValueError(f"Could not load base image for experiment: {req.base_image_id}")

        steps = max(3, min(10, req.variation_steps))
        vals = np.linspace(req.min_val, req.max_val, steps)

        points: List[RobustnessPointResult] = []

        # Temp directory for controlled variants
        temp_dir = settings.DATA_DIR / "processed" / exp_id
        temp_dir.mkdir(parents=True, exist_ok=True)

        for i, val in enumerate(vals):
            val_float = round(float(val), 2)
            var_label = f"{val_float}"
            scale = 1.0
            rot = 0.0
            tx = 0.0
            bright = 0.0
            contrast = 1.0

            if req.experiment_type == "illumination":
                bright = val_float
                var_label = f"ΔB: {val_float:+.0f}"
            elif req.experiment_type == "scale":
                scale = max(0.5, 1.0 + (val_float / 100.0))
                var_label = f"Scale: {scale:.2f}x"
            elif req.experiment_type == "rotation":
                rot = val_float
                var_label = f"Rot: {val_float:+.1f}°"
            elif req.experiment_type == "translation":
                tx = val_float
                var_label = f"Tx: {val_float:+.0f}px"

            # Create controlled variant
            variant, _ = apply_controlled_variation(
                base_img,
                scale=scale,
                rotation_deg=rot,
                tx_px=tx,
                brightness_offset=bright,
                contrast_factor=contrast,
                seed=26166 + i,
            )
            variant_path = temp_dir / f"step_{i}.png"
            cv2.imwrite(str(variant_path), variant)

            # Formulate sub-pipeline request
            pipe_req = PipelineRunRequest(
                reference_image_id=str(base_path),
                moving_image_id=str(variant_path),
                feature_method=req.feature_method,
                matcher=req.matcher,
                ratio_threshold=req.ratio_threshold,
                geometric_model=req.geometric_model,
                spatial_balancing=req.spatial_balancing,
                grid_size=req.grid_size,
                simulation_mode=False,
            )

            try:
                res = pipeline_service.execute_pipeline(pipe_req)
                points.append(
                    RobustnessPointResult(
                        variation_value=val_float,
                        variation_label=var_label,
                        inliers=res.metrics.ransac_inliers,
                        inlier_ratio=res.metrics.inlier_ratio,
                        spatial_coverage=res.metrics.spatial_coverage,
                        rmse_px=res.metrics.rmse_px,
                        runtime_ms=res.metrics.runtime_ms,
                        status=res.status,
                    )
                )
            except Exception as e:
                logger.error(f"Experiment step {i} failed: {e}")
                points.append(
                    RobustnessPointResult(
                        variation_value=val_float,
                        variation_label=var_label,
                        inliers=0,
                        inlier_ratio=0.0,
                        spatial_coverage=0.0,
                        rmse_px=None,
                        runtime_ms=0.0,
                        status=RegistrationStatus.FAILED,
                    )
                )

        # Save experiment summary
        exp_record = {
            "experiment_id": exp_id,
            "timestamp": datetime.utcnow().isoformat(),
            "experiment_type": req.experiment_type,
            "base_image": str(base_path.name),
            "disclaimer": "Controlled robustness experiment — for algorithmic profiling only",
            "points": [p.model_dump() for p in points],
        }
        save_json(self.experiments_dir / "results" / f"{exp_id}.json", exp_record)

        return RobustnessExperimentResponse(
            experiment_id=exp_id,
            experiment_type=req.experiment_type,
            base_image_id=req.base_image_id,
            disclaimer="Controlled robustness experiment — for algorithmic profiling only",
            points=points,
            summary={
                "steps_completed": len(points),
                "peak_inliers": max((p.inliers for p in points), default=0),
                "avg_inlier_ratio": round(float(np.mean([p.inlier_ratio for p in points])), 2) if points else 0.0,
                "avg_spatial_coverage": round(float(np.mean([p.spatial_coverage for p in points])), 2) if points else 0.0,
            }
        )

experiment_service = ExperimentService()
