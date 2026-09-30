"""RIFT2 Zero-Inlier Regression Investigation — read-only diagnosis."""
import sys
import warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import cv2
warnings.filterwarnings("ignore")

from app.services.image_service import image_service
from app.services.pipeline_service import PipelineService
from app.models.requests import PipelineRunRequest
from app.models.schemas import FeatureMethod, MatcherType, GeometricModel, EstimatorMethod, PreprocessingConfig
from app.preprocessing.pyramid import extract_rift2_multiscale
from app.vision.matcher import FeatureMatcher
from app.vision.geometry import magsac_plus_plus
from app.services.router import select_pipeline_config
from app.vision.preprocessing import preprocess_lunar_image


def load_gray(image_id):
    path = image_service.resolve_image_path(image_id)
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    print(f"  {image_id} -> {path}, shape={img.shape}")
    return img


print("=" * 60)
print("STEP 1: Full pipeline reproduction")
print("=" * 60)
svc = PipelineService()
for pair_label, ref_id, mov_id in [("Pair A", "demo_pair_a_ref", "demo_pair_a_mov"),
                                     ("Pair B", "demo_pair_b_ref", "demo_pair_b_mov")]:
    for fm_label, fm in [("RIFT2", FeatureMethod.RIFT2_MULTISCALE), ("SIFT", FeatureMethod.SIFT)]:
        req = PipelineRunRequest(
            reference_image_id=ref_id,
            moving_image_id=mov_id,
            feature_method=fm,
            matcher=MatcherType.BF,
            geometric_model=GeometricModel.AFFINE,
            estimator_method=EstimatorMethod.MAGSAC,
        )
        result = svc.execute_pipeline(req)
        diag = result.diagnostic_details
        print(f"  {pair_label} {fm_label}: status={result.status.value}, "
              f"candidates={diag.get('candidate_count')}, "
              f"filtered={diag.get('filtered_count')}, "
              f"inliers={diag.get('inlier_count')}, "
              f"decision={result.metrics is not None and 'see_qr' or 'N/A'}")

print()
print("=" * 60)
print("STEP 2: Feature extraction in isolation (raw, no preprocessing)")
print("=" * 60)
for pair_label, ref_id, mov_id in [("Pair A", "demo_pair_a_ref", "demo_pair_a_mov"),
                                     ("Pair B", "demo_pair_b_ref", "demo_pair_b_mov")]:
    ref = load_gray(ref_id)
    mov = load_gray(mov_id)
    pts_r, desc_r, lvl_r = extract_rift2_multiscale(ref, n_levels=3)
    pts_m, desc_m, lvl_m = extract_rift2_multiscale(mov, n_levels=3)
    print(f"  {pair_label} RIFT2 raw: ref={len(pts_r)} kps, mov={len(pts_m)} kps")
    print(f"    ref desc shape={desc_r.shape}, level dist={ {l: int((lvl_r == l).sum()) for l in sorted(set(lvl_r.tolist()))} }")
    print(f"    mov desc shape={desc_m.shape}, level dist={ {l: int((lvl_m == l).sum()) for l in sorted(set(lvl_m.tolist()))} }")

print()
print("=" * 60)
print("STEP 3: Feature extraction with preprocessing (CLAHE)")
print("=" * 60)
from app.models.schemas import PreprocessingConfig
pp = PreprocessingConfig(clahe=True)
for pair_label, ref_id, mov_id in [("Pair A", "demo_pair_a_ref", "demo_pair_a_mov"),
                                     ("Pair B", "demo_pair_b_ref", "demo_pair_b_mov")]:
    ref = load_gray(ref_id)
    mov = load_gray(mov_id)
    ref_pre, _ = preprocess_lunar_image(ref, pp)
    mov_pre, _ = preprocess_lunar_image(mov, pp)
    pts_r, desc_r, lvl_r = extract_rift2_multiscale(ref_pre, n_levels=3)
    pts_m, desc_m, lvl_m = extract_rift2_multiscale(mov_pre, n_levels=3)
    print(f"  {pair_label} RIFT2+CLAHE: ref={len(pts_r)} kps, mov={len(pts_m)} kps")

print()
print("=" * 60)
print("STEP 4: Matching (ratio 0.75 vs 0.85 vs 0.95, with/without level filter)")
print("=" * 60)
for pair_label, ref_id, mov_id in [("Pair A", "demo_pair_a_ref", "demo_pair_a_mov"),
                                     ("Pair B", "demo_pair_b_ref", "demo_pair_b_mov")]:
    ref = load_gray(ref_id)
    mov = load_gray(mov_id)
    pts_r, desc_r, lvl_r = extract_rift2_multiscale(ref, n_levels=3)
    pts_m, desc_m, lvl_m = extract_rift2_multiscale(mov, n_levels=3)
    for ratio in [0.75, 0.85, 0.95]:
        matcher = FeatureMatcher(matcher_type=MatcherType.BF, ratio_threshold=ratio)
        # Build fake keypoints for the matcher
        from app.models.schemas import MatchPairModel
        # Just use the matcher's internal knnMatch directly
        bf = cv2.BFMatcher(cv2.NORM_L2)
        knn = bf.knnMatch(desc_r.astype(np.float32), desc_m.astype(np.float32), k=2)
        raw = [p for p in knn if len(p) == 2 and p[0].distance < ratio * p[1].distance]
        with_level_filter = [m for m in raw if abs(int(lvl_r[m.queryIdx]) - int(lvl_m[m.trainIdx])) <= 1]
        print(f"  {pair_label} ratio={ratio}: raw={len(raw)}, level_filtered={len(with_level_filter)}, "
              f"min_level_gap={abs(int(lvl_r[raw[0].queryIdx]) - int(lvl_m[raw[0].trainIdx])) if raw else 'N/A'}")

print()
print("=" * 60)
print("STEP 5: SIFT comparison (same pipeline)")
print("=" * 60)
for pair_label, ref_id, mov_id in [("Pair A", "demo_pair_a_ref", "demo_pair_a_mov"),
                                     ("Pair B", "demo_pair_b_ref", "demo_pair_b_mov")]:
    ref = load_gray(ref_id)
    mov = load_gray(mov_id)
    sift = cv2.SIFT_create(nfeatures=600)
    kp_r, desc_r = sift.detectAndCompute(ref, None)
    kp_m, desc_m = sift.detectAndCompute(mov, None)
    bf = cv2.BFMatcher(cv2.NORM_L2)
    knn = bf.knnMatch(desc_r.astype(np.float32), desc_m.astype(np.float32), k=2)
    matches_75 = [p[0] for p in knn if len(p) == 2 and p[0].distance < 0.75 * p[1].distance]
    print(f"  {pair_label} SIFT: kp_ref={len(kp_r)}, kp_mov={len(kp_m)}, matches(ratio=0.75)={len(matches_75)}")

print()
print("=" * 60)
print("STEP 6: Routing config")
print("=" * 60)
config = select_pipeline_config({"sensor": "unknown"}, {"sensor": "unknown"})
print(f"  feature_method={config.feature_method}")
print(f"  matcher={config.matcher}")
print(f"  pyramid_levels={config.pyramid_levels}")
print(f"  estimator={config.estimator}")
print(f"  geometry_model={config.geometry_model}")
print(f"  preprocessing={config.preprocessing}")
print(f"  rationale={config.rationale}")
