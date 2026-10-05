"""Does a second, higher-resolution scoring pass promote the true coarse pose?"""
import json
import math
import sys
import time
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, ".")
from app.vision import dense_structural as ds  # noqa: E402
from validation.diag.coarse_rank import gt_pose  # noqa: E402

pairs = sys.argv[1].split(",")
for n in pairs:
    P = Path("data/real/pairs") / n
    d = json.loads((P / "pair.json").read_text())
    st, at = gt_pose(d)
    mov = ds._to_float(cv2.imread(str(P / d["moving"]["file"]), cv2.IMREAD_UNCHANGED))
    ref = ds._to_float(cv2.imread(str(P / d["reference"]["file"]), cv2.IMREAD_UNCHANGED))
    sp = d["moving"]["gsd_m"] / d["reference"]["gsd_m"]
    t = time.perf_counter()
    hy = ds.coarse_search(ref, mov, ds.default_scales(sp), ds.default_angles(None), top_k=40)

    def is_true(h):
        return abs(((h.angle - at + 180) % 360) - 180) <= 8 and abs(math.log(h.scale / st)) < 0.15
    r0 = next((i for i, h in enumerate(hy) if is_true(h)), None)
    for wp, sig in ((480, 1.0), (480, 2.0), (640, 1.5)):
        t1 = time.perf_counter()
        scored = []
        for h in hy:
            b = ds.coarse_search(ref, mov, [h.scale * 2 ** (k / 8) for k in (-1, 0, 1)],
                                 [h.angle - 5, h.angle, h.angle + 5], work_px=wp, sigma=sig)
            if b is not None:
                scored.append(b)
        scored.sort(key=lambda h: -h.distinct)
        r1 = next((i for i, h in enumerate(scored) if is_true(h)), None)
        print(n, "true s=%.2f a=%.0f" % (st, at), "rank@240", r0, f"rank@{wp}/s{sig}", r1,
              "top", [(round(h.scale, 2), round(h.angle), round(h.distinct, 3)) for h in scored[:2]],
              "%.1fs" % (time.perf_counter() - t1), flush=True)
