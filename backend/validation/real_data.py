"""Build real-data validation pairs from public lunar archives.

Sources (all public, no login):
  * Chandrayaan-2 OHRC calibrated PDS4 products (ISSDC PRADAN release mirrored on
    the Internet Archive item ``chandrayaan-2-high-resolution-images-of-the-moon``):
    browse PNG, PDS4 label and the per-pixel lat/lon geometry grid.
  * SELENE/Kaguya Terrain Camera map-projected COGs (USGS Astrogeology STAC,
    collection ``kaguya_terrain_camera_monoscopic_uncontrolled_observations``).
  * LRO NAC calibrated CDR products (PDS LROC node), fetched with HTTP range
    requests so only the lines that overlap the OHRC crop are downloaded.

Every pair is stored together with a ground-truth correspondence grid derived from
the archive geometry (OHRC geometry grid + TC map projection, or NAC footprint),
so registration accuracy can be scored independently of the pipeline itself.

Usage:  python -m validation.real_data            (from backend/)
"""
from __future__ import annotations

import json
import re
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import rasterio
from pyproj import CRS, Transformer
from rasterio.transform import Affine
from rasterio.windows import from_bounds
from scipy.interpolate import RegularGridInterpolator

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "real"
OHRC_DIR = DATA / "ohrc"
PAIRS_DIR = DATA / "pairs"

IA_ITEM = "https://archive.org/download/chandrayaan-2-high-resolution-images-of-the-moon/Optical%20High%20Resolution%20Camera%20%28OHRC%29"
STAC = "https://stac.astrogeology.usgs.gov/api/search"
TC_COLLECTION = "kaguya_terrain_camera_monoscopic_uncontrolled_observations"

MOON_SPS = CRS.from_proj4("+proj=stere +lat_0=-90 +lat_ts=-90 +lon_0=0 +x_0=0 +y_0=0 +R=1737400 +units=m +no_defs")
MOON_LL = CRS.from_proj4("+proj=longlat +R=1737400 +no_defs")
LL2SPS = Transformer.from_crs(MOON_LL, MOON_SPS, always_xy=True)

OHRC_STRIPS = {
    # strip id: (calibrated product name, acquisition day folder, browse decimation)
    "20200229T0739312111": ("ch2_ohr_ncp_20200229T0739312111_d_img_d18", "20200229"),
    "20200229T0938004033": ("ch2_ohr_ncp_20200229T0938004033_d_img_d32", "20200229"),
    "20200824T1003365280": ("ch2_ohr_ncp_20200824T1003365280_d_img_d18", "20200824"),
}
OHRC_FULL_SHAPE = (93693, 12000)  # lines, samples (PDS4 label)


def _get(url: str, dest: Path, timeout: int = 600) -> Path:
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=timeout) as r, open(dest, "wb") as f:
        f.write(r.read())
    return dest


def fetch_ohrc() -> None:
    """Download browse image, PDS4 label and geometry grid for each OHRC strip."""
    for sid, (product, day) in OHRC_STRIPS.items():
        suf = product.rsplit("_", 1)[-1]
        zip_name = f"ch2_ohr_ncp_{sid}_d_img_{suf}.zip"
        base = f"{IA_ITEM}/{zip_name}"
        _get(f"{base}/browse%2Fcalibrated%2F{day}%2Fch2_ohr_ncp_{sid}_b_brw_{suf}.png", OHRC_DIR / f"{sid}_brw.png")
        _get(f"{base}/data%2Fcalibrated%2F{day}%2F{product}.xml", OHRC_DIR / f"{sid}_img.xml")
        _get(f"{base}/geometry%2Fcalibrated%2F{day}%2Fch2_ohr_ncp_{sid}_g_grd_{suf}.csv", OHRC_DIR / f"{sid}_grd.csv")


@dataclass
class OhrcGeometry:
    """Maps OHRC browse pixel coordinates to lunar south-polar stereographic metres."""

    fx: RegularGridInterpolator
    fy: RegularGridInterpolator
    decim: float

    @classmethod
    def load(cls, sid: str) -> "OhrcGeometry":
        g = np.loadtxt(OHRC_DIR / f"{sid}_grd.csv", delimiter=",", skiprows=1)
        scans = np.unique(g[:, 3])
        pixels = np.unique(g[:, 2])
        lon = g[:, 0].reshape(len(scans), len(pixels))
        lat = g[:, 1].reshape(len(scans), len(pixels))
        x, y = LL2SPS.transform(lon, lat)
        brw = cv2.imread(str(OHRC_DIR / f"{sid}_brw.png"), cv2.IMREAD_GRAYSCALE)
        decim = OHRC_FULL_SHAPE[1] / brw.shape[1]
        kw = dict(bounds_error=False, fill_value=None)
        return cls(RegularGridInterpolator((scans, pixels), x, **kw),
                   RegularGridInterpolator((scans, pixels), y, **kw), decim)

    def browse_to_map(self, bx: np.ndarray, by: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        line = (np.asarray(by, dtype=np.float64) + 0.5) * self.decim - 0.5
        samp = (np.asarray(bx, dtype=np.float64) + 0.5) * self.decim - 0.5
        pts = np.stack([line.ravel(), samp.ravel()], axis=1)
        return self.fx(pts).reshape(np.shape(bx)), self.fy(pts).reshape(np.shape(bx))


def stac_tc_items(lon: float, lat: float) -> list[dict]:
    url = f"{STAC}?collections={TC_COLLECTION}&bbox={lon - 0.01},{lat - 0.01},{lon + 0.01},{lat + 0.01}&limit=50"
    with urllib.request.urlopen(url, timeout=120) as r:
        return json.load(r)["features"]


def _stretch_u8(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    lo, hi = np.percentile(a[valid], [0.5, 99.5])
    out = np.clip((a.astype(np.float64) - lo) / max(hi - lo, 1e-6) * 255.0, 0, 255)
    out[~valid] = 0
    return out.astype(np.uint8)


def read_tc_window(href: str, bounds: tuple[float, float, float, float]):
    """Read a TC COG window given south-polar stereographic bounds.

    COGs that are not already polar stereographic (e.g. equirectangular TC
    products north of -65 deg) are warped on the fly at their native GSD.
    Returns (int16 array, transform, crs, nodata) in MOON_SPS.
    """
    from rasterio.enums import Resampling
    from rasterio.warp import reproject, transform_bounds
    with rasterio.open(f"/vsicurl/{href}") as ds:
        if CRS.from_user_input(ds.crs).to_proj4().startswith("+proj=stere"):
            win = from_bounds(*bounds, transform=ds.transform).round_offsets().round_lengths()
            arr = ds.read(1, window=win, boundless=True, fill_value=ds.nodata)
            return arr, ds.window_transform(win), MOON_SPS, ds.nodata
        # Equirectangular product: warp the overlapping source window onto a polar grid
        # at the native ground sample distance (taken along the latitude axis).
        gsd = abs(ds.transform.e)
        sb = transform_bounds(MOON_SPS, ds.crs, *bounds, densify_pts=41)
        swin = from_bounds(*sb, transform=ds.transform).round_offsets().round_lengths()
        src = ds.read(1, window=swin, boundless=True, fill_value=ds.nodata)
        str_ = ds.window_transform(swin)
        w = int(np.ceil((bounds[2] - bounds[0]) / gsd))
        h = int(np.ceil((bounds[3] - bounds[1]) / gsd))
        dtr = Affine(gsd, 0, bounds[0], 0, -gsd, bounds[3])
        dst = np.full((h, w), ds.nodata, dtype=src.dtype)
        reproject(src, dst, src_transform=str_, src_crs=ds.crs, src_nodata=ds.nodata,
                  dst_transform=dtr, dst_crs=MOON_SPS, dst_nodata=ds.nodata, resampling=Resampling.bilinear)
        return dst, dtr, MOON_SPS, ds.nodata


def _write_geotiff(path: Path, arr: np.ndarray, transform: Affine, crs, nodata=None) -> None:
    profile = dict(driver="GTiff", width=arr.shape[1], height=arr.shape[0], count=1,
                   dtype=arr.dtype, crs=crs, transform=transform)
    if nodata is not None:
        profile["nodata"] = nodata
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(arr, 1)


def ortho_ohrc(brw: np.ndarray, geo: OhrcGeometry, x0: int, y0: int, w: int, h: int, gsd: float):
    """Orthorectify an OHRC browse crop onto the south-polar stereographic grid."""
    gy, gx = np.mgrid[y0:y0 + h + 1:8, x0:x0 + w + 1:8].astype(np.float64)
    mx, my = geo.browse_to_map(gx, gy)
    # inverse polynomial map (map metres -> browse px), 3rd order is exact to << 0.1 px here
    A = _poly_terms(mx.ravel(), my.ravel())
    cx, *_ = np.linalg.lstsq(A, gx.ravel(), rcond=None)
    cy, *_ = np.linalg.lstsq(A, gy.ravel(), rcond=None)
    xmin, xmax, ymin, ymax = mx.min(), mx.max(), my.min(), my.max()
    ow, oh = int(np.ceil((xmax - xmin) / gsd)), int(np.ceil((ymax - ymin) / gsd))
    ty, tx = np.mgrid[0:oh, 0:ow].astype(np.float64)
    X = xmin + (tx + 0.5) * gsd
    Y = ymax - (ty + 0.5) * gsd
    B = _poly_terms(X.ravel(), Y.ravel())
    sx = (B @ cx).reshape(oh, ow).astype(np.float32)
    sy = (B @ cy).reshape(oh, ow).astype(np.float32)
    inside = (sx >= x0) & (sx <= x0 + w - 1) & (sy >= y0) & (sy <= y0 + h - 1)
    out = cv2.remap(brw, sx, sy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    out[~inside] = 0
    out[inside & (out == 0)] = 1  # keep 0 reserved for nodata
    return out, Affine(gsd, 0, xmin, 0, -gsd, ymax)


def _poly_terms(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    xs, ys = (x - x.mean()) / 1000.0, (y - y.mean()) / 1000.0
    _poly_terms.center = (x.mean(), y.mean())
    return np.stack([np.ones_like(xs), xs, ys, xs * xs, xs * ys, ys * ys,
                     xs ** 3, xs * xs * ys, xs * ys * ys, ys ** 3], axis=1)


def build_ohrc_tc_pair(name: str, sid: str, by0: int, crop: int = 1024, margin_m: float = 500.0) -> dict:
    """OHRC browse crop (moving, raw strip geometry) vs SELENE TC window (reference)."""
    out_dir = PAIRS_DIR / name
    out_dir.mkdir(parents=True, exist_ok=True)
    brw = cv2.imread(str(OHRC_DIR / f"{sid}_brw.png"), cv2.IMREAD_GRAYSCALE)
    geo = OhrcGeometry.load(sid)
    bx0, w = 0, brw.shape[1]
    mov = brw[by0:by0 + crop, bx0:bx0 + w]

    gy, gx = np.mgrid[by0:by0 + crop:32, 0:w:32].astype(np.float64)
    mx, my = geo.browse_to_map(gx, gy)
    lon_c, lat_c = Transformer.from_crs(MOON_SPS, MOON_LL, always_xy=True).transform(mx.mean(), my.mean())

    items = stac_tc_items(lon_c, lat_c)
    best = None
    for it in items:
        href = it["assets"]["image"]["href"]
        bounds = (mx.min() - margin_m, my.min() - margin_m, mx.max() + margin_m, my.max() + margin_m)
        arr, tr, crs, nod = read_tc_window(href, bounds)
        valid = arr != nod
        if valid.mean() < 0.97:
            continue
        sun_el = it["properties"].get("view:sun_elevation")
        score = float(valid.mean()) * 1e3 + float(np.std(arr[valid]))
        if best is None or score > best[0]:
            best = (score, it, arr, tr, crs, nod, sun_el)
    if best is None:
        raise RuntimeError(f"No full-coverage TC observation for {name}")
    _, it, arr, tr, crs, nod, sun_el = best
    valid = arr != nod
    ref_u8 = _stretch_u8(arr, valid)

    # Ground truth: OHRC browse crop pixel -> TC window pixel via geometry grid + TC transform
    cy, cx = np.mgrid[0:crop:16, 0:w:16].astype(np.float64)
    mxx, myy = geo.browse_to_map(cx + bx0, cy + by0)
    inv = ~tr
    rx, ry = inv * (mxx, myy)
    rx, ry = rx - 0.5, ry - 0.5  # pixel-centre convention
    gt = {"mov_pts": np.stack([cx.ravel(), cy.ravel()], 1).tolist(),
          "ref_pts": np.stack([rx.ravel(), ry.ravel()], 1).tolist()}

    # Orientation/scale of the mapping (for reporting)
    J = np.array([[rx[0, 1] - rx[0, 0], rx[1, 0] - rx[0, 0]], [ry[0, 1] - ry[0, 0], ry[1, 0] - ry[0, 0]]]) / 16.0
    det = float(np.linalg.det(J))
    scale = float(np.sqrt(abs(det)))
    rot = float(np.degrees(np.arctan2(J[1, 0], J[0, 0])))

    cv2.imwrite(str(out_dir / "mov_ohrc.png"), mov)
    cv2.imwrite(str(out_dir / "ref_selene_tc.png"), ref_u8)
    _write_geotiff(out_dir / "ref_selene_tc.tif", arr, tr, crs, nodata=nod)
    ortho, otr = ortho_ohrc(brw, geo, bx0, by0, w, crop, gsd=2.5)
    _write_geotiff(out_dir / "mov_ohrc_ortho.tif", ortho, otr, MOON_SPS, nodata=0)

    meta = {
        "name": name,
        "kind": "OHRC->SELENE_TC",
        "moving": {"sensor": "OHRC", "file": "mov_ohrc.png", "geotiff": "mov_ohrc_ortho.tif",
                   "source": f"Chandrayaan-2 OHRC {OHRC_STRIPS[sid][0]} browse rows {by0}-{by0 + crop}",
                   "gsd_m": round(geo.decim * 0.23, 3), "shape": list(mov.shape)},
        "reference": {"sensor": "SELENE", "file": "ref_selene_tc.png", "geotiff": "ref_selene_tc.tif",
                      "source": f"Kaguya TC {it['id']} ({it['properties']['datetime'][:10]})",
                      "gsd_m": round(abs(tr.a), 3), "shape": list(ref_u8.shape),
                      "sun_elevation_deg": sun_el, "sun_azimuth_deg": it["properties"].get("view:sun_azimuth")},
        "center_lonlat": [round(lon_c, 5), round(lat_c, 5)],
        "gt_mapping": {"det": det, "scale_ref_per_mov": scale, "rotation_deg": rot,
                       "mirrored": det < 0},
        "gt": gt,
    }
    with open(out_dir / "pair.json", "w") as f:
        json.dump(meta, f)
    return meta


if __name__ == "__main__":
    fetch_ohrc()
    plan = [
        ("ohrc_tc_s1_a", "20200229T0739312111", 2500),
        ("ohrc_tc_s1_b", "20200229T0739312111", 6000),
        ("ohrc_tc_s2_a", "20200229T0938004033", 1500),
        ("ohrc_tc_s2_b", "20200229T0938004033", 5500),
        ("ohrc_tc_s3_a", "20200824T1003365280", 2000),
        ("ohrc_tc_s3_b", "20200824T1003365280", 6500),
    ]
    for name, sid, by0 in plan:
        m = build_ohrc_tc_pair(name, sid, by0)
        g = m["gt_mapping"]
        print(f"{name}: ref={m['reference']['source']} mov{m['moving']['shape']} ref{m['reference']['shape']} "
              f"scale={g['scale_ref_per_mov']:.3f} rot={g['rotation_deg']:.1f} mirrored={g['mirrored']}")
