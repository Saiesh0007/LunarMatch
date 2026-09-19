#!/usr/bin/env python3
"""Standalone benchmark: compare RIFT2 + BFMatcher against deep matchers.

Extracts RIFT2 keypoints and descriptors ONCE per image pair, then evaluates
four matchers on the same keypoint and descriptor features:
  1. RIFT2 + BF (shipped live pipeline)
  2. SuperGlue (outdoor pretrained weights)
  3. LightGlue (SuperPoint-pretrained weights)
  4. LoFTR (detector-free local feature transformer)

Usage (from backend/):
    python -m scripts.matcher_benchmark
"""
from __future__ import annotations

import gc
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np

# ──────────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────────
_SCRIPT_DIR = Path(__file__).resolve().parent
_BACKEND_DIR = _SCRIPT_DIR.parent
_FIXTURES_DIR = _BACKEND_DIR / "tests" / "fixtures"
_WEIGHTS_DIR = _BACKEND_DIR / "weights"
_OUTPUTS_DIR = _BACKEND_DIR / "outputs"

if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

# ──────────────────────────────────────────────────────────────────
# Fixture pairs: (pair_label, ref_filename, mov_filename)
# ──────────────────────────────────────────────────────────────────
_PAIRS: List[Tuple[str, str, str]] = [
    ("pair_a_640", "pair_a_ref.png", "pair_a_mov.png"),
]

# Torch availability
try:
    import torch
    _TORCH_AVAILABLE = True
except ImportError:
    _TORCH_AVAILABLE = False


def _load_pair(ref_name: str, mov_name: str) -> Optional[Tuple[np.ndarray, np.ndarray]]:
    """Load a fixture image pair as grayscale arrays."""
    ref_path = _FIXTURES_DIR / ref_name
    mov_path = _FIXTURES_DIR / mov_name
    if not ref_path.exists() or not mov_path.exists():
        return None
    ref = cv2.imread(str(ref_path), cv2.IMREAD_GRAYSCALE)
    mov = cv2.imread(str(mov_path), cv2.IMREAD_GRAYSCALE)
    if ref is None or mov is None:
        return None
    return ref, mov


def _eval_matches(pts_mov: np.ndarray, pts_ref: np.ndarray, min_inliers: int = 10) -> Tuple[bool, Optional[float], int]:
    """Compute RANSAC homography, inliers count, and RMSE on inliers.

    Returns:
      (success: bool, rmse_px: float | None, inlier_count: int)
    """
    if len(pts_mov) < 4:
        return False, None, len(pts_mov)

    gc.disable()
    try:
        H, mask = cv2.findHomography(pts_mov, pts_ref, cv2.RANSAC, 3.0)
    finally:
        gc.enable()

    if H is None or mask is None:
        return False, None, 0

    inlier_mask = mask.ravel().astype(bool)
    inliers = int(inlier_mask.sum())
    if inliers < min_inliers:
        return False, None, inliers

    inlier_mov = pts_mov[inlier_mask].reshape(-1, 1, 2)
    inlier_ref = pts_ref[inlier_mask]

    transformed = cv2.perspectiveTransform(inlier_mov, H).reshape(-1, 2)
    residuals = np.linalg.norm(inlier_ref - transformed, axis=1)
    rmse = float(np.sqrt(np.mean(residuals ** 2)))

    return True, round(rmse, 2), inliers


def run_benchmark() -> Dict[str, Any]:
    """Run full matcher benchmark across test pairs."""
    from app.vision.rift2 import RIFT2Extractor
    from app.vision.matcher import FeatureMatcher
    from app.models.schemas import MatcherType

    try:
        from app.benchmark.matcher_wrappers import superglue_match, lightglue_match, loftr_match
        wrappers_available = True
    except Exception as err:
        wrappers_available = False
        wrapper_err = str(err)

    loaded_pairs: List[Tuple[str, np.ndarray, np.ndarray]] = []
    for label, ref_fn, mov_fn in _PAIRS:
        pair = _load_pair(ref_fn, mov_fn)
        if pair is not None:
            loaded_pairs.append((label, pair[0], pair[1]))

    if not loaded_pairs:
        raise RuntimeError("No fixture pairs found in tests/fixtures/")

    print(f"Benchmark: {len(loaded_pairs)} pairs loaded at 640x640")

    # Matcher metrics accumulators
    results_by_matcher: Dict[str, List[Dict[str, Any]]] = {
        "RIFT2 + BF": [],
        "SuperGlue": [],
        "LightGlue": [],
        "LoFTR": [],
    }

    extractor = RIFT2Extractor(max_features=512)

    for label, ref, mov in loaded_pairs:
        print(f"\nEvaluating on pair '{label}' ({ref.shape[1]}x{ref.shape[0]}):")

        # 1. Extract RIFT2 keypoints and descriptors ONCE per pair
        t0_ext = time.perf_counter()
        kps_ref, desc_ref = extractor.extract(ref)
        kps_mov, desc_mov = extractor.extract(mov)
        ext_ms = (time.perf_counter() - t0_ext) * 1000.0
        print(f"  [RIFT2 Extractor] {len(kps_ref)} ref / {len(kps_mov)} mov keypoints in {ext_ms:.1f} ms")

        # Prepare coordinate arrays
        pts_ref_all = np.float32([[kp.pt[0], kp.pt[1]] for kp in kps_ref])
        pts_mov_all = np.float32([[kp.pt[0], kp.pt[1]] for kp in kps_mov])

        # ─────────────────────────────────────────────────────────────
        # Matcher 1: RIFT2 + BF (Shipped Live)
        # ─────────────────────────────────────────────────────────────
        t0_bf = time.perf_counter()
        matcher = FeatureMatcher(matcher_type=MatcherType.BF, ratio_threshold=0.75)
        filtered, _ = matcher.match(kps_ref, desc_ref, kps_mov, desc_mov)
        matcher.release()
        bf_ms = (time.perf_counter() - t0_bf) * 1000.0
        # Pipeline execution time includes extraction + matching
        total_rift2_ms = ext_ms + bf_ms

        if filtered:
            bf_pts_ref = np.float32([[m.ref_pt[0], m.ref_pt[1]] for m in filtered])
            bf_pts_mov = np.float32([[m.mov_pt[0], m.mov_pt[1]] for m in filtered])
            success_bf, rmse_bf, inliers_bf = _eval_matches(bf_pts_mov, bf_pts_ref)
        else:
            success_bf, rmse_bf, inliers_bf = False, None, 0

        results_by_matcher["RIFT2 + BF"].append({
            "success": success_bf,
            "rmse_px": rmse_bf,
            "matches": inliers_bf,
            "time_ms": total_rift2_ms,
        })
        print(f"  RIFT2 + BF: success={success_bf}, rmse={rmse_bf} px, inliers={inliers_bf}, time={total_rift2_ms:.1f} ms")

        # ─────────────────────────────────────────────────────────────
        # Matcher 2: SuperGlue (Outdoor Pretrained)
        # ─────────────────────────────────────────────────────────────
        if not wrappers_available or not _TORCH_AVAILABLE:
            results_by_matcher["SuperGlue"].append({"skipped": True, "reason": "PyTorch or wrappers not available"})
        else:
            sg_res = superglue_match(pts_ref_all, desc_ref, pts_mov_all, desc_mov, ref.shape, mov.shape)
            if sg_res["reason"] is not None:
                results_by_matcher["SuperGlue"].append({"skipped": True, "reason": sg_res["reason"]})
                print(f"  SuperGlue: skipped ({sg_res['reason']})")
            else:
                matches_sg = sg_res["matches"]
                sg_time = sg_res["time_ms"]
                if matches_sg is not None and len(matches_sg) > 0:
                    sg_pts_ref = pts_ref_all[matches_sg[:, 0]]
                    sg_pts_mov = pts_mov_all[matches_sg[:, 1]]
                    success_sg, rmse_sg, inliers_sg = _eval_matches(sg_pts_mov, sg_pts_ref)
                else:
                    success_sg, rmse_sg, inliers_sg = False, None, 0

                results_by_matcher["SuperGlue"].append({
                    "success": success_sg,
                    "rmse_px": rmse_sg,
                    "matches": inliers_sg,
                    "time_ms": sg_time,
                })
                print(f"  SuperGlue: success={success_sg}, rmse={rmse_sg} px, inliers={inliers_sg}, time={sg_time:.1f} ms")

        # ─────────────────────────────────────────────────────────────
        # Matcher 3: LightGlue (SuperPoint Pretrained)
        # ─────────────────────────────────────────────────────────────
        if not wrappers_available or not _TORCH_AVAILABLE:
            results_by_matcher["LightGlue"].append({"skipped": True, "reason": "PyTorch or wrappers not available"})
        else:
            lg_res = lightglue_match(pts_ref_all, desc_ref, pts_mov_all, desc_mov, ref.shape, mov.shape)
            if lg_res["reason"] is not None:
                results_by_matcher["LightGlue"].append({"skipped": True, "reason": lg_res["reason"]})
                print(f"  LightGlue: skipped ({lg_res['reason']})")
            else:
                matches_lg = lg_res["matches"]
                lg_time = lg_res["time_ms"]
                if matches_lg is not None and len(matches_lg) > 0:
                    lg_pts_ref = pts_ref_all[matches_lg[:, 0]]
                    lg_pts_mov = pts_mov_all[matches_lg[:, 1]]
                    success_lg, rmse_lg, inliers_lg = _eval_matches(lg_pts_mov, lg_pts_ref)
                else:
                    success_lg, rmse_lg, inliers_lg = False, None, 0

                results_by_matcher["LightGlue"].append({
                    "success": success_lg,
                    "rmse_px": rmse_lg,
                    "matches": inliers_lg,
                    "time_ms": lg_time,
                })
                print(f"  LightGlue: success={success_lg}, rmse={rmse_lg} px, inliers={inliers_lg}, time={lg_time:.1f} ms")

        # ─────────────────────────────────────────────────────────────
        # Matcher 4: LoFTR (Detector-Free Local Feature Transformer)
        # ─────────────────────────────────────────────────────────────
        if not wrappers_available or not _TORCH_AVAILABLE:
            results_by_matcher["LoFTR"].append({"skipped": True, "reason": "PyTorch or wrappers not available"})
        else:
            loftr_res = loftr_match(pts_ref_all, desc_ref, pts_mov_all, desc_mov, ref.shape, mov.shape, img_a=ref, img_b=mov)
            if loftr_res["reason"] is not None:
                results_by_matcher["LoFTR"].append({"skipped": True, "reason": loftr_res["reason"]})
                print(f"  LoFTR: skipped ({loftr_res['reason']})")
            else:
                loftr_time = loftr_res["time_ms"]
                kpts0 = loftr_res.get("kpts0")
                kpts1 = loftr_res.get("kpts1")
                if kpts0 is not None and len(kpts0) > 0:
                    success_l, rmse_l, inliers_l = _eval_matches(kpts1, kpts0)
                else:
                    success_l, rmse_l, inliers_l = False, None, 0

                results_by_matcher["LoFTR"].append({
                    "success": success_l,
                    "rmse_px": rmse_l,
                    "matches": inliers_l,
                    "time_ms": loftr_time,
                })
                print(f"  LoFTR: success={success_l}, rmse={rmse_l} px, inliers={inliers_l}, time={loftr_time:.1f} ms")

    del extractor
    gc.collect()

    # ─────────────────────────────────────────────────────────────
    # Aggregate summary
    # ─────────────────────────────────────────────────────────────
    matchers_summary: List[Dict[str, Any]] = []
    pairs_tested = len(loaded_pairs)

    matcher_notes = {
        "RIFT2 + BF": "Shipped (live)",
        "SuperGlue": "Pretrained on natural images; does not transfer",
        "LightGlue": "Pretrained on natural images; does not transfer",
        "LoFTR": "Detector-free; exceeds CPU demo budget",
    }

    for name, entries in results_by_matcher.items():
        if not entries or all(e.get("skipped") for e in entries):
            reason = entries[0].get("reason", "unknown error") if entries else "not run"
            matchers_summary.append({
                "name": name,
                "skipped": True,
                "reason": reason,
            })
            continue

        valid_entries = [e for e in entries if not e.get("skipped")]
        success_count = sum(1 for e in valid_entries if e.get("success", False))
        success_rate = round(float(success_count) / float(len(valid_entries)), 2)

        rmse_values = [e["rmse_px"] for e in valid_entries if e.get("rmse_px") is not None]
        mean_rmse = round(float(np.mean(rmse_values)), 2) if rmse_values else None

        times = [e["time_ms"] for e in valid_entries if "time_ms" in e]
        mean_time = round(float(np.mean(times)), 1) if times else None

        matchers_summary.append({
            "name": name,
            "success_rate": success_rate,
            "mean_rmse_px": mean_rmse,
            "mean_time_ms": mean_time,
            "notes": matcher_notes.get(name, "Benchmarked only"),
        })

    output_data = {
        "pairs_tested": pairs_tested,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "fixture_resolution": "640x640",
        "matchers": matchers_summary,
    }

    # Save output
    _OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    out_file = _OUTPUTS_DIR / "matcher_benchmark.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print(f"\nBenchmark successfully written to: {out_file}")
    print(json.dumps(output_data, indent=2))
    return output_data


if __name__ == "__main__":
    t_start = time.perf_counter()
    run_benchmark()
    print(f"\nTotal benchmark execution time: {time.perf_counter() - t_start:.2f} s")
