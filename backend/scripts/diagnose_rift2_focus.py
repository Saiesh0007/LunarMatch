"""Focused RIFT2 diagnosis on Pair A — where do matches get lost?"""
import sys, warnings
from pathlib import Path
warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import cv2
from app.services.image_service import image_service
from app.preprocessing.pyramid import extract_rift2_multiscale
from app.vision.matcher import FeatureMatcher
from app.vision.geometry import magsac_plus_plus
from app.models.schemas import MatcherType, GeometricModel, PreprocessingConfig
from app.vision.preprocessing import preprocess_lunar_image

def load_gray(image_id):
    path = image_service.resolve_image_path(image_id)
    return cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)

ref = load_gray("demo_pair_a_ref")
mov = load_gray("demo_pair_a_mov")
print(f"Pair A: ref shape={ref.shape}, mov shape={mov.shape}")

# Step 2: Raw extraction (no preprocessing)
pts_r, desc_r, lvl_r = extract_rift2_multiscale(ref, n_levels=3)
pts_m, desc_m, lvl_m = extract_rift2_multiscale(mov, n_levels=3)
print(f"\nStep 2: Raw RIFT2 multiscale extraction")
print(f"  ref: {len(pts_r)} kps, desc shape={desc_r.shape}")
print(f"  mov: {len(pts_m)} kps, desc shape={desc_m.shape}")
print(f"  ref levels: { {l: int((lvl_r == l).sum()) for l in sorted(set(lvl_r.tolist()))} }")
print(f"  mov levels: { {l: int((lvl_m == l).sum()) for l in sorted(set(lvl_m.tolist()))} }")

# Step 3: With CLAHE preprocessing
pp = PreprocessingConfig(clahe=True)
ref_pre, _ = preprocess_lunar_image(ref, pp)
mov_pre, _ = preprocess_lunar_image(mov, pp)
pts_r2, desc_r2, lvl_r2 = extract_rift2_multiscale(ref_pre, n_levels=3)
pts_m2, desc_m2, lvl_m2 = extract_rift2_multiscale(mov_pre, n_levels=3)
print(f"\nStep 3: RIFT2 + CLAHE extraction")
print(f"  ref: {len(pts_r2)} kps")
print(f"  mov: {len(pts_m2)} kps")
print(f"  (vs raw: {len(pts_r)} and {len(pts_m)})")

# Step 4: Matching at different ratios, with/without level filter, raw vs CLAHE
print(f"\nStep 4: Matching analysis")
for label, desc_r_use, desc_m_use, lvl_r_use, lvl_m_use in [
    ("RAW", desc_r, desc_m, lvl_r, lvl_m),
    ("CLAHE", desc_r2, desc_m2, lvl_r2, lvl_m2),
]:
    for ratio in [0.75, 0.80, 0.85, 0.90, 0.95]:
        bf = cv2.BFMatcher(cv2.NORM_L2)
        knn = bf.knnMatch(desc_r_use.astype(np.float32), desc_m_use.astype(np.float32), k=2)
        raw = [p for p in knn if len(p) == 2 and p[0].distance < ratio * p[1].distance]
        no_level_filter = len(raw)
        with_level_filter = len([m for m in raw if abs(int(lvl_r_use[m.queryIdx]) - int(lvl_m_use[m.trainIdx])) <= 1])
        print(f"  {label} ratio={ratio}: raw_matches={no_level_filter}, level_filtered={with_level_filter}")

# Step 5: What's the match distance distribution?
print(f"\nStep 5: Match distance analysis (raw, top 20 matches)")
bf = cv2.BFMatcher(cv2.NORM_L2)
knn = bf.knnMatch(desc_r.astype(np.float32), desc_m.astype(np.float32), k=2)
distances = [(p[0].distance, p[1].distance, p[0].distance/p[1].distance) for p in knn if len(p) == 2]
ratios = sorted([r for _, _, r in distances])
print(f"  Total candidate pairs: {len(distances)}")
print(f"  Best 20 distance ratios: {[f'{r:.4f}' for r in ratios[:20]]}")
print(f"  Median ratio: {ratios[len(ratios)//2]:.4f}")
print(f"  Matches passing 0.75: {sum(1 for r in ratios if r < 0.75)}")
print(f"  Matches passing 0.85: {sum(1 for r in ratios if r < 0.85)}")
print(f"  Matches passing 0.95: {sum(1 for r in ratios if r < 0.95)}")

# Step 6: Try MAGSAC with the best available matches
print(f"\nStep 6: MAGSAC with 0.85 ratio matches (raw, no level filter)")
matches_85 = [p[0] for p in knn if len(p) == 2 and p[0].distance < 0.85 * p[1].distance]
print(f"  Matches at 0.85: {len(matches_85)}")
if len(matches_85) >= 3:
    src_pts = np.array([pts_m[m.trainIdx] for m in matches_85], dtype=np.float32).reshape(-1, 2)
    dst_pts = np.array([pts_r[m.queryIdx] for m in matches_85], dtype=np.float32).reshape(-1, 2)
    matrix, mask, diag = magsac_plus_plus(src_pts, dst_pts, model="affine")
    print(f"  MAGSAC result: matrix={matrix is not None}, inliers={int(mask.sum()) if mask is not None else 0}")
    print(f"  diag: {diag}")
else:
    print(f"  Too few matches for MAGSAC (need >= 3)")
