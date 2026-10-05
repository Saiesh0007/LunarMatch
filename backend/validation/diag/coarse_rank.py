"""Rank of the ground-truth hypothesis in the coarse search under different scorings."""
import json
import math
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, ".")
from app.vision import dense_structural as ds  # noqa: E402

pairs = sys.argv[1].split(",")
work = [int(x) for x in (sys.argv[2] if len(sys.argv) > 2 else "240").split(",")]


def gt_pose(d):
    m = np.float32(d["gt"]["mov_pts"]); r = np.float32(d["gt"]["ref_pts"])
    H, _ = cv2.findHomography(m, r, 0)
    A = H[:2, :2] / H[2, 2]
    return math.sqrt(abs(np.linalg.det(A))), -math.degrees(math.atan2(A[1, 0], A[0, 0])) % 360


orig_peak = ds._peak_stats
for n in pairs:
    P = Path("data/real/pairs") / n
    d = json.loads((P / "pair.json").read_text())
    st, at = gt_pose(d)
    mov = ds._to_float(cv2.imread(str(P / d["moving"]["file"]), cv2.IMREAD_UNCHANGED))
    ref = ds._to_float(cv2.imread(str(P / d["reference"]["file"]), cv2.IMREAD_UNCHANGED))
    sp = d["moving"]["gsd_m"] / d["reference"]["gsd_m"]
    for wp in work:
        rows = {}
        for mode in ("s1", "s2"):
            def peak(res, excl, _mode=mode):
                p1, p2, loc = orig_peak(res, excl)
                if False:
                    r = res[np.isfinite(res)]
                    return p1, p1 - (p1 - float(r.mean())) / max(float(r.std()), 1e-6) * 0.01, loc
                return p1, p2, loc
            ds._peak_stats = peak
            c = min(1.0, wp / float(max(ref.shape)))
            hy = ds.coarse_search(ref, mov, ds.default_scales(sp), ds.default_angles(None), work_px=wp, top_k=40, sigma=1.0 if mode == "s1" else 2.0)
            ds._peak_stats = orig_peak
            rank = next((i for i, h in enumerate(hy) if abs(((h.angle - at + 180) % 360) - 180) <= 8 and abs(math.log(h.scale / st)) < 0.15), None)
            rows[mode] = rank
        print(n, "true s=%.2f a=%.0f" % (st, at), "work", wp, rows, flush=True)
