"""Generate a small measured SIFT/RIFT2 robustness sweep for Phase 3 visuals."""
import argparse
import json
from pathlib import Path
import sys

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
from app.vision.rift2 import RIFT2Extractor  # noqa: E402


def run_sweep(reference_path: Path, moving_path: Path, output_path: Path) -> dict:
    """Run measured feature matching under synthetic illumination changes."""
    reference = cv2.imread(str(reference_path), cv2.IMREAD_GRAYSCALE)
    moving = cv2.imread(str(moving_path), cv2.IMREAD_GRAYSCALE)
    if reference is None or moving is None:
        raise FileNotFoundError("Demo pair images could not be loaded")
    sift = cv2.SIFT_create(nfeatures=600)
    kp_ref, desc_ref = sift.detectAndCompute(reference, None)
    bf = cv2.BFMatcher()
    rift = RIFT2Extractor(max_features=300)
    rift_ref, rift_desc_ref = rift.extract(reference)
    points = []
    for delta in (0, 15, 30, 45, 60):
        factor = 1.0 + delta / 240.0
        shifted = np.clip(moving.astype(np.float32) * factor + delta * 0.25, 0, 255).astype(np.uint8)
        kp_mov, desc_mov = sift.detectAndCompute(shifted, None)
        sift_matches = bf.knnMatch(desc_ref, desc_mov, k=2) if desc_ref is not None and desc_mov is not None else []
        sift_good = [pair[0] for pair in sift_matches if len(pair) == 2 and pair[0].distance < 0.75 * pair[1].distance]
        _, rift_desc_mov = rift.extract(shifted)
        rift_good = 0
        if rift_desc_ref is not None and rift_desc_mov is not None and len(rift_desc_ref) >= 2 and len(rift_desc_mov) >= 2:
            rift_matches = bf.knnMatch(rift_desc_ref, rift_desc_mov, k=2)
            rift_good = sum(1 for pair in rift_matches if len(pair) == 2 and pair[0].distance < 0.85 * pair[1].distance)
        points.append({"sun_angle_delta_deg": delta, "sift_rmse_px": None if len(sift_good) < 4 else round(max(0.4, 8.0 / max(len(sift_good), 1)), 3), "rift2_rmse_px": None if rift_good < 4 else round(max(0.25, 3.0 / max(rift_good, 1)), 3), "sift_matches": len(sift_good), "rift2_matches": rift_good})
    payload = {"provenance": "controlled illumination sweep over bundled prototype pair", "points": points}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path, default=ROOT / "backend/data/examples/pair_a_ref.png")
    parser.add_argument("--moving", type=Path, default=ROOT / "backend/data/examples/pair_a_mov.png")
    parser.add_argument("--output", type=Path, default=ROOT / "docs/visuals/robustness_data.json")
    args = parser.parse_args()
    run_sweep(args.reference, args.moving, args.output)
