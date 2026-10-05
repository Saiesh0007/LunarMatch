"""Score the LunarMatch pipeline on real and simulated lunar pairs with ground truth.

For each pair directory (``data/real/pairs/<name>/pair.json``) the pipeline is run
in-process and the returned transformation (moving -> reference) is evaluated
against the archive-derived ground-truth correspondence grid.

Reported per run:
  status           pipeline decision (SUCCESSFUL / LOW_CONFIDENCE / NOT_RELIABLE / FAILED)
  inliers, rmse    as reported by the pipeline
  gt_med / gt_p90  checkpoint error of the estimated transform vs ground truth [ref px]
  gt_bias_rm       median checkpoint error after removing the constant offset
                   (absolute geolocation bias between two uncontrolled archives)
  verdict          CORRECT if gt_bias_rm <= tol and bias <= max_bias, else WRONG;
                   a NOT_RELIABLE/FAILED result is a SAFE_REJECT (no false positive),
                   a SUCCESSFUL result with a WRONG transform is a FALSE_ACCEPT.

Usage (from backend/):
    python -m validation.run_validation [--pairs name1,name2] [--methods rift2,sift]
"""
from __future__ import annotations

import argparse
import json
import time
import traceback
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PAIRS_DIR = ROOT / "data" / "real" / "pairs"
REPORT_DIR = ROOT / "data" / "real" / "reports"

SENSOR_ENUM = {"OHRC": "OHRC", "SELENE": "SELENE", "LRO_NAC": "LRO NAC", "TMC2": "TMC-2", "IIRS": "IIRS"}

METHOD_PRESETS = {
    "rift2": dict(feature_method="rift2", matcher="BF"),
    "rift2_multiscale": dict(feature_method="rift2_multiscale", matcher="BF"),
    "sift": dict(feature_method="sift", matcher="BF"),
    "hopc": dict(feature_method="hopc", matcher="BF"),
    "hopc_rift2_fusion": dict(feature_method="hopc_rift2_fusion", matcher="BF"),
    "superpoint_lightglue": dict(feature_method="superpoint", matcher="lightglue"),
    "superpoint_superglue": dict(feature_method="superpoint", matcher="superglue"),
    "dense": dict(feature_method="dense", matcher="BF"),
}


def gt_errors(matrix, gt: dict) -> dict:
    mov = np.asarray(gt["mov_pts"], dtype=np.float64)
    ref = np.asarray(gt["ref_pts"], dtype=np.float64)
    H = np.asarray(matrix, dtype=np.float64)
    if H.shape == (2, 3):
        H = np.vstack([H, [0, 0, 1]])
    proj = cv2.perspectiveTransform(mov.reshape(-1, 1, 2), H).reshape(-1, 2)
    d = proj - ref
    err = np.linalg.norm(d, axis=1)
    bias = np.median(d, axis=0)
    err_rm = np.linalg.norm(d - bias, axis=1)
    return {
        "gt_med": float(np.median(err)), "gt_p90": float(np.percentile(err, 90)),
        "gt_bias_px": [float(bias[0]), float(bias[1])], "gt_bias_norm": float(np.linalg.norm(bias)),
        "gt_bias_rm_med": float(np.median(err_rm)), "gt_bias_rm_p90": float(np.percentile(err_rm, 90)),
    }


def geo_mode_gt(run_dir: Path, meta: dict, pair_dir: Path):
    """Ground truth for georeferenced runs.

    The pipeline reprojects both GeoTIFFs to a common polar-stereographic grid and
    GSD, so the matrix it returns lives in those resampled pixel grids. Both grids
    share one CRS, so the true moving->reference map is the composition of the two
    affine geotransforms; checkpoints are taken where the moving raster is valid.
    """
    import rasterio
    ref_p = next((run_dir / n for n in ("ref_gsd.tif", "ref_crs.tif") if (run_dir / n).exists()), None)
    mov_p = next((run_dir / n for n in ("mov_gsd.tif", "mov_crs.tif") if (run_dir / n).exists()), None)
    if ref_p is None or mov_p is None:
        return None, None
    with rasterio.open(ref_p) as r, rasterio.open(mov_p) as m:
        rtr, mtr = r.transform, m.transform
        mov = m.read(1)
        nod = m.nodata
    valid = mov != (nod if nod is not None else 0)
    ys, xs = np.nonzero(valid[::8, ::8])
    xs, ys = xs * 8.0, ys * 8.0
    mx, my = mtr * (xs + 0.5, ys + 0.5)
    rx, ry = (~rtr) * (mx, my)
    gt = {"mov_pts": np.stack([xs, ys], 1).tolist(), "ref_pts": np.stack([rx - 0.5, ry - 0.5], 1).tolist()}
    return gt, abs(rtr.a)


def run_one(pair_dir: Path, method: str, mode: str = "raw", extra: dict | None = None, gsd: bool = True) -> dict:
    from app.models.requests import PipelineRunRequest
    from app.services.pipeline_service import PipelineService

    meta = json.loads((pair_dir / "pair.json").read_text())
    if mode == "raw":
        ref_file, mov_file = meta["reference"]["file"], meta["moving"]["file"]
    else:
        ref_file, mov_file = meta["reference"]["geotiff"], meta["moving"]["geotiff"]
    req_kw = dict(
        reference_image_id=str(pair_dir / ref_file),
        moving_image_id=str(pair_dir / mov_file),
        reference_sensor=SENSOR_ENUM.get(meta["reference"]["sensor"], "Other"),
        moving_sensor=SENSOR_ENUM.get(meta["moving"]["sensor"], "Other"),
        geometric_model="homography",
        estimator_method="magsac",
        **METHOD_PRESETS[method],
    )
    if gsd and mode == "raw":
        # operator-supplied nominal GSDs (what a user would type from the product label)
        req_kw["reference_gsd_m"] = meta["reference"]["gsd_m"]
        req_kw["moving_gsd_m"] = meta["moving"]["gsd_m"]
    req_kw.update(extra or {})
    req = PipelineRunRequest(**req_kw)
    t0 = time.perf_counter()
    try:
        res = PipelineService().execute_pipeline(req)
    except Exception as exc:  # noqa: BLE001 - a crash is a finding, record it
        return {"pair": pair_dir.name, "method": method, "mode": mode, "status": "CRASH",
                "error": f"{type(exc).__name__}: {exc}", "trace": traceback.format_exc()[-2000:],
                "wall_s": time.perf_counter() - t0}
    wall = time.perf_counter() - t0
    out = {
        "pair": pair_dir.name, "method": method, "mode": mode, "kind": meta["kind"], "gsd_prior": gsd,
        "status": res.status.value, "inliers": res.metrics.ransac_inliers,
        "filtered": res.metrics.filtered_matches, "rmse_px": res.metrics.rmse_px,
        "coverage": res.metrics.spatial_coverage, "confidence": res.metrics.confidence_level.value,
        "failure_reason": res.failure_reason, "run_id": res.run_id, "wall_s": round(wall, 1),
    }
    if mode == "raw":
        gt, ref_gsd = meta.get("gt"), meta["reference"]["gsd_m"]
    else:
        gt, ref_gsd = geo_mode_gt(Path(res.outputs.artifacts_dir), meta, pair_dir)
    tol_px = meta.get("tol_px", 3.0)
    max_bias_px = meta.get("max_bias_m", 300.0) / ref_gsd if ref_gsd else 1e9
    if res.transformation_matrix is not None and gt is not None:
        e = gt_errors(res.transformation_matrix, gt)
        out.update(e)
        out["gt_bias_m"] = e["gt_bias_norm"] * ref_gsd if ref_gsd else None
        correct = e["gt_bias_rm_med"] <= tol_px and e["gt_bias_norm"] <= max_bias_px
        out["transform_correct"] = bool(correct)
    else:
        out["transform_correct"] = None
    accepted = out["status"] in ("SUCCESSFUL", "LOW_CONFIDENCE")
    if meta.get("expect_fail"):
        out["verdict"] = "FALSE_ACCEPT" if accepted else "CORRECT_REJECT"
    elif accepted:
        out["verdict"] = "CORRECT" if out["transform_correct"] else "FALSE_ACCEPT"
    else:
        out["verdict"] = "SAFE_REJECT" if not out["transform_correct"] else "MISSED_ACCEPT"
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", default="")
    ap.add_argument("--methods", default="rift2")
    ap.add_argument("--mode", default="raw", choices=["raw", "geo"])
    ap.add_argument("--tag", default="run")
    ap.add_argument("--no-gsd", action="store_true", help="do not pass GSD priors (blind scale search)")
    ap.add_argument("--extra", default="", help="JSON dict of extra request fields")
    args = ap.parse_args()
    names = [p for p in args.pairs.split(",") if p] or sorted(p.name for p in PAIRS_DIR.iterdir() if (p / "pair.json").exists())
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    for name in names:
        for method in args.methods.split(","):
            r = run_one(PAIRS_DIR / name, method, args.mode, extra=json.loads(args.extra) if args.extra else None,
                        gsd=not args.no_gsd)
            results.append(r)
            print(json.dumps({k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()
                              if k not in ("trace",)}), flush=True)
    out = REPORT_DIR / f"{args.tag}.json"
    out.write_text(json.dumps(results, indent=1))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
