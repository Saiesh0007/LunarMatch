"""Quick standalone check of register_dense on pair directories (no pipeline overhead).

    python validation/diag/dense_pairs.py [gsd|none] [glob]
"""
import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, ".")
from app.vision.dense_structural import register_dense  # noqa: E402
from validation.run_validation import gt_errors  # noqa: E402

prior = sys.argv[1] if len(sys.argv) > 1 else "gsd"
pattern = sys.argv[2] if len(sys.argv) > 2 else "ohrc_tc_*"
for P in sorted(Path("data/real/pairs").glob(pattern)):
    d = json.loads((P / "pair.json").read_text())
    mov = cv2.imread(str(P / d["moving"]["file"]), cv2.IMREAD_UNCHANGED)
    ref = cv2.imread(str(P / d["reference"]["file"]), cv2.IMREAD_UNCHANGED)
    sp = d["moving"]["gsd_m"] / d["reference"]["gsd_m"] if prior == "gsd" else None
    t = time.perf_counter()
    r = register_dense(ref, mov, scale_prior=sp)
    dt = time.perf_counter() - t
    if r.H is None:
        print(P.name, d.get("category", ""), "FAIL", r.diagnostics.get("failure_reason"), "%.1fs" % dt, flush=True)
        continue
    if not d.get("gt"):
        print(P.name, d.get("category", ""), "ACCEPTED (no GT)", int(r.inlier_mask.sum()), "%.1fs" % dt, flush=True)
        continue
    e = gt_errors(r.H, d["gt"])
    print(P.name, d.get("category", ""), "inl", int(r.inlier_mask.sum()), "/", len(r.matches),
          "rmse %.2f" % r.diagnostics["inlier_rmse_px"],
          "gt_med %.1f bias %s rm_med %.2f p90 %.2f" % (e["gt_med"], np.round(e["gt_bias_px"], 1).tolist(),
                                                      e["gt_bias_rm_med"], e["gt_bias_rm_p90"]),
          "coarse s=%s a=%s" % (r.diagnostics.get("coarse_scale"), r.diagnostics.get("coarse_angle_deg")),
          "%.1fs" % dt, flush=True)
