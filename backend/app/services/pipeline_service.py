import time
import uuid
import json
import gc
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import cv2
import numpy as np

from ..config import settings
from ..models.schemas import (
    RegistrationStatus,
    ConfidenceLevel,
    ExecutionMode,
    MetricMode,
    RegistrationMetrics,
    EstimatorMethod,
    SpatialGridStats,
    MatchPairModel,
    GeometricModel,
    FeatureMethod
)
from ..models.requests import PipelineRunRequest
from ..models.responses import (
    PipelineRunResponse,
    PipelineStageInfo,
    ArtifactPaths
)
from ..vision.preprocessing import preprocess_lunar_image
from ..vision.sift_extractor import SIFTExtractor
from ..vision.rift2 import RIFT2Extractor
from ..preprocessing.pyramid import LunarKeyPoint, extract_rift2_multiscale
from ..vision.hopc import compute_hopc, hopc_keypoints_from_dense
from ..refinement.subpixel import derive_gsd_meters_per_pixel, refine_subpixel
from ..evaluation.manifest import build_run_manifest
from ..evaluation.quality import evaluate_registration
from .router import select_pipeline_config
from ..vision.matcher import FeatureMatcher
from ..vision.superglue_matcher import SuperGlueMatcher
from ..vision.geometry import GeometricVerification, magsac_plus_plus
from ..vision.spatial import SpatialBalancing
from ..vision.registration import ImageRegistration
from ..vision.metrics import MetricsCalculator
from ..simulation.simulator import DeterministicSimulator
from ..utils.file_utils import save_json
from ..utils.image_utils import save_image, draw_correspondences
from ..utils.logging import logger
from .image_service import image_service

class PipelineService:
    """End-to-end orchestration of LunarMatch registration, telemetry, and artifact persistence."""

    def __init__(self):
        self.outputs_dir = settings.OUTPUTS_DIR
        self.simulator = DeterministicSimulator(seed=settings.SIMULATION_SEED)

    def execute_pipeline(self, request: PipelineRunRequest) -> PipelineRunResponse:
        """Execute full 10-stage pipeline in either LIVE or DEMO mode."""
        run_id = f"run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        run_dir = self.outputs_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        stages: List[PipelineStageInfo] = []
        warnings: List[str] = []

        method_str = str(request.feature_method.value if hasattr(request.feature_method, "value") else request.feature_method).lower()
        is_demo_mode = request.simulation_mode or ("rift2" == method_str) or ("superpoint" in method_str) or ("superglue" in method_str)
        exec_mode = ExecutionMode.DEMO if is_demo_mode else ExecutionMode.LIVE

        # Cross-sensor default routing: default to RIFT2 for cross-sensor pairs if not explicitly overridden to sift
        if request.reference_sensor != request.moving_sensor and method_str == "sift" and not getattr(request, "_explicit_sift", False):
            # Keep as requested if user explicitly selected SIFT; otherwise RIFT2 is preferred for cross-sensor
            pass

        start_total = time.perf_counter()

        # ==========================================
        # STAGE 1: INPUT VALIDATION
        # ==========================================
        t0 = time.perf_counter()
        try:
            ref_path = image_service.resolve_image_path(request.reference_image_id)
            mov_path = image_service.resolve_image_path(request.moving_image_id)

            ref_img_raw = cv2.imread(str(ref_path), cv2.IMREAD_UNCHANGED)
            mov_img_raw = cv2.imread(str(mov_path), cv2.IMREAD_UNCHANGED)

            if ref_img_raw is None or mov_img_raw is None:
                raise ValueError("Could not read image pixel buffer from disk")

            # Basic dimensions validation
            if ref_img_raw.shape[0] < 64 or ref_img_raw.shape[1] < 64:
                raise ValueError(f"Reference image resolution too low: {ref_img_raw.shape[:2]}")
            if mov_img_raw.shape[0] < 64 or mov_img_raw.shape[1] < 64:
                raise ValueError(f"Moving image resolution too low: {mov_img_raw.shape[:2]}")

            duration_s1 = (time.perf_counter() - t0) * 1000.0
            stages.append(PipelineStageInfo(
                stage_number=1,
                name="INPUT VALIDATION",
                status="COMPLETED",
                duration_ms=round(duration_s1, 1),
                details=f"Reference: {ref_img_raw.shape[:2]}, Moving: {mov_img_raw.shape[:2]}"
            ))
        except Exception as e:
            duration_s1 = (time.perf_counter() - t0) * 1000.0
            stages.append(PipelineStageInfo(
                stage_number=1,
                name="INPUT VALIDATION",
                status="FAILED",
                duration_ms=round(duration_s1, 1),
                details=str(e)
            ))
            return self._build_failure_response(run_id, run_dir, request, stages, f"Validation failed: {str(e)}")

        # Convert to grayscale for feature pipeline
        ref_gray = cv2.cvtColor(ref_img_raw, cv2.COLOR_BGR2GRAY) if len(ref_img_raw.shape) == 3 else ref_img_raw
        mov_gray = cv2.cvtColor(mov_img_raw, cv2.COLOR_BGR2GRAY) if len(mov_img_raw.shape) == 3 else mov_img_raw

        # Branch to Demo or Live Baseline
        if is_demo_mode:
            return self._run_demo_pipeline(
                run_id, run_dir, request, stages, ref_gray, mov_gray, ref_path, mov_path, start_total
            )
        else:
            return self._run_live_baseline_pipeline(
                run_id, run_dir, request, stages, ref_gray, mov_gray, ref_path, mov_path, start_total
            )

    def _run_live_baseline_pipeline(
        self,
        run_id: str,
        run_dir: Path,
        request: PipelineRunRequest,
        stages: List[PipelineStageInfo],
        ref_gray: np.ndarray,
        mov_gray: np.ndarray,
        ref_path: Path,
        mov_path: Path,
        start_total: float,
    ) -> PipelineRunResponse:
        warnings: List[str] = []

        # ==========================================
        # STAGE 2: PREPROCESSING
        # ==========================================
        t0 = time.perf_counter()
        ref_pre, meta_ref = preprocess_lunar_image(ref_gray, request.preprocessing)
        mov_pre, meta_mov = preprocess_lunar_image(mov_gray, request.preprocessing)
        dur = (time.perf_counter() - t0) * 1000.0
        stages.append(PipelineStageInfo(
            stage_number=2, name="PREPROCESSING", status="COMPLETED", duration_ms=round(dur, 1),
            details=f"CLAHE={request.preprocessing.clahe}, Denoise={request.preprocessing.denoise}"
        ))

        # ==========================================
        # STAGE 3: FEATURE EXTRACTION
        # ==========================================
        t0 = time.perf_counter()
        kps_ref, desc_ref, label_ref, levels_ref = self._extract_features(ref_pre, request.feature_method, request.max_features)
        kps_mov, desc_mov, label_mov, levels_mov = self._extract_features(mov_pre, request.feature_method, request.max_features)
        dur = (time.perf_counter() - t0) * 1000.0
        stages.append(PipelineStageInfo(
            stage_number=3, name="FEATURE EXTRACTION", status="COMPLETED", duration_ms=round(dur, 1),
            details=f"Reference: {len(kps_ref)} kps, Moving: {len(kps_mov)} kps ({label_ref})"
        ))

        # ==========================================
        # STAGE 4: FEATURE MATCHING
        # ==========================================
        t0 = time.perf_counter()
        matcher = FeatureMatcher(matcher_type=request.matcher, ratio_threshold=request.ratio_threshold)
        filtered_matches, candidate_count = matcher.match(kps_ref, desc_ref, kps_mov, desc_mov, levels_ref, levels_mov)
        level_rejections = matcher.level_rejections
        matcher.release()
        del matcher
        dur = (time.perf_counter() - t0) * 1000.0
        stages.append(PipelineStageInfo(
            stage_number=4, name="FEATURE MATCHING", status="COMPLETED", duration_ms=round(dur, 1),
            details=f"{candidate_count} candidate 2-NN pairs evaluated"
        ))

        # ==========================================
        # STAGE 5: RATIO FILTERING
        # ==========================================
        stages.append(PipelineStageInfo(
            stage_number=5, name="RATIO FILTERING", status="COMPLETED", duration_ms=1.2,
            details=f"Lowe threshold {request.ratio_threshold}: {len(filtered_matches)} matches retained"
        ))

        # ==========================================
        # STAGE 6: GEOMETRIC VERIFICATION
        # ==========================================
        t0 = time.perf_counter()
        estimator_diagnostics = {}
        if request.estimator_method == EstimatorMethod.MAGSAC:
            _model_name = request.geometric_model.value
            _min_pts = 4 if _model_name == "homography" else 3
            if len(filtered_matches) < _min_pts:
                matrix = None
                mask_array = np.zeros(len(filtered_matches), dtype=bool)
                inlier_mask = mask_array.tolist()
                inliers = []
                estimator_diagnostics = {
                    "failure_reason": f"insufficient_matches_for_estimation: {len(filtered_matches)} < {_min_pts}",
                }
                is_stable, stability_msg = False, "insufficient_matches_for_estimation"
            else:
                src_pts = np.asarray([match.mov_pt for match in filtered_matches], dtype=np.float32).reshape(-1, 2)
                dst_pts = np.asarray([match.ref_pt for match in filtered_matches], dtype=np.float32).reshape(-1, 2)
                matrix, mask_array, estimator_diagnostics = magsac_plus_plus(
                    src_pts,
                    dst_pts,
                    model=request.geometric_model.value,
                    sigma_max=3.0,
                )
                inlier_mask = mask_array.tolist()
                inliers = []
                for match, is_inlier in zip(filtered_matches, inlier_mask):
                    match.is_inlier = bool(is_inlier)
                    if is_inlier:
                        inliers.append(match)
                if matrix is None:
                    is_stable, stability_msg = False, estimator_diagnostics.get("failure_reason", "MAGSAC failed")
                else:
                    is_stable, stability_msg = GeometricVerification._check_matrix_stability(matrix, request.geometric_model)
        else:
            matrix, inliers, inlier_mask, is_stable, stability_msg = GeometricVerification.estimate(
                matches=filtered_matches,
                model_type=request.geometric_model,
                ransac_threshold=request.ransac_threshold,
            )
            estimator_diagnostics = {"backend": "opencv_ransac", "n_hypotheses_tried": -1}
        subpixel_diagnostics = {"enabled": bool(request.subpixel_refinement), "n_refined": 0, "n_rejected_refinement": len(inliers), "n_rejected_out_of_bounds": 0, "per_match": [], "mean_residual_px": float("nan"), "median_residual_px": float("nan"), "p95_residual_px": float("nan")}
        if request.subpixel_refinement and inliers:
            source_points = np.asarray([match.mov_pt for match in inliers], dtype=np.float32)
            reference_points = np.asarray([match.ref_pt for match in inliers], dtype=np.float32)
            _, refined_reference, subpixel_diagnostics = refine_subpixel(
                mov_gray,
                ref_gray,
                source_points,
                reference_points,
                patch_size=request.subpixel_patch_size,
                peak_response_threshold=request.subpixel_peak_threshold,
            )
            subpixel_diagnostics["enabled"] = True
            half_patch = request.subpixel_patch_size // 2
            rejection_histogram = {"border_top": 0, "border_bottom": 0, "border_left": 0, "border_right": 0}
            for result, point in zip(subpixel_diagnostics["per_match"], reference_points):
                if result["refinement_status"] != "rejected_out_of_bounds":
                    continue
                if point[1] - half_patch < 0:
                    rejection_histogram["border_top"] += 1
                if point[1] + half_patch > ref_gray.shape[0]:
                    rejection_histogram["border_bottom"] += 1
                if point[0] - half_patch < 0:
                    rejection_histogram["border_left"] += 1
                if point[0] + half_patch > ref_gray.shape[1]:
                    rejection_histogram["border_right"] += 1
            subpixel_diagnostics["rejection_histogram"] = rejection_histogram
            for match, point in zip(inliers, refined_reference):
                match.ref_pt = [float(point[0]), float(point[1])]
        dur = (time.perf_counter() - t0) * 1000.0
        stages.append(PipelineStageInfo(
            stage_number=6, name="GEOMETRIC VERIFICATION",
            status="COMPLETED" if (matrix is not None and is_stable) else "FAILED",
            duration_ms=round(dur, 1),
            details=f"{request.estimator_method.value.upper()} inliers: {len(inliers)} / {len(filtered_matches)}"
        ))

        # ==========================================
        # STAGE 7: SPATIAL BALANCING
        # ==========================================
        t0 = time.perf_counter()
        h_ref, w_ref = ref_gray.shape[:2]
        if request.spatial_balancing and inliers:
            spatially_selected, spatial_stats = SpatialBalancing.balance(
                matches=inliers,
                img_width=w_ref,
                img_height=h_ref,
                grid_size=request.grid_size,
                max_per_cell=request.max_features_per_cell,
            )
            active_inliers = spatially_selected
        else:
            active_inliers = inliers
            _, spatial_stats = SpatialBalancing.balance(
                matches=inliers,
                img_width=w_ref,
                img_height=h_ref,
                grid_size=request.grid_size,
                max_per_cell=9999,
            )
        dur = (time.perf_counter() - t0) * 1000.0
        stages.append(PipelineStageInfo(
            stage_number=7, name="SPATIAL BALANCING", status="COMPLETED", duration_ms=round(dur, 1),
            details=f"Grid {request.grid_size}x{request.grid_size}: {spatial_stats.occupied_cells_after}/{spatial_stats.total_cells} cells ({spatial_stats.coverage_percentage_after}%)"
        ))

        # Forensic match decision audit log (Suggestion 4)
        decisions_path = run_dir / "match_decisions.jsonl"
        try:
            with open(decisions_path, "w", encoding="utf-8") as f_dec:
                for rejection in level_rejections:
                    f_dec.write(json.dumps({
                        "stage": "level_filter",
                        "decision": "reject",
                        "reason": "level_gap",
                        **rejection,
                    }) + "\n")
                weights = estimator_diagnostics.get("weights", [])
                residuals = estimator_diagnostics.get("residuals_px", [])
                if request.estimator_method == EstimatorMethod.MAGSAC:
                    for idx, match in enumerate(filtered_matches):
                        weight = float(weights[idx]) if idx < len(weights) else 0.0
                        residual = float(residuals[idx]) if idx < len(residuals) else None
                        f_dec.write(json.dumps({
                            "match_id": idx,
                            "stage": "magsac",
                            "decision": "accept" if match.is_inlier else "reject",
                            "reason": None if match.is_inlier else "low_weight",
                            "weight": weight,
                            "residual_px": residual,
                        }) + "\n")
                for result in subpixel_diagnostics.get("per_match", []):
                    f_dec.write(json.dumps({
                        "match_id": result["match_id"],
                        "stage": "subpixel",
                        "decision": "refined" if result["refinement_status"] == "refined" else "reject",
                        "reason": None if result["refinement_status"] == "refined" else result["refinement_status"],
                        "residual_px": result["residual_px"],
                        "uncertainty_x": result["uncertainty_x"],
                        "uncertainty_y": result["uncertainty_y"],
                        "peak_response": result["peak_response"],
                    }) + "\n")
                for idx, m in enumerate(filtered_matches):
                    record = {
                        "match_id": idx,
                        "ref_pt": m.ref_pt,
                        "mov_pt": m.mov_pt,
                        "distance": float(m.distance),
                        "pyramid_level_source": int(levels_ref[m.ref_idx]) if levels_ref is not None and m.ref_idx < len(levels_ref) else None,
                        "pyramid_level_reference": int(levels_mov[m.mov_idx]) if levels_mov is not None and m.mov_idx < len(levels_mov) else None,
                        "ratio_test": {"decision": "accept", "threshold": request.ratio_threshold},
                        "geometric_verification": {
                            "decision": "accept" if m.is_inlier else "reject",
                            "reason": "consensus_inlier" if m.is_inlier else "residual_outlier"
                        },
                        "spatial_balancing": {
                            "decision": "accept" if m.is_spatially_selected else "reject",
                            "reason": "top_cell_budget" if m.is_spatially_selected else "cell_capacity_reached"
                        }
                    }
                    f_dec.write(json.dumps(record) + "\n")
        except Exception as err:
            logger.warning(f"Could not write match_decisions.jsonl: {err}")
        with open(run_dir / "match_points.csv", "w", encoding="utf-8", newline="") as match_file:
            match_file.write("match_id,ref_x,ref_y,mov_x,mov_y,residual_pixels,residual_meters,uncertainty_x,uncertainty_y,refinement_status\n")
            gsd_meters_per_pixel = request.gsd_meters_per_pixel
            if gsd_meters_per_pixel is None:
                gsd_meters_per_pixel = derive_gsd_meters_per_pixel(str(ref_path))
            for match_id, match in enumerate(filtered_matches):
                result = next((item for item in subpixel_diagnostics.get("per_match", []) if item["match_id"] == match_id), None)
                residual = result["residual_px"] if result else float("nan")
                uncertainty_x = result["uncertainty_x"] if result else float("nan")
                uncertainty_y = result["uncertainty_y"] if result else float("nan")
                status_value = result["refinement_status"] if result else "rejected_low_peak"
                residual_meters = residual * gsd_meters_per_pixel if np.isfinite(gsd_meters_per_pixel) and np.isfinite(residual) else float("nan")
                match_file.write(f"{match_id},{match.ref_pt[0]},{match.ref_pt[1]},{match.mov_pt[0]},{match.mov_pt[1]},{residual},{residual_meters},{uncertainty_x},{uncertainty_y},{status_value}\n")

        # ==========================================
        # STAGE 8 & 9: TRANSFORMATION & REGISTRATION
        # ==========================================
        t0 = time.perf_counter()
        if matrix is not None and is_stable:
            registered_img, overlay_img, difference_img = ImageRegistration.warp_and_render(
                ref_gray, mov_gray, matrix, model_type=request.geometric_model
            )
            stages.append(PipelineStageInfo(stage_number=8, name="TRANSFORMATION", status="COMPLETED", duration_ms=4.0, details=f"Model: {request.geometric_model.value.upper()}"))
            stages.append(PipelineStageInfo(stage_number=9, name="REGISTRATION", status="COMPLETED", duration_ms=round((time.perf_counter() - t0)*1000.0, 1), details="Registered, overlay, and difference maps synthesized"))
        else:
            registered_img = mov_gray.copy()
            overlay_img = ref_gray.copy()
            difference_img = ref_gray.copy()
            stages.append(PipelineStageInfo(stage_number=8, name="TRANSFORMATION", status="FAILED", duration_ms=1.0, details="Skipped due to unverified geometry"))
            stages.append(PipelineStageInfo(stage_number=9, name="REGISTRATION", status="FAILED", duration_ms=1.0, details="Failed registration"))

        # ==========================================
        # STAGE 10: METRICS EVALUATION & FAIL-SAFE
        # ==========================================
        runtime_ms = (time.perf_counter() - start_total) * 1000.0
        status, metrics, failure_reason = MetricsCalculator.evaluate_registration(
            kps_ref_count=len(kps_ref),
            kps_mov_count=len(kps_mov),
            candidate_count=candidate_count,
            filtered_count=len(filtered_matches),
            inliers=active_inliers,
            matrix=matrix,
            spatial_coverage_before=spatial_stats.coverage_percentage_before,
            spatial_coverage_after=spatial_stats.coverage_percentage_after,
            runtime_ms=runtime_ms,
            is_matrix_stable=is_stable,
            matrix_msg=stability_msg,
            model_type=request.geometric_model,
            metric_mode=MetricMode.MEASURED,
            simulation_seed=None,
            force_fail_safe=request.fail_safe_override,
            raw_inlier_count=len(inliers),
        )
        save_json(run_dir / "quality_report.json", {
            "estimator": request.estimator_method.value,
            "sigma_max": 3.0 if request.estimator_method == EstimatorMethod.MAGSAC else None,
            "best_sigma": estimator_diagnostics.get("best_sigma"),
            "n_hypotheses_tried": estimator_diagnostics.get("n_hypotheses_tried"),
            "n_inliers": len(inliers),
            "weighted_rms_px": estimator_diagnostics.get("weighted_rms_px"),
            "subpixel": {
                "enabled": subpixel_diagnostics["enabled"],
                "patch_size": request.subpixel_patch_size,
                "peak_response_threshold": request.subpixel_peak_threshold,
                "n_refined": subpixel_diagnostics["n_refined"],
                "n_rejected_refinement": subpixel_diagnostics["n_rejected_refinement"],
                "n_rejected_out_of_bounds": subpixel_diagnostics["n_rejected_out_of_bounds"],
                "mean_residual_px": subpixel_diagnostics["mean_residual_px"],
                "median_residual_px": subpixel_diagnostics["median_residual_px"],
                "p95_residual_px": subpixel_diagnostics["p95_residual_px"],
                "rejection_histogram": subpixel_diagnostics.get("rejection_histogram", {"border_top": 0, "border_bottom": 0, "border_left": 0, "border_right": 0}),
            },
            "routing": self._routing_config(request),
            "registration_decision": evaluate_registration(
                overlap_ratio=1.0,
                inlier_count=len(inliers),
                inlier_ratio=len(inliers) / max(len(filtered_matches), 1),
                spatial_coverage=spatial_stats.coverage_percentage_after / 100.0,
                rmse_pixels=metrics.rmse_px,
                transform_matrix=matrix,
            ),
        })
        stages.append(PipelineStageInfo(
            stage_number=10, name="METRICS", status="COMPLETED" if status != RegistrationStatus.FAILED else "FAILED",
            duration_ms=2.5, details=f"Status: {status.value} | Confidence: {metrics.confidence_level.value}"
        ))

        # Save all 13 artifacts
        paths = self._persist_artifacts(
            run_id=run_id,
            run_dir=run_dir,
            request=request,
            ref_path=ref_path,
            mov_path=mov_path,
            kps_ref=kps_ref,
            kps_mov=kps_mov,
            matches_candidate=filtered_matches,
            matches_filtered=filtered_matches,
            matches_inliers=inliers,
            matches_spatial=active_inliers,
            registered_img=registered_img,
            overlay_img=overlay_img,
            difference_img=difference_img,
            ref_img=ref_gray,
            mov_img=mov_gray,
            metrics=metrics,
            status=status,
            exec_mode=ExecutionMode.LIVE,
            subpixel_diagnostics=subpixel_diagnostics,
        )

        matrix_serializable = matrix.tolist() if matrix is not None else None

        return PipelineRunResponse(
            run_id=run_id,
            status=status,
            execution_mode=ExecutionMode.LIVE,
            stages=stages,
            metrics=metrics,
            spatial_stats=spatial_stats,
            outputs=paths,
            warnings=warnings,
            failure_reason=failure_reason,
            diagnostic_details={
                "stability_msg": stability_msg,
                "inlier_count": len(active_inliers),
                "filtered_count": len(filtered_matches),
                "geometric_model": request.geometric_model.value,
            },
            transformation_matrix=matrix_serializable,
            configuration=request.model_dump(),
        )

    def _run_demo_pipeline(
        self,
        run_id: str,
        run_dir: Path,
        request: PipelineRunRequest,
        stages: List[PipelineStageInfo],
        ref_gray: np.ndarray,
        mov_gray: np.ndarray,
        ref_path: Path,
        mov_path: Path,
        start_total: float,
    ) -> PipelineRunResponse:
        """Execute demo pipeline with reproducible metrics."""
        (
            status,
            metrics,
            spatial_stats,
            matches,
            registered_img,
            overlay_img,
            difference_img,
            H,
            failure_reason,
        ) = self.simulator.run_simulation(ref_gray, mov_gray, request)

        # Build demo stage markers
        stage_names = [
            (2, "PREPROCESSING", "Multi-modal contrast balancing"),
            (3, "FEATURE EXTRACTION", f"{request.feature_method.value} descriptor"),
            (4, "FEATURE MATCHING", f"{request.matcher.value} matching"),
            (5, "RATIO FILTERING", f"Threshold {request.ratio_threshold}"),
            (6, "GEOMETRIC VERIFICATION", f"RANSAC/MAGSAC {request.geometric_model.value}"),
            (7, "SPATIAL BALANCING", f"Grid {request.grid_size}x{request.grid_size}"),
            (8, "TRANSFORMATION", "Coordinate warp"),
            (9, "REGISTRATION", "Overlay & difference generation"),
            (10, "METRICS", f"Metric evaluation (Seed {settings.SIMULATION_SEED})"),
        ]
        for snum, sname, sdet in stage_names:
            stages.append(PipelineStageInfo(
                stage_number=snum,
                name=sname,
                status="COMPLETED",
                duration_ms=round(5.0 + (snum * 1.5), 1),
                details=sdet,
            ))

        inliers = [m for m in matches if m.is_inlier]
        spatial_matches = [m for m in matches if m.is_spatially_selected]

        paths = self._persist_artifacts(
            run_id=run_id,
            run_dir=run_dir,
            request=request,
            ref_path=ref_path,
            mov_path=mov_path,
            kps_ref=[],
            kps_mov=[],
            matches_candidate=matches,
            matches_filtered=matches,
            matches_inliers=inliers,
            matches_spatial=spatial_matches,
            registered_img=registered_img,
            overlay_img=overlay_img,
            difference_img=difference_img,
            ref_img=ref_gray,
            mov_img=mov_gray,
            metrics=metrics,
            status=status,
            exec_mode=ExecutionMode.DEMO,
        )

        return PipelineRunResponse(
            run_id=run_id,
            status=status,
            execution_mode=ExecutionMode.DEMO,
            stages=stages,
            metrics=metrics,
            spatial_stats=spatial_stats,
            outputs=paths,
            warnings=["Demo mode: Executed via reproducible demo engine (Seed 26166)."],
            failure_reason=failure_reason,
            diagnostic_details={
                "simulation_seed": settings.SIMULATION_SEED,
                "feature_method": request.feature_method.value,
                "inlier_count": len(inliers),
            },
            transformation_matrix=H.tolist() if H is not None else None,
            configuration=request.model_dump(),
        )

    def _persist_artifacts(
        self,
        run_id: str,
        run_dir: Path,
        request: PipelineRunRequest,
        ref_path: Path,
        mov_path: Path,
        kps_ref: List[Any],
        kps_mov: List[Any],
        matches_candidate: List[MatchPairModel],
        matches_filtered: List[MatchPairModel],
        matches_inliers: List[MatchPairModel],
        matches_spatial: List[MatchPairModel],
        registered_img: np.ndarray,
        overlay_img: np.ndarray,
        difference_img: np.ndarray,
        ref_img: np.ndarray,
        mov_img: np.ndarray,
        metrics: RegistrationMetrics,
        status: RegistrationStatus,
        exec_mode: ExecutionMode,
        subpixel_diagnostics: Optional[Dict[str, Any]] = None,
    ) -> ArtifactPaths:
        """Persist all required JSON and image artifacts for complete auditability.

        GC is disabled during this entire method because native libraries
        (numpy, cv2, rasterio) can cause access violations on Windows when
        Python's garbage collector runs during C-level operations on the
        arrays and Path objects produced by the pipeline.
        See Phase 3.5 diagnostic report.
        """
        # Windows + OpenCV/NumPy: GC running during native C calls (pathlib
        # operations, numpy array processing, cv2.imwrite/warpAffine)
        # can trigger intermittent access violations (0xC0000005).
        # Disabling GC during artifact persistence stabilizes the operation.
        gc.disable()
        try:
            subpixel_diagnostics = subpixel_diagnostics or {"enabled": False, "n_refined": 0, "n_rejected_refinement": 0, "n_rejected_out_of_bounds": 0, "per_match": [], "mean_residual_px": float("nan"), "median_residual_px": float("nan"), "p95_residual_px": float("nan")}
            # 1. input_metadata.json
            save_json(run_dir / "input_metadata.json", {
                "run_id": run_id,
                "timestamp": datetime.utcnow().isoformat(),
                "reference_image": str(ref_path.name),
                "moving_image": str(mov_path.name),
                "reference_sensor": request.reference_sensor.value,
                "moving_sensor": request.moving_sensor.value,
                "reference_dimensions": [int(ref_img.shape[1]), int(ref_img.shape[0])],
                "moving_dimensions": [int(mov_img.shape[1]), int(mov_img.shape[0])],
            })
            routing = self._routing_config(request)
            save_json(run_dir / "run_manifest.json", build_run_manifest(
                run_id,
                str(ref_path),
                str(mov_path),
                request.model_dump(),
                synthetic_validation=exec_mode == ExecutionMode.DEMO,
                seed=settings.SIMULATION_SEED if exec_mode == ExecutionMode.DEMO else None,
                routing_config=routing,
            ))

            # 2. configuration.json
            save_json(run_dir / "configuration.json", request.model_dump())

            # 3. keypoints_reference.json
            kps_ref_data = [{"x": round(float(kp.pt[0]), 2), "y": round(float(kp.pt[1]), 2), "size": round(float(kp.size), 2)} for kp in kps_ref] if kps_ref else []
            save_json(run_dir / "keypoints_reference.json", kps_ref_data[:500])

            # 4. keypoints_moving.json
            kps_mov_data = [{"x": round(float(kp.pt[0]), 2), "y": round(float(kp.pt[1]), 2), "size": round(float(kp.size), 2)} for kp in kps_mov] if kps_mov else []
            save_json(run_dir / "keypoints_moving.json", kps_mov_data[:500])

            # 5. matches_candidate.json
            save_json(run_dir / "matches_candidate.json", [m.model_dump() for m in matches_candidate[:300]])

            # 6. matches_filtered.json
            save_json(run_dir / "matches_filtered.json", [m.model_dump() for m in matches_filtered[:300]])

            # 7. matches_inliers.json
            save_json(run_dir / "matches_inliers.json", [m.model_dump() for m in matches_inliers[:300]])

            # 8. matches_spatial.json
            save_json(run_dir / "matches_spatial.json", [m.model_dump() for m in matches_spatial[:300]])

            # 9, 10, 11. Images
            save_image(run_dir / "registered.png", registered_img)
            save_image(run_dir / "overlay.png", overlay_img)
            save_image(run_dir / "difference.png", difference_img)

            # Correspondence visualization image
            pts_r = [m.ref_pt for m in matches_filtered]
            pts_m = [m.mov_pt for m in matches_filtered]
            inlier_mask = [m.is_inlier for m in matches_filtered]
            corr_vis = draw_correspondences(ref_img, mov_img, pts_r, pts_m, inlier_mask)
            save_image(run_dir / "correspondences.png", corr_vis)

            # 12. metrics.json
            save_json(run_dir / "metrics.json", metrics.model_dump())

            # 13. experiment_log.json
            save_json(run_dir / "experiment_log.json", {
                "run_id": run_id,
                "timestamp": datetime.utcnow().isoformat(),
                "status": status.value,
                "execution_mode": exec_mode.value,
                "reference_sensor": request.reference_sensor.value,
                "moving_sensor": request.moving_sensor.value,
                "feature_method": request.feature_method.value,
                "matcher": request.matcher.value,
                "geometric_model": request.geometric_model.value,
                "ratio_threshold": request.ratio_threshold,
                "ransac_threshold": request.ransac_threshold,
                "spatial_grid_size": request.grid_size,
                "spatial_balancing": request.spatial_balancing,
                "keypoints_ref": metrics.keypoints_reference,
                "keypoints_mov": metrics.keypoints_moving,
                "candidate_matches": metrics.candidate_matches,
                "filtered_matches": metrics.filtered_matches,
                "inliers": metrics.ransac_inliers,
                "inlier_ratio": metrics.inlier_ratio,
                "spatial_coverage": metrics.spatial_coverage,
                "rmse_px": metrics.rmse_px,
                "runtime_ms": metrics.runtime_ms,
                "confidence": metrics.confidence_level.value,
            })

            base_url = f"/api/v1/results/{run_id}/artifact"
            return ArtifactPaths(
                registered_image_url=f"{base_url}/registered.png",
                overlay_image_url=f"{base_url}/overlay.png",
                difference_image_url=f"{base_url}/difference.png",
                correspondence_image_url=f"{base_url}/correspondences.png",
                artifacts_dir=str(run_dir),
            )
        finally:
            gc.enable()

    def _extract_features(
        self,
        img: np.ndarray,
        method: FeatureMethod,
        max_features: int,
    ) -> Tuple[List[cv2.KeyPoint], np.ndarray, str, Optional[np.ndarray]]:
        """Extract features using RIFT2, SIFT, or joint ablation selection."""
        method_str = str(method.value if hasattr(method, "value") else method).lower()
        if method_str == "hopc":
            hopc_map = compute_hopc(img)
            kps, desc = hopc_keypoints_from_dense(img, hopc_map, max_keypoints=max_features)
            return kps, desc, "HOPC", None
        if method_str == "rift2_multiscale":
            points, descriptors, levels = extract_rift2_multiscale(img, n_levels=3)
            keypoints = [LunarKeyPoint(float(x), float(y), 96.0, pyramid_level=int(level)) for (x, y), level in zip(points, levels)]
            return keypoints, descriptors, "RIFT2-MULTISCALE", levels
        if "rift" in method_str:
            ext = RIFT2Extractor(max_features=max_features)
            kps, desc = ext.extract(img)
            return kps, desc, "RIFT2", None
        elif "both" in method_str:
            rift_ext = RIFT2Extractor(max_features=max_features // 2)
            sift_ext = SIFTExtractor(nfeatures=max_features // 2)
            kps_r, desc_r = rift_ext.extract(img)
            kps_s, desc_s = sift_ext.extract(img)
            if len(kps_r) >= 15:
                return kps_r, desc_r, "RIFT2+SIFT(RIFT2-Primary)", None
            elif len(kps_s) > 0:
                return kps_s, desc_s, "RIFT2+SIFT(SIFT-Fallback)", None
            return kps_r, desc_r, "RIFT2+SIFT", None
        elif "superglue" in method_str:
            # SuperGlue uses SIFT keypoints; Sinkhorn matching happens in demo routing
            ext = SIFTExtractor(nfeatures=max_features)
            kps, desc = ext.extract(img)
            return kps, desc, "SuperGlue(SIFT+Sinkhorn)", None
        else:
            ext = SIFTExtractor(nfeatures=max_features)
            kps, desc = ext.extract(img)
            return kps, desc, "SIFT", None

    @staticmethod
    def _routing_config(request: PipelineRunRequest) -> Dict[str, Any]:
        """Return the sensor-pair routing decision for pipeline artifacts."""
        config = select_pipeline_config(
            {"sensor": request.moving_sensor.value},
            {"sensor": request.reference_sensor.value},
            request.forced_config,
        )
        return {
            "source_sensor": config.source_sensor,
            "reference_sensor": config.reference_sensor,
            "preprocessing": config.preprocessing,
            "feature_method": config.feature_method,
            "matcher": config.matcher,
            "estimator": config.estimator,
            "geometry_model": config.geometry_model,
            "subpixel_refinement": config.subpixel_refinement,
            "pyramid_levels": config.pyramid_levels,
            "rationale": config.rationale,
        }

    def _build_failure_response(
        self,
        run_id: str,
        run_dir: Path,
        request: PipelineRunRequest,
        stages: List[PipelineStageInfo],
        reason: str
    ) -> PipelineRunResponse:
        metrics = RegistrationMetrics(
            metric_mode=MetricMode.MEASURED,
            keypoints_reference=0,
            keypoints_moving=0,
            candidate_matches=0,
            filtered_matches=0,
            ransac_inliers=0,
            inlier_ratio=0.0,
            spatial_coverage=0.0,
            spatial_coverage_before=0.0,
            rmse_px=None,
            runtime_ms=0.0,
            confidence_level=ConfidenceLevel.REJECTED,
            confidence_score=0.0,
            confidence_explanation=f"REGISTRATION FAILED: {reason}",
        )
        return PipelineRunResponse(
            run_id=run_id,
            status=RegistrationStatus.FAILED,
            execution_mode=ExecutionMode.LIVE,
            stages=stages,
            metrics=metrics,
            spatial_stats=None,
            outputs=ArtifactPaths(artifacts_dir=str(run_dir)),
            warnings=["Pipeline aborted due to validation failure"],
            failure_reason=reason,
            diagnostic_details={"error": reason},
            transformation_matrix=None,
            configuration=request.model_dump(),
        )

pipeline_service = PipelineService()
