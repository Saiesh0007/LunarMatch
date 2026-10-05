"""LRO NAC reference pairs for the real-data validation set.

For every OHRC crop already paired with SELENE TC (see ``real_data.py``) this
downloads only the needed lines of a calibrated LRO NAC CDR (HTTP range request
on the PDS LROC node), geolocates them from the PDS index footprint (four
corners + centre; no SPICE kernels needed) and writes an OHRC -> NAC pair with a
ground-truth correspondence grid.

The NAC index does not say which labelled corner is pixel (0, 0) for a given
flight direction / NAC-L vs NAC-R, so all four orientation hypotheses are tested
against the (map-projected) TC window and the most distinctive one is kept.

Usage:  python -m validation.nac_data      (from backend/)
"""
from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

import cv2
import numpy as np
import rasterio

from .real_data import (DATA, LL2SPS, OHRC_DIR, OHRC_STRIPS, PAIRS_DIR, OhrcGeometry,
                        _poly_terms, _stretch_u8)

NAC_DIR = DATA / "nac"
STRIP_TAG = {"20200229T0739312111": "s1", "20200229T0938004033": "s2", "20200824T1003365280": "s3"}

NAC_PLAN = [
    # (existing OHRC/TC pair, NAC product, output pair name)
    # Illumination-matched references: Sun direction relative to north (LROC
    # SUB_SOLAR_AZIMUTH - NORTH_AZIMUTH) of 59-86 deg, i.e. lit from the same side
    # as the OHRC / TC scenes - the reference an analyst would pick.
    ("ohrc_tc_s1_a", "M1369217819LC", "ohrc_nac_s1_a"),
    ("ohrc_tc_s1_b", "M1399738578LC", "ohrc_nac_s1_b"),
    ("ohrc_tc_s2_a", "M1381929802RC", "ohrc_nac_s2_a"),
    ("ohrc_tc_s2_b", "M1524860933LC", "ohrc_nac_s2_b"),
    ("ohrc_tc_s3_b", "M1514476994RC", "ohrc_nac_s3_b"),
    # Stress set: Sun azimuth 75-120 deg away from the OHRC scene (shadows on
    # opposite crater walls). Expected outcome is a safe rejection, not a match.
    ("ohrc_tc_s1_a", "M1258744166LC", "ohrc_nac_sunx_s1_a"),
    ("ohrc_tc_s1_b", "M1434937384RC", "ohrc_nac_sunx_s1_b"),
    ("ohrc_tc_s2_a", "M1412426148LC", "ohrc_nac_sunx_s2_a"),
    ("ohrc_tc_s2_b", "M1488856381RC", "ohrc_nac_sunx_s2_b"),
]


def parse_nac_index(p: dict) -> dict:
    """Parse the LROC cumulative-index record ODE attaches to a product."""
    rec = next(n for n in p["ODE_notes"]["ODE_note"] if n.startswith('"'))
    f = [x.strip().strip('"').strip() for x in rec.split(",")]
    # tail: LINES SAMPLES BITS RES RES RES EMI INC PHASE NORTH_AZ SUBSOLAR_AZ SS_LAT SS_LON SC_LAT SC_LON
    #       SOLAR_DIST SOLAR_LON C_LAT C_LON UR_LAT UR_LON LR_LAT LR_LON LL_LAT LL_LON UL_LAT UL_LON ALT DIST NODE DIR
    v = [float(x) for x in f[-31:-4]]
    return {
        "lines": int(v[0]), "samples": int(v[1]), "res": v[5], "emission": v[6], "incidence": v[7],
        "subsolar_az": v[10], "center": (v[18], v[17]),
        "UR": (v[20], v[19]), "LR": (v[22], v[21]), "LL": (v[24], v[23]), "UL": (v[26], v[25]),
    }


class NacGeometry:
    """Approximate NAC (line, sample) -> south polar stereographic metres.

    Bilinear between the corners plus a quadratic along-track term through the
    image centre. ``flip_line``/``flip_samp`` choose which corner is pixel (0, 0).
    """

    def __init__(self, idx: dict, flip_line: bool, flip_samp: bool):
        self.L, self.S = idx["lines"], idx["samples"]
        P = {k: np.array(LL2SPS.transform(*idx[k])) for k in ("UL", "UR", "LL", "LR", "center")}
        top, bot = (("LL", "LR"), ("UL", "UR")) if flip_line else (("UL", "UR"), ("LL", "LR"))
        if flip_samp:
            top, bot = top[::-1], bot[::-1]
        self.p00, self.p01 = P[top[0]], P[top[1]]
        self.p10, self.p11 = P[bot[0]], P[bot[1]]
        self.qc = P["center"] - self._bil(np.array(0.5), np.array(0.5))

    def _bil(self, v, u):
        v, u = np.asarray(v)[..., None], np.asarray(u)[..., None]
        return (1 - v) * ((1 - u) * self.p00 + u * self.p01) + v * ((1 - u) * self.p10 + u * self.p11)

    def to_map(self, line, samp):
        v = np.asarray(line, float) / (self.L - 1)
        u = np.asarray(samp, float) / (self.S - 1)
        p = self._bil(v, u) + (4 * v * (1 - v))[..., None] * self.qc
        return p[..., 0], p[..., 1]

    def fit_inverse(self, l0: int, l1: int):
        ll, ss = np.mgrid[l0:l1:64j, 0:self.S - 1:24j]
        x, y = self.to_map(ll, ss)
        cx, cy = x.mean(), y.mean()
        A = _poly_terms(x.ravel(), y.ravel())
        cl, *_ = np.linalg.lstsq(A, ll.ravel(), rcond=None)
        cs, *_ = np.linalg.lstsq(A, ss.ravel(), rcond=None)

        def inv(mx, my):
            xs = (np.asarray(mx, float) - cx) / 1000.0
            ys = (np.asarray(my, float) - cy) / 1000.0
            B = np.stack([np.ones_like(xs), xs, ys, xs * xs, xs * ys, ys * ys,
                          xs ** 3, xs * xs * ys, xs * ys * ys, ys ** 3], -1)
            return B @ cl, B @ cs
        return inv


def fetch_nac_lines(label_url: str, l0: int, l1: int, samples: int, cache: Path) -> np.ndarray:
    """Range-download lines l0..l1 of a NAC CDR (SignedLSB2, no header offset)."""
    if cache.exists():
        return np.load(cache)
    img_url = re.sub(r"\.xml$", ".IMG", label_url, flags=re.I)
    start, end = l0 * samples * 2, (l1 + 1) * samples * 2 - 1
    req = urllib.request.Request(img_url, headers={"Range": f"bytes={start}-{end}"})
    with urllib.request.urlopen(req, timeout=1800) as r:
        buf = r.read()
    arr = np.frombuffer(buf, dtype="<i2").reshape(-1, samples)
    cache.parent.mkdir(parents=True, exist_ok=True)
    np.save(cache, arr)
    return arr


def _struct(x: np.ndarray) -> np.ndarray:
    x = cv2.GaussianBlur(x.astype(np.float32), (0, 0), 1.5)
    return np.hypot(cv2.Sobel(x, cv2.CV_32F, 1, 0), cv2.Sobel(x, cv2.CV_32F, 0, 1))


def _orientation_score(tc: np.ndarray, nac_on_tc: np.ndarray) -> tuple[float, tuple[int, int]]:
    ok = np.isfinite(nac_on_tc)
    if ok.mean() < 0.2:
        return -1.0, (0, 0)
    rows, cols = np.nonzero(ok)
    r0, r1, c0, c1 = rows.min(), rows.max(), cols.min(), cols.max()
    sub = np.nan_to_num(nac_on_tc[r0:r1, c0:c1], nan=float(np.nanmean(nac_on_tc)))
    A, B = _struct(tc[r0:r1, c0:c1]), _struct(sub)
    m = max(8, min(B.shape) // 4)
    T = B[m:-m, m:-m]
    if min(T.shape) < 16:
        return -1.0, (0, 0)
    res = cv2.matchTemplate(A, T, cv2.TM_CCOEFF_NORMED)
    _, p1, _, loc = cv2.minMaxLoc(res)
    r2 = res.copy()
    cv2.circle(r2, loc, 6, -1, -1)
    return p1 - float(r2.max()), (loc[0] - m, loc[1] - m)


def build_ohrc_nac_pair(tc_pair: str, nac_name: str, out_name: str, bin_to_m: float = 1.6, margin_m: float = 400.0) -> dict:
    tc_dir = PAIRS_DIR / tc_pair
    tmeta = json.loads((tc_dir / "pair.json").read_text())
    sid = next(k for k in OHRC_STRIPS if k in tmeta["moving"]["source"])
    by0 = int(tmeta["moving"]["source"].split("rows ")[1].split("-")[0])
    prods = json.loads((NAC_DIR / f"ode_{STRIP_TAG[sid]}.json").read_text())["ODEResults"]["Products"]["Product"]
    p = next(x for x in prods if x["Product_name"].startswith(nac_name))
    idx = parse_nac_index(p)

    geo = OhrcGeometry.load(sid)
    brw = cv2.imread(str(OHRC_DIR / f"{sid}_brw.png"), cv2.IMREAD_GRAYSCALE)
    crop_h, w = tmeta["moving"]["shape"]
    gy, gx = np.mgrid[by0:by0 + crop_h:32, 0:w:32].astype(np.float64)
    mx, my = geo.browse_to_map(gx, gy)

    # each orientation hypothesis needs its own (small) line range of the CDR
    hyps = []
    ll, ss = np.mgrid[0:idx["lines"]:128, 0:idx["samples"]:64].astype(float)
    for fl in (False, True):
        for fs in (False, True):
            ng = NacGeometry(idx, fl, fs)
            nx, ny = ng.to_map(ll, ss)
            inside = ((nx > mx.min() - margin_m) & (nx < mx.max() + margin_m)
                      & (ny > my.min() - margin_m) & (ny < my.max() + margin_m))
            if inside.any():
                l0 = int(max(ll[inside].min() - 256, 0))
                l1 = int(min(ll[inside].max() + 256, idx["lines"] - 1))
                if l1 - l0 <= 12000:  # a plausible crop spans a few km, not the whole strip
                    hyps.append((fl, fs, l0, l1))
    if not hyps:
        raise RuntimeError(f"NAC {nac_name} does not cover {tc_pair}")

    with rasterio.open(tc_dir / "ref_selene_tc.tif") as ds:
        tc = ds.read(1).astype(np.float32)
        tc_tr = ds.transform
    ty, tx = np.mgrid[0:tc.shape[0], 0:tc.shape[1]].astype(np.float64)
    TX, TY = tc_tr * (tx + 0.5, ty + 0.5)
    k_tc = max(1.0, abs(tc_tr.a) / idx["res"])
    chunks = {}
    scores = []
    for fl, fs, l0, l1 in hyps:
        if (l0, l1) not in chunks:
            raw = fetch_nac_lines(p["LabelURL"], l0, l1, idx["samples"], NAC_DIR / f"{nac_name}_{l0}_{l1}.npy")
            valid = raw != -32768
            f = np.where(valid, raw.astype(np.float32), np.nan)
            # pre-smooth NAC to TC resolution before point sampling
            f_s = cv2.GaussianBlur(np.nan_to_num(f, nan=float(np.nanmean(f))), (0, 0), 0.5 * k_tc)
            f_s[~valid] = np.nan
            chunks[(l0, l1)] = (f, f_s)
        f, f_s = chunks[(l0, l1)]
        inv = NacGeometry(idx, fl, fs).fit_inverse(l0, l1)
        lq, sq = inv(TX, TY)
        samp = cv2.remap(f_s, sq.astype(np.float32), (lq - l0).astype(np.float32), cv2.INTER_LINEAR,
                         borderMode=cv2.BORDER_CONSTANT, borderValue=np.nan)
        d, off = _orientation_score(tc, samp)
        scores.append((d, fl, fs, off, l0, l1))
    scores.sort(key=lambda t: -t[0])
    dist, fl, fs, off_tc, L0, L1 = scores[0]
    f = chunks[(L0, L1)][0]
    inv = NacGeometry(idx, fl, fs).fit_inverse(L0, L1)

    lq, sq = inv(mx, my)
    pad = margin_m / idx["res"]
    a0, a1 = int(max(lq.min() - pad, L0)), int(min(lq.max() + pad, L1))
    s0, s1 = int(max(sq.min() - pad, 0)), int(min(sq.max() + pad, idx["samples"] - 1))
    win = f[a0 - L0:a1 - L0, s0:s1]
    k = max(1, int(round(bin_to_m / idx["res"])))
    hh, ww = (win.shape[0] // k) * k, (win.shape[1] // k) * k
    blocks = win[:hh, :ww].reshape(hh // k, k, ww // k, k)
    v_b = np.isfinite(blocks).all(axis=(1, 3))
    win_b = np.nan_to_num(np.nanmean(blocks, axis=(1, 3)), nan=0.0)
    ref_u8 = _stretch_u8(win_b, v_b)

    out_dir = PAIRS_DIR / out_name
    out_dir.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_dir / "mov_ohrc.png"), brw[by0:by0 + crop_h, 0:w])
    cv2.imwrite(str(out_dir / "ref_lro_nac.png"), ref_u8)

    cy, cx = np.mgrid[0:crop_h:16, 0:w:16].astype(np.float64)
    mxx, myy = geo.browse_to_map(cx, cy + by0)
    lq, sq = inv(mxx, myy)
    rx = (sq - s0 + 0.5) / k - 0.5
    ry = (lq - a0 + 0.5) / k - 0.5
    meta = {
        "name": out_dir.name, "kind": "OHRC->LRO_NAC",
        "moving": {"sensor": "OHRC", "file": "mov_ohrc.png", "geotiff": None,
                   "gsd_m": tmeta["moving"]["gsd_m"], "source": tmeta["moving"]["source"], "shape": [crop_h, w]},
        "reference": {"sensor": "LRO_NAC", "file": "ref_lro_nac.png", "geotiff": None,
                      "gsd_m": round(idx["res"] * k, 3), "shape": list(ref_u8.shape),
                      "source": f"LRO NAC {nac_name} CDR lines {a0}-{a1} samples {s0}-{s1} binned {k}x{k}",
                      "incidence_deg": idx["incidence"], "subsolar_azimuth_deg": idx["subsolar_az"]},
        "gt_quality": "approximate: NAC geolocated from PDS index footprint (corners + centre), no SPICE",
        "nac_orientation": {"flip_line": fl, "flip_samp": fs, "distinctiveness_vs_tc": round(float(dist), 3),
                            "nac_vs_tc_offset_tc_px": [int(off_tc[0]), int(off_tc[1])],
                            "all_hypotheses": [(round(float(s[0]), 3), s[1], s[2]) for s in scores]},
        "category": "sun_extreme" if "sunx" in out_name else "cross_sensor",
        "max_bias_m": 800.0,
        "tol_px": 4.0,
        "gt": {"mov_pts": np.stack([cx.ravel(), cy.ravel()], 1).tolist(),
               "ref_pts": np.stack([rx.ravel(), ry.ravel()], 1).tolist()},
    }
    (out_dir / "pair.json").write_text(json.dumps(meta))
    return meta


if __name__ == "__main__":
    for tc_pair, nac, out_name in NAC_PLAN:
        try:
            m = build_ohrc_nac_pair(tc_pair, nac, out_name)
            print(m["name"], "|", m["reference"]["source"], m["reference"]["shape"], "|", m["nac_orientation"], flush=True)
        except Exception as exc:  # report and continue with the next pair
            print("NAC pair failed:", tc_pair, nac, type(exc).__name__, exc, flush=True)
