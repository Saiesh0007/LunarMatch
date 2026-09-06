import time

from src.io import load_pair
from src.preprocessing import preprocess, DEFAULT_CONFIG as DEFAULT_PREPROCESS
from src.features import extract
from src.matching import match
from src.geometry import extract_match_points, estimate, compute_inlier_stats
from src.spatial import spatial_balance, compute_coverage
from src.registration import register, create_overlay, create_difference
from src.metrics import evaluate


DEFAULT_CONFIG = {
    "preprocessing": {
        "grayscale": True,
        "normalize": True,
        "clahe": True,
        "denoise": False,
        "clahe_clip": 2.0,
        "clahe_grid": 8,
        "denoise_strength": 10,
    },
    "feature": {"method": "sift"},
    "matching": {"method": "bf", "ratio_thresh": 0.75},
    "geometry": {"model": "affine", "ransac_thresh": 5.0},
    "spatial": {"enabled": True, "grid_size": 8, "max_per_cell": 5},
}


def run_pipeline(ref_path, mov_path, config=None):
    if config is None:
        config = DEFAULT_CONFIG

    start_time = time.time()
    result = {
        "status": "failed",
        "reason": None,
        "config": config,
        "metrics": None,
    }

    try:
        ref_image, mov_image = load_pair(ref_path, mov_path)
    except (FileNotFoundError, ValueError) as e:
        result["reason"] = str(e)
        return result

    result["ref_image"] = ref_image
    result["mov_image"] = mov_image

    pre_cfg = config.get("preprocessing", DEFAULT_PREPROCESS)
    ref_processed, ref_steps = preprocess(ref_image, pre_cfg)
    mov_processed, mov_steps = preprocess(mov_image, pre_cfg)
    result["ref_processed"] = ref_processed
    result["mov_processed"] = mov_processed

    feat_cfg = config.get("feature", {})
    method = feat_cfg.get("method", "sift")
    kp_ref, desc_ref = extract(ref_processed, method=method)
    kp_mov, desc_mov = extract(mov_processed, method=method)
    result["kp_ref"] = kp_ref
    result["kp_mov"] = kp_mov

    if len(kp_ref) < 4 or len(kp_mov) < 4:
        result["reason"] = (
            f"Insufficient keypoints: reference={len(kp_ref)}, moving={len(kp_mov)}"
        )
        return result

    match_cfg = config.get("matching", {})
    knn_matches, good_matches = match(
        desc_ref, desc_mov,
        method=match_cfg.get("method", "bf"),
        ratio_thresh=match_cfg.get("ratio_thresh", 0.75),
    )
    result["candidate_matches"] = knn_matches
    result["good_matches"] = good_matches

    if len(good_matches) < 4:
        result["reason"] = f"Insufficient good matches: {len(good_matches)}"
        return result

    pts_ref, pts_mov = extract_match_points(kp_ref, kp_mov, good_matches)

    geo_cfg = config.get("geometry", {})
    model_type = geo_cfg.get("model", "affine")
    transform, inlier_mask = estimate(
        pts_ref, pts_mov,
        model=model_type,
        ransac_thresh=geo_cfg.get("ransac_thresh", 5.0),
    )

    if transform is None:
        result["reason"] = "RANSAC failed to find a stable transformation"
        return result

    inlier_count, inlier_ratio = compute_inlier_stats(inlier_mask)
    result["transform"] = transform
    result["inlier_mask"] = inlier_mask
    result["model_type"] = model_type

    if inlier_count < 4:
        result["reason"] = f"Too few inliers: {inlier_count}"
        return result

    spatial_cfg = config.get("spatial", {})
    spatial_coverage = None
    spatial_indices = None

    if spatial_cfg.get("enabled", True):
        spatial_indices = spatial_balance(
            pts_ref, good_matches, inlier_mask,
            ref_processed.shape,
            grid_size=spatial_cfg.get("grid_size", 8),
            max_per_cell=spatial_cfg.get("max_per_cell", 5),
        )
        if len(spatial_indices) > 0:
            selected_pts = pts_ref[spatial_indices]
            spatial_coverage = compute_coverage(
                selected_pts, ref_processed.shape,
                grid_size=spatial_cfg.get("grid_size", 8),
            )

    result["spatial_indices"] = spatial_indices
    result["spatial_coverage"] = spatial_coverage

    registered_image = register(ref_processed, mov_processed, transform, model=model_type)
    overlay = create_overlay(ref_processed, registered_image)
    difference = create_difference(ref_processed, registered_image)
    result["registered_image"] = registered_image
    result["overlay"] = overlay
    result["difference"] = difference

    runtime = time.time() - start_time

    result["metrics"] = evaluate(
        kp_ref_count=len(kp_ref),
        kp_mov_count=len(kp_mov),
        candidate_count=len(knn_matches),
        good_count=len(good_matches),
        inlier_count=inlier_count,
        inlier_mask=inlier_mask,
        pts_ref=pts_ref,
        pts_mov=pts_mov,
        transform=transform,
        spatial_coverage=spatial_coverage,
        runtime=runtime,
    )

    result["status"] = "success"
    return result
