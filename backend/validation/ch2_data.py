"""Real Chandrayaan-2 TMC-2 -> IIRS validation pairs from raw ISSDC PDS4 products.

Both products come from the same orbit (1675, 2020-01-09), so the two strips
image the same ground within minutes under identical illumination; what differs
is the sensor (panchromatic pushbroom vs 256-band infrared spectrometer),
resolution (4.9 m vs 78 m) and view geometry (TMC-2 fore camera, ~25 deg ahead).

    python validation/ch2_data.py [--tmc DIR] [--iirs DIR] [--n 6]

Moving   = TMC-2 crop, area-decimated 4x to 19.6 m (raw strip geometry).
Reference = IIRS crop, mean of bands 9-28 (850-1200 nm), column-destriped.
Ground truth comes from the labels' ground-projected corner coordinates
(bilinear in line/sample). Its absolute accuracy is limited by each product's
pointing knowledge, so a constant offset is expected; `gt_bias_rm_*` in
run_validation measures the error after removing that offset.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.io.pds_reader import read_pds4_array, read_pds4_label  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parents[1] / "data" / "real" / "pairs"
TMC_DECIMATE = 4
IIRS_BANDS = list(range(8, 28))   # 0-based; 864-1184 nm, clear of the dead blue bands and the 1218 nm seam
MOV_LINES = 200                   # IIRS lines the moving crop spans (~16 km)
REF_PAD = 160                     # reference lines added above and below; the labels disagree by ~100 lines
REF_LINES = MOV_LINES + 2 * REF_PAD
CORE = 0.62                       # moving crop covers this central fraction of the reference width


class CornerGeometry:
    """Bilinear (line, sample) <-> (lat, lon) model from a label's four ground corners."""

    def __init__(self, meta: dict):
        c = meta["corners"]
        self.n_lines, self.n_samples = meta["lines"], meta["samples"]
        self.q = {k: np.asarray(v, float) for k, v in c.items()}

    def forward(self, line, sample):
        v = np.asarray(line, float) / (self.n_lines - 1)
        u = np.asarray(sample, float) / (self.n_samples - 1)
        q = self.q
        top = q["upper_left"][:, None] * (1 - u) + q["upper_right"][:, None] * u
        bot = q["lower_left"][:, None] * (1 - u) + q["lower_right"][:, None] * u
        latlon = top * (1 - v) + bot * v
        return latlon[0], latlon[1]

    def inverse(self, lat, lon, iters: int = 8):
        lat, lon = np.asarray(lat, float), np.asarray(lon, float)
        line = np.full(lat.shape, self.n_lines / 2.0)
        sample = np.full(lat.shape, self.n_samples / 2.0)
        for _ in range(iters):  # Newton on the bilinear map, numerical Jacobian
            la, lo = self.forward(line, sample)
            la_l, lo_l = self.forward(line + 1.0, sample)
            la_s, lo_s = self.forward(line, sample + 1.0)
            j11, j12, j21, j22 = la_l - la, la_s - la, lo_l - lo, lo_s - lo
            det = j11 * j22 - j12 * j21
            r1, r2 = lat - la, lon - lo
            line = line + (j22 * r1 - j12 * r2) / det
            sample = sample + (-j21 * r1 + j11 * r2) / det
        return line, sample


def _find_label(directory: Path) -> Path:
    labels = sorted((directory / "data").rglob("*_d_img_*.xml"))
    if not labels:
        raise FileNotFoundError(f"no PDS4 data label under {directory / 'data'}")
    return labels[0]


def destripe_columns(img: np.ndarray) -> np.ndarray:
    """Remove pushbroom detector striping: equalise each column's median and spread to the strip's."""
    med = np.median(img, axis=0)
    mad = np.median(np.abs(img - med), axis=0) + 1e-6
    return (img - med) / mad * np.median(mad) + np.median(med)


def stretch_u8(a: np.ndarray, lo_pct: float = 0.5, hi_pct: float = 99.5) -> np.ndarray:
    lo, hi = np.percentile(a, [lo_pct, hi_pct])
    return np.clip((a - lo) / max(hi - lo, 1e-9) * 254 + 1, 1, 255).astype(np.uint8)


def build_pairs(tmc_dir: Path, iirs_dir: Path, n_pairs: int) -> list[dict]:
    tmc_label, iirs_label = _find_label(tmc_dir), _find_label(iirs_dir)
    tmc_meta, iirs_meta = read_pds4_label(str(tmc_label)), read_pds4_label(str(iirs_label))
    g_tmc, g_iirs = CornerGeometry(tmc_meta), CornerGeometry(iirs_meta)

    print(f"IIRS: averaging bands {IIRS_BANDS[0] + 1}-{IIRS_BANDS[-1] + 1}", flush=True)
    iirs = destripe_columns(read_pds4_array(str(iirs_label), band=IIRS_BANDS).astype(np.float32))

    # overlapping IIRS line range: lines whose ground also lies inside the TMC strip
    lines = np.arange(0, iirs_meta["lines"], 16)
    lat, lon = g_iirs.forward(lines, np.full(lines.shape, iirs_meta["samples"] / 2.0))
    tl, _ = g_tmc.inverse(lat, lon)
    inside = lines[(tl > 0) & (tl < tmc_meta["lines"] - 1)]
    j_lo, j_hi = int(inside.min()) + 40, int(inside.max()) - REF_LINES - 40
    starts = np.linspace(j_lo, j_hi, n_pairs).astype(int)

    pairs = []
    for k, j0 in enumerate(starts):
        name = f"ch2_tmc_iirs_{k + 1}"
        ref = iirs[j0:j0 + REF_LINES]
        ref_h, ref_w = ref.shape

        # moving footprint: MOV_LINES x central CORE width of the reference, mapped into TMC full-res pixels
        m = (1 - CORE) / 2
        box_l = j0 + REF_PAD + MOV_LINES * np.array([0.0, 0.0, 1.0, 1.0])
        box_s = ref_w * np.array([m, 1 - m, m, 1 - m])
        tl_full, ts_full = g_tmc.inverse(*g_iirs.forward(box_l, box_s))
        l0, l1 = int(max(0, tl_full.min())), int(min(tmc_meta["lines"], tl_full.max()))
        s0, s1 = int(max(0, ts_full.min())), int(min(tmc_meta["samples"], ts_full.max()))
        l0, s0 = l0 - l0 % TMC_DECIMATE, s0 - s0 % TMC_DECIMATE
        tmc = read_pds4_array(str(tmc_label), rows=(l0, l1)).astype(np.float32)[:, s0:s1]
        h, w = (tmc.shape[0] // TMC_DECIMATE) * TMC_DECIMATE, (tmc.shape[1] // TMC_DECIMATE) * TMC_DECIMATE
        mov = cv2.resize(tmc[:h, :w], (w // TMC_DECIMATE, h // TMC_DECIMATE), interpolation=cv2.INTER_AREA)

        # GT checkpoints: moving pixel -> TMC full-res -> ground -> IIRS -> reference crop pixel
        gy, gx = np.meshgrid(np.linspace(0, mov.shape[0] - 1, 9), np.linspace(0, mov.shape[1] - 1, 9), indexing="ij")
        mov_pts = np.stack([gx.ravel(), gy.ravel()], 1)
        full_l = l0 + (mov_pts[:, 1] + 0.5) * TMC_DECIMATE - 0.5
        full_s = s0 + (mov_pts[:, 0] + 0.5) * TMC_DECIMATE - 0.5
        il, is_ = g_iirs.inverse(*g_tmc.forward(full_l, full_s))
        ref_pts = np.stack([is_, il - j0], 1)
        Hgt, _ = cv2.findHomography(mov_pts, ref_pts, 0)
        A = Hgt[:2, :2] / Hgt[2, 2]
        lat_c, lon_c = g_tmc.forward(np.array([(l0 + l1) / 2.0]), np.array([(s0 + s1) / 2.0]))

        d = OUT / name
        d.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(d / "mov_tmc2.png"), stretch_u8(mov))
        cv2.imwrite(str(d / "ref_iirs.png"), stretch_u8(ref))
        pair = {
            "name": name,
            "kind": "TMC2->IIRS",
            "category": "ch2_cross_sensor",
            "moving": {
                "sensor": "TMC2", "file": "mov_tmc2.png",
                "source": f"Chandrayaan-2 TMC-2 {tmc_label.stem} lines {l0}-{l1} samples {s0}-{s1}, area-decimated x{TMC_DECIMATE}",
                "gsd_m": round(tmc_meta["gsd_meters"] * TMC_DECIMATE, 3), "shape": list(mov.shape),
                "sun_elevation_deg": tmc_meta["solar_elevation_deg"], "sun_azimuth_deg": tmc_meta["solar_azimuth_deg"],
            },
            "reference": {
                "sensor": "IIRS", "file": "ref_iirs.png",
                "source": f"Chandrayaan-2 IIRS {iirs_label.stem} lines {j0}-{j0 + ref_h}, bands {IIRS_BANDS[0] + 1}-{IIRS_BANDS[-1] + 1} mean, column-destriped",
                "gsd_m": iirs_meta["gsd_meters"], "shape": list(ref.shape),
            },
            "center_lonlat": [round(float(lon_c[0]), 4), round(float(lat_c[0]), 4)],
            "gt_source": "PDS4 label ground corners (bilinear); the two labels disagree by ~8 km along-track, so judge by gt_bias_rm_*",
            "gt_mapping": {
                "scale_ref_per_mov": float(np.sqrt(abs(np.linalg.det(A)))),
                "rotation_deg": float(np.degrees(np.arctan2(A[1, 0], A[0, 0]))),
                "mirrored": bool(np.linalg.det(A) < 0),
            },
            "gt": {"mov_pts": mov_pts.tolist(), "ref_pts": ref_pts.tolist()},
        }
        (d / "pair.json").write_text(json.dumps(pair, indent=1))
        print(name, "lat %.2f" % lat_c[0], "mov", mov.shape, "ref", ref.shape,
              "scale %.3f rot %.2f" % (pair["gt_mapping"]["scale_ref_per_mov"], pair["gt_mapping"]["rotation_deg"]), flush=True)
        pairs.append(pair)
    return pairs


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tmc", type=Path, default=ROOT / "tmc")
    ap.add_argument("--iirs", type=Path, default=ROOT / "iir")
    ap.add_argument("--n", type=int, default=6)
    args = ap.parse_args()
    build_pairs(args.tmc, args.iirs, args.n)
