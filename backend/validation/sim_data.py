"""Sun-angle, TMC-2-like, IIRS-like, robustness and negative validation pairs.

Real TMC-2 and IIRS products are only distributed through ISSDC PRADAN (login
required), so those sensors are emulated from REAL lunar imagery of the same
ground acquired under a DIFFERENT Sun geometry than the reference:

* ``sun_*``   - real SELENE TC vs real SELENE TC, Sun azimuth 32-152 deg away
                (multi-temporal, sun-angle invariance on genuine data)
* ``tmc2_*``  - real high-resolution TC (3-5 m, other Sun) resampled to the
                TMC-2 5 m GSD with TMC-2-like MTF, noise and 10-bit quantisation,
                delivered as 16-bit PNG in a rotated "raw" frame
* ``iirs_*``  - real TC (other Sun) degraded to the IIRS 80 m GSD with a
                reflectance + thermal-emission band-mean, column striping and low
                SNR, delivered as float32 TIFF in a rotated frame
* ``rob_*``   - controlled perturbations of a real OHRC/TC pair (rotation, scale,
                noise, blur, gamma, contrast inversion, JPEG, partial overlap)
* ``neg_*``   - unrelated ground (must be rejected, never accepted)

All moving images are synthesised from a map-projected source with a known
pixel -> map transform, so ground truth is exact up to the uncontrolled
geolocation offset between two TC observations (tens of metres).

Usage:  python -m validation.sim_data      (from backend/)
"""
from __future__ import annotations

import json
import math
import urllib.request
from pathlib import Path

import cv2
import numpy as np
import rasterio
from pyproj import Transformer

from .real_data import (LL2SPS, MOON_LL, MOON_SPS, PAIRS_DIR, STAC, TC_COLLECTION, _stretch_u8,
                        _write_geotiff, read_tc_window)

COLLECTIONS = [TC_COLLECTION,
               "kaguya_terrain_camera_stereoscopic_uncontrolled_observations",
               "kaguya_terrain_camera_spsupport_uncontrolled_observations"]

# (lon, lat) of each test site and the TC observations used there.
SITES = {
    "L1": {"lonlat": (43.65, -74.0), "ref": "TC1S2B0_01_03482S746E0433",
           "sun": ["TC1W2B0_01_04817S739E0427", "TC1W2B0_01_00811S743E0434", "TC1S2B0_01_05828S744E0432",
                   "TC1S2B0_01_01814S742E0436"],
           "tmc2_src": "TC1S2B0_01_07045S744E0439", "iirs_src": "TC1W2B0_01_00811S743E0434"},
    "L2": {"lonlat": (42.7, -73.4), "ref": "TC1S2B0_01_03482S732E0433",
           "sun": ["TC1W2B0_01_04817S739E0427", "TC1W2B0_01_00812S730E0425", "TC1S2B0_01_05152S728E0422",
                   "TC1S2B0_01_01815S728E0427"],
           "tmc2_src": "TC1S2B0_01_05829S737E0422", "iirs_src": "TC1W2B0_01_04817S739E0427"},
    "L3": {"lonlat": (56.7, -62.2), "ref": "TC1S2B0_01_03470S619E0560",
           "sun": ["TC1W2B0_01_00800S618E0556", "TC2W2B0_01_02638S621E0562"],
           "tmc2_src": "TC2W2B0_01_07384S620E0562", "iirs_src": "TC1W2B0_01_00800S618E0556"},
}

_item_cache: dict = {}


def stac_item(item_id: str) -> dict:
    if item_id in _item_cache:
        return _item_cache[item_id]
    for col in COLLECTIONS:
        with urllib.request.urlopen(f"{STAC}?collections={col}&ids={item_id}", timeout=120) as r:
            feats = json.load(r)["features"]
        if feats:
            _item_cache[item_id] = feats[0]
            return feats[0]
    raise KeyError(item_id)


def read_window(item_id: str, cx: float, cy: float, half_m: float, gsd: float | None = None):
    """Square TC window centred on map point (cx, cy); resampled to `gsd` if given."""
    it = stac_item(item_id)
    href = it["assets"]["image"]["href"]
    arr, tr, _, nod = read_tc_window(href, (cx - half_m, cy - half_m, cx + half_m, cy + half_m))
    valid = arr != nod
    return arr.astype(np.float32), valid, tr, it["properties"]


def valid_centre(masks_trs, cx, cy, half_m, res_m):
    """Centre (map) and radius (m) of the largest disc valid in every (mask, transform)."""
    n = int(2 * half_m / res_m)
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float64)
    X = cx - half_m + (xx + 0.5) * res_m
    Y = cy + half_m - (yy + 0.5) * res_m
    ok = np.ones((n, n), bool)
    for m, tr in masks_trs:
        px, py = (~tr) * (X, Y)
        px, py = px.astype(int), py.astype(int)
        inside = (px >= 0) & (py >= 0) & (px < m.shape[1]) & (py < m.shape[0])
        v = np.zeros((n, n), bool)
        v[inside] = m[py[inside], px[inside]]
        ok &= v
    ok[0, :] = ok[-1, :] = ok[:, 0] = ok[:, -1] = False  # the window edge bounds the disc too
    dist = cv2.distanceTransform(ok.astype(np.uint8), cv2.DIST_L2, 5)
    iy, ix = np.unravel_index(int(np.argmax(dist)), dist.shape)
    return float(X[iy, ix]), float(Y[iy, ix]), float(dist[iy, ix]) * res_m


def synth_raw_frame(src: np.ndarray, src_valid: np.ndarray, src_tr, cx: float, cy: float, out_wh: tuple[int, int],
                    gsd_out: float, angle_deg: float, mtf_sigma_px: float):
    """Resample a map-projected source into a rotated sensor frame.

    Output pixel (u, v) looks at map point
        X = cx + g (cos a (u-u0) - sin a (v-v0)),  Y = cy - g (sin a (u-u0) + cos a (v-v0))
    Returns image, validity mask and the (u, v) -> (X, Y) function.
    """
    w, h = out_wh
    u0, v0 = (w - 1) / 2.0, (h - 1) / 2.0
    a = math.radians(angle_deg)
    gsd_src = abs(src_tr.a)
    # optical MTF + anti-aliasing: Gaussian in output pixels, applied at source resolution
    sig = math.hypot(max(0.0, 0.42 * gsd_out / gsd_src), mtf_sigma_px * gsd_out / gsd_src)
    fill = float(np.median(src[src_valid])) if src_valid.any() else 0.0
    sm = cv2.GaussianBlur(np.where(src_valid, src, fill).astype(np.float32), (0, 0), max(sig, 0.3))

    def to_map(u, v):
        du, dv = np.asarray(u, float) - u0, np.asarray(v, float) - v0
        return (cx + gsd_out * (math.cos(a) * du - math.sin(a) * dv),
                cy - gsd_out * (math.sin(a) * du + math.cos(a) * dv))

    vv, uu = np.mgrid[0:h, 0:w].astype(np.float64)
    X, Y = to_map(uu, vv)
    inv = ~src_tr
    sx, sy = inv * (X, Y)
    sx, sy = (sx - 0.5).astype(np.float32), (sy - 0.5).astype(np.float32)
    img = cv2.remap(sm, sx, sy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=np.nan)
    ok = cv2.remap(src_valid.astype(np.uint8), sx, sy, cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT, borderValue=0) > 0
    return img, ok & np.isfinite(img), to_map


def gt_grid(to_map, w: int, h: int, ref_tr, step: int) -> dict:
    vv, uu = np.mgrid[0:h:step, 0:w:step].astype(np.float64)
    X, Y = to_map(uu, vv)
    rx, ry = (~ref_tr) * (X, Y)
    return {"mov_pts": np.stack([uu.ravel(), vv.ravel()], 1).tolist(),
            "ref_pts": np.stack([rx.ravel() - 0.5, ry.ravel() - 0.5], 1).tolist()}


def _write_pair(name: str, ref_u8: np.ndarray, ref_gsd: float, ref_src: str, mov_file: str, mov_writer,
                mov_sensor: str, mov_gsd: float, mov_src: str, gt: dict, kind: str, category: str, extra: dict) -> None:
    d = PAIRS_DIR / name
    d.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(d / "ref_selene_tc.png"), ref_u8)
    mov_writer(d / mov_file)
    meta = {"name": name, "kind": kind, "category": category,
            "moving": {"sensor": mov_sensor, "file": mov_file, "geotiff": None, "gsd_m": round(mov_gsd, 3), "source": mov_src},
            "reference": {"sensor": "SELENE", "file": "ref_selene_tc.png", "geotiff": None, "gsd_m": round(ref_gsd, 3),
                          "source": ref_src},
            "max_bias_m": 300.0, "gt": gt}
    meta.update(extra)
    (d / "pair.json").write_text(json.dumps(meta))


def build_site(site: str) -> list[str]:
    cfg = SITES[site]
    cx, cy = LL2SPS.transform(*cfg["lonlat"])
    made = []
    ref_half = 6000.0
    ref, rv, rtr, rp = read_window(cfg["ref"], cx, cy, ref_half)
    if rv.mean() < 0.97:
        print(f"{site}: reference window incomplete ({rv.mean():.2f}), skipped")
        return made
    ref_u8 = _stretch_u8(ref, rv)
    ref_gsd = abs(rtr.a)
    ref_src = f"SELENE TC {cfg['ref']} {rp['datetime'][:10]} sun az {rp.get('view:sun_azimuth', 0):.0f} el {rp.get('view:sun_elevation', 0):.1f}"
    angles = [17.0, 63.0, 141.0, 205.0, 300.0]

    # --- real multi-temporal SELENE TC (sun-angle invariance) -------------------
    for k, sid in enumerate(cfg["sun"]):
        src, sv, stri, sp = read_window(sid, cx, cy, 6000.0)
        if sv.mean() < 0.9:
            print(f"{site}: {sid} coverage {sv.mean():.2f}, skipped")
            continue
        g = abs(stri.a)
        size = int(7000 / g)
        ang = angles[k % len(angles)]
        img, ok, to_map = synth_raw_frame(src, sv, stri, cx + 400, cy - 300, (size, size), g, ang, 0.0)
        if ok.mean() < 0.97:
            continue
        mov = _stretch_u8(np.nan_to_num(img), ok)
        daz = abs(((sp.get("view:sun_azimuth", 0) - rp.get("view:sun_azimuth", 0)) + 180) % 360 - 180)
        el = sp.get("view:sun_elevation", 0)
        name = f"sun_{site}_az{sp.get('view:sun_azimuth', 0):.0f}"
        _write_pair(name, ref_u8, ref_gsd, ref_src, "mov_selene_tc.png", lambda p, m=mov: cv2.imwrite(str(p), m),
                    "SELENE", g, f"SELENE TC {sid} {sp['datetime'][:10]} sun az {sp.get('view:sun_azimuth', 0):.0f} el {el:.1f}, rotated {ang} deg",
                    gt_grid(to_map, size, size, rtr, 16), "SELENE->SELENE (multi-temporal)",
                    "sun_extreme" if (daz > 120 or el < 3.0) else "sun_angle",
                    {"sun_azimuth_diff_deg": round(daz, 1), "moving_sun_elevation_deg": el, "applied_rotation_deg": ang})
        made.append(name)

    # --- TMC-2-like: 5 m, 10-bit, from a 3-5 m TC observation under a different Sun ---
    src, sv, stri, sp = read_window(cfg["tmc2_src"], cx, cy, 6000.0)
    mx, my, rad = valid_centre([(sv, stri), (rv, rtr)], cx, cy, 6000.0, 20.0)
    side = min(5000.0, 1.35 * rad)
    if side >= 2500.0:
        size = int(side / 5.0)
        img, ok, to_map = synth_raw_frame(src, sv, stri, mx, my, (size, size), 5.0, 38.0, 0.6)
        if ok.mean() > 0.97:
            rng = np.random.default_rng(26166)
            lo, hi = np.percentile(img[ok], [0.2, 99.8])
            dn = (np.nan_to_num(img) - lo) / max(hi - lo, 1e-6) * 900.0 + 40.0
            dn = dn + rng.normal(0, 1, dn.shape) * np.sqrt(2.0 ** 2 + 0.01 * np.maximum(dn, 0))  # read + shot noise
            dn = np.clip(np.round(dn), 0, 1023).astype(np.uint16)
            name = f"tmc2sim_{site}"
            _write_pair(name, ref_u8, ref_gsd, ref_src, "mov_tmc2sim.png", lambda p, m=dn: cv2.imwrite(str(p), m),
                        "TMC2", 5.0, f"TMC-2 emulation from TC {cfg['tmc2_src']} ({sp['datetime'][:10]}, sun az {sp.get('view:sun_azimuth', 0):.0f}, {abs(stri.a):.1f} m) -> 5 m, 10-bit, {size}x{size} px, rotated 38 deg",
                        gt_grid(to_map, size, size, rtr, 16), "TMC2(sim)->SELENE", "sensor_sim",
                        {"applied_rotation_deg": 38.0})
            made.append(name)
        else:
            print(f"{site}: TMC-2 frame coverage {ok.mean():.2f}, skipped")
    else:
        print(f"{site}: TMC-2 source overlap too small ({side:.0f} m), skipped")

    # --- IIRS-like: 80 m band-mean with thermal emission, striping, low SNR --------
    ref2, rv2, rtr2, _ = read_window(cfg["ref"], cx, cy, 14000.0)
    src, sv, stri, sp = read_window(cfg["iirs_src"], cx, cy, 14000.0)
    mx, my, rad = valid_centre([(sv, stri), (rv2, rtr2)], cx, cy, 14000.0, 50.0)
    side = min(15000.0, 1.35 * rad)
    if side >= 8000.0:
        size = int(side / 80.0)
        img, ok, to_map = synth_raw_frame(src, sv, stri, mx, my, (size, size), 80.0, 112.0, 0.7)
        if ok.mean() > 0.95:
            rng = np.random.default_rng(26166)
            r = np.nan_to_num(img)
            lo, hi = np.percentile(r[ok], [1, 99])
            r = np.clip((r - lo) / max(hi - lo, 1e-6), 0, None)
            thermal = cv2.GaussianBlur(r ** 1.5, (0, 0), 0.8)  # emission from sun-facing slopes
            band_mean = 0.55 * r + 0.45 * thermal
            band_mean *= 1.0 + 0.02 * rng.standard_normal(size)[None, :]  # pushbroom detector striping
            band_mean += rng.normal(0, 0.02, band_mean.shape)
            rad_img = (band_mean * 6.0).astype(np.float32)  # W m-2 sr-1 um-1 scale
            # reference: the TC window around the IIRS footprint (where TC data is valid)
            ref2_u8 = _stretch_u8(ref2, rv2)
            name = f"iirssim_{site}"

            def write_tif(p, m=rad_img):
                with rasterio.open(p, "w", driver="GTiff", width=m.shape[1], height=m.shape[0], count=1,
                                   dtype="float32") as dst:
                    dst.write(m, 1)
            _write_pair(name, ref2_u8, abs(rtr2.a), ref_src.replace("SELENE TC", "SELENE TC (28 km window)"),
                        "mov_iirssim.tif", write_tif, "IIRS", 80.0,
                        f"IIRS emulation from TC {cfg['iirs_src']} ({sp['datetime'][:10]}, sun az {sp.get('view:sun_azimuth', 0):.0f}) -> 80 m band-mean + thermal, {size}x{size} px, rotated 112 deg",
                        gt_grid(to_map, size, size, rtr2, 4), "IIRS(sim)->SELENE", "sensor_sim",
                        {"applied_rotation_deg": 112.0, "tol_px": 6.0})
            made.append(name)
        else:
            print(f"{site}: IIRS frame coverage {ok.mean():.2f}, skipped")
    else:
        print(f"{site}: IIRS overlap too small ({side:.0f} m), skipped")
    return made


# ---------------------------------------------------------------------------
# Robustness sweep on a real OHRC/TC pair and negatives
# ---------------------------------------------------------------------------

def build_robustness(base: str = "ohrc_tc_s2_b") -> list[str]:
    src_dir = PAIRS_DIR / base
    meta = json.loads((src_dir / "pair.json").read_text())
    mov = cv2.imread(str(src_dir / "mov_ohrc.png"), cv2.IMREAD_GRAYSCALE)
    ref = cv2.imread(str(src_dir / "ref_selene_tc.png"), cv2.IMREAD_GRAYSCALE)
    rng = np.random.default_rng(26166)
    h, w = mov.shape
    made = []

    def warp_case(name, A, out_wh, post=None, note=""):
        """A: 3x3 map from ORIGINAL moving px to NEW moving px."""
        new = cv2.warpPerspective(mov, A, out_wh, flags=cv2.INTER_AREA if abs(np.linalg.det(A[:2, :2])) < 1 else cv2.INTER_LINEAR,
                                  borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        if post is not None:
            new = post(new)
        mp = np.asarray(meta["gt"]["mov_pts"], np.float64).reshape(-1, 1, 2)
        newp = cv2.perspectiveTransform(mp, A).reshape(-1, 2)
        keep = (newp[:, 0] >= 0) & (newp[:, 1] >= 0) & (newp[:, 0] < out_wh[0]) & (newp[:, 1] < out_wh[1])
        gt = {"mov_pts": newp[keep].tolist(), "ref_pts": np.asarray(meta["gt"]["ref_pts"])[keep].tolist()}
        d = PAIRS_DIR / f"rob_{name}"
        d.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(d / "mov_ohrc.png"), new)
        cv2.imwrite(str(d / "ref_selene_tc.png"), ref)
        s = math.sqrt(abs(np.linalg.det(A[:2, :2])))
        m2 = {"name": d.name, "kind": "OHRC->SELENE_TC (perturbed)", "category": "robustness", "perturbation": note,
              "moving": dict(meta["moving"], gsd_m=round(meta["moving"]["gsd_m"] / s, 3)),
              "reference": meta["reference"], "gt": gt}
        (d / "pair.json").write_text(json.dumps(m2))
        made.append(d.name)

    def rot(deg, scale=1.0):
        M, (nh, nw) = _rot_canvas((h, w), deg, scale)
        return np.vstack([M, [0, 0, 1]]), (nw, nh)

    for deg in (45, 90, 180, 270):
        A, wh = rot(deg)
        warp_case(f"rot{deg}", A, wh, note=f"extra rotation {deg} deg")
    for sc in (0.5, 0.35):
        A, wh = rot(0, sc)
        warp_case(f"scale{sc}", A, wh, note=f"moving downscaled x{sc} (resolution gap x{0.26 / sc / 0.26:.1f} more)")
    I3 = np.eye(3)
    warp_case("noise20", I3, (w, h), post=lambda x: np.clip(x + rng.normal(0, 20, x.shape), 0, 255).astype(np.uint8), note="Gaussian noise sigma 20 DN")
    warp_case("blur3", I3, (w, h), post=lambda x: cv2.GaussianBlur(x, (0, 0), 3), note="Gaussian blur sigma 3 px")
    warp_case("gamma2", I3, (w, h), post=lambda x: (255 * (x / 255.0) ** 2.0).astype(np.uint8), note="gamma 2.0")
    warp_case("invert", I3, (w, h), post=lambda x: (255 - x).astype(np.uint8), note="contrast inversion (polarity flip)")
    warp_case("jpeg15", I3, (w, h), post=lambda x: cv2.imdecode(cv2.imencode(".jpg", x, [cv2.IMWRITE_JPEG_QUALITY, 15])[1], 0), note="JPEG quality 15")
    T = np.array([[1, 0, -w * 0.45], [0, 1, 0], [0, 0, 1]], float)
    warp_case("partial55", T, (int(w * 0.55), h), note="moving cropped to 55 % width (partial overlap)")
    A, wh = rot(130, 0.6)
    warp_case("combo", A, wh, post=lambda x: np.clip(cv2.GaussianBlur(x, (0, 0), 1.0) + rng.normal(0, 10, x.shape), 0, 255).astype(np.uint8),
              note="rotation 130 deg + scale 0.6 + blur + noise")
    return made


def _rot_canvas(shape, deg, scale):
    h, w = shape
    M = cv2.getRotationMatrix2D((w / 2.0, h / 2.0), deg, scale)
    c, s = abs(M[0, 0]), abs(M[0, 1])
    nw, nh = int(math.ceil(h * s + w * c)), int(math.ceil(h * c + w * s))
    M[0, 2] += nw / 2.0 - w / 2.0
    M[1, 2] += nh / 2.0 - h / 2.0
    return M, (nh, nw)


def build_negatives() -> list[str]:
    made = []
    plan = [("ohrc_tc_s1_a", "ohrc_tc_s3_a", "neg_ohrc_s1_vs_tc_s3"),
            ("ohrc_tc_s3_b", "ohrc_tc_s2_a", "neg_ohrc_s3_vs_tc_s2"),
            ("ohrc_tc_s2_b", "ohrc_tc_s1_b", "neg_ohrc_s2_vs_tc_s1")]
    for mov_pair, ref_pair, name in plan:
        mm = json.loads((PAIRS_DIR / mov_pair / "pair.json").read_text())
        rm = json.loads((PAIRS_DIR / ref_pair / "pair.json").read_text())
        d = PAIRS_DIR / name
        d.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(d / "mov_ohrc.png"), cv2.imread(str(PAIRS_DIR / mov_pair / "mov_ohrc.png"), 0))
        cv2.imwrite(str(d / "ref_selene_tc.png"), cv2.imread(str(PAIRS_DIR / ref_pair / "ref_selene_tc.png"), 0))
        meta = {"name": name, "kind": "unrelated ground", "category": "negative", "expect_fail": True,
                "moving": mm["moving"], "reference": rm["reference"], "gt": None}
        (d / "pair.json").write_text(json.dumps(meta))
        made.append(name)
    # synthetic: featureless and pure-noise moving images against a real reference
    for nm, img in (("neg_flat", np.full((800, 800), 120, np.uint8)),
                    ("neg_noise", np.random.default_rng(1).integers(0, 255, (800, 800)).astype(np.uint8))):
        d = PAIRS_DIR / nm
        d.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(d / "mov_ohrc.png"), img)
        cv2.imwrite(str(d / "ref_selene_tc.png"), cv2.imread(str(PAIRS_DIR / "ohrc_tc_s2_b" / "ref_selene_tc.png"), 0))
        rm = json.loads((PAIRS_DIR / "ohrc_tc_s2_b" / "pair.json").read_text())
        meta = {"name": nm, "kind": "synthetic non-lunar", "category": "negative", "expect_fail": True,
                "moving": {"sensor": "OHRC", "file": "mov_ohrc.png", "gsd_m": 2.6}, "reference": rm["reference"], "gt": None}
        (d / "pair.json").write_text(json.dumps(meta))
        made.append(nm)
    return made


if __name__ == "__main__":
    import sys
    only = sys.argv[1:] or ["sites", "robustness", "negatives"]
    for site in (SITES if "sites" in only else []):
        try:
            print(site, build_site(site), flush=True)
        except Exception as exc:
            print(site, "failed:", type(exc).__name__, exc, flush=True)
    if "robustness" in only:
        print("robustness", build_robustness(), flush=True)
    if "negatives" in only:
        print("negatives", build_negatives(), flush=True)
