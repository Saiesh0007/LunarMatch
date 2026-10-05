"""Dense structural registration for cross-sensor lunar imagery.

Sparse descriptors (SIFT, RIFT2, SuperPoint) break down when two lunar images
differ simultaneously in sensor, epoch, Sun geometry and ground sample distance:
measured on real Chandrayaan-2 OHRC vs SELENE TC pairs they return < 10 correct
matches even after perfect geometric pre-alignment. Area-based matching on a
structural (oriented-gradient) representation is far more stable in that regime
(Ye et al., "Fast and robust matching for multimodal remote sensing images",
IEEE TGRS 2019 - CFOG), so this module implements:

1. Coarse global search over scale, rotation and translation on smoothed
   gradient-magnitude maps (contrast- and polarity-invariant), restricted by
   priors when the GSD ratio or map orientation is known.
2. Fine template matching on a grid of CFOG patches (unsigned orientation
   channels, so a Sun-azimuth flip that reverses shading polarity still matches),
   with sub-pixel peak interpolation and peak-distinctiveness gating.
3. MAGSAC++ homography estimation, iterated with a shrinking search radius.

All coordinates returned are in the ORIGINAL pixel grids: the homography maps
moving pixels to reference pixels.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import cv2
import numpy as np

# ----------------------------------------------------------------------------
# Representations
# ----------------------------------------------------------------------------


def _to_float(img: np.ndarray) -> np.ndarray:
    a = np.asarray(img)
    if a.ndim == 3:
        a = cv2.cvtColor(a[..., :3].astype(np.float32), cv2.COLOR_BGR2GRAY)
    a = a.astype(np.float32)
    lo, hi = np.percentile(a, [0.5, 99.5]) if a.size else (0.0, 1.0)
    return np.clip((a - lo) / max(hi - lo, 1e-6), 0.0, 1.0).astype(np.float32)


def gradient_magnitude(img: np.ndarray, sigma: float = 1.0) -> np.ndarray:
    """Smoothed, locally contrast-normalised gradient magnitude."""
    a = cv2.GaussianBlur(img, (0, 0), sigma) if sigma > 0 else img
    gx = cv2.Sobel(a, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(a, cv2.CV_32F, 0, 1, ksize=3)
    mag = np.sqrt(gx * gx + gy * gy)
    # local normalisation removes albedo / exposure differences between sensors
    local = cv2.GaussianBlur(mag, (0, 0), 8.0)
    return mag / (local + 1e-3 * float(mag.mean() + 1e-6))


def cfog_channels(img: np.ndarray, n_orient: int = 8, sigma: float = 0.8, smooth: float = 1.5) -> np.ndarray:
    """Channel features of orientated gradients with unsigned orientation."""
    a = cv2.GaussianBlur(img, (0, 0), sigma) if sigma > 0 else img
    gx = cv2.Sobel(a, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(a, cv2.CV_32F, 0, 1, ksize=3)
    mag = np.sqrt(gx * gx + gy * gy)
    theta2 = 2.0 * np.arctan2(gy, gx)  # angle doubling -> polarity invariant
    ch = np.empty(img.shape + (n_orient,), np.float32)
    for k in range(n_orient):
        c = np.cos(theta2 - 2.0 * math.pi * k / n_orient)
        ch[..., k] = cv2.GaussianBlur(mag * np.maximum(c, 0.0) ** 2, (0, 0), smooth)
    norm = np.sqrt((ch * ch).sum(axis=2, keepdims=True)) + 1e-3 * float(mag.mean() + 1e-6)
    return ch / norm


# ----------------------------------------------------------------------------
# Matching helpers
# ----------------------------------------------------------------------------


def _subpixel(res: np.ndarray, loc: Tuple[int, int]) -> Tuple[float, float]:
    x, y = loc
    dx = dy = 0.0
    if 0 < x < res.shape[1] - 1:
        l, c, r = res[y, x - 1], res[y, x], res[y, x + 1]
        den = l - 2 * c + r
        if abs(den) > 1e-9:
            dx = float(np.clip(0.5 * (l - r) / den, -0.5, 0.5))
    if 0 < y < res.shape[0] - 1:
        u, c, d = res[y - 1, x], res[y, x], res[y + 1, x]
        den = u - 2 * c + d
        if abs(den) > 1e-9:
            dy = float(np.clip(0.5 * (u - d) / den, -0.5, 0.5))
    return x + dx, y + dy


def _peak_stats(res: np.ndarray, excl: int) -> Tuple[float, float, Tuple[int, int]]:
    """Best peak, best value outside an exclusion disc, and the peak location.

    NaN entries mark invalid placements and are ignored.
    """
    r = np.nan_to_num(res, nan=-np.inf) if np.isnan(res).any() else res
    flat = int(np.argmax(r))
    loc = (flat % r.shape[1], flat // r.shape[1])
    p1 = float(r[loc[1], loc[0]])
    yy, xx = np.ogrid[:r.shape[0], :r.shape[1]]
    outside = (yy - loc[1]) ** 2 + (xx - loc[0]) ** 2 > max(int(excl), 1) ** 2
    rest = r[outside & np.isfinite(r)]
    p2 = float(rest.max()) if rest.size else p1
    return p1, p2, loc


def _rot_scale_matrix(shape: Tuple[int, int], angle_deg: float, scale: float) -> Tuple[np.ndarray, Tuple[int, int]]:
    """Affine (2x3) that rotates/scales an image of `shape` onto an expanded canvas."""
    h, w = shape
    M = cv2.getRotationMatrix2D((w / 2.0, h / 2.0), angle_deg, scale)
    cos, sin = abs(M[0, 0]), abs(M[0, 1])
    nw, nh = int(math.ceil(h * sin + w * cos)), int(math.ceil(h * cos + w * sin))
    M[0, 2] += nw / 2.0 - w / 2.0
    M[1, 2] += nh / 2.0 - h / 2.0
    return M, (nh, nw)


def _inscribed_rect(mask: np.ndarray) -> Tuple[int, int, int, int]:
    """Largest axis-aligned rectangle of valid pixels centred in a warped template."""
    h, w = mask.shape
    cy, cx = h // 2, w // 2
    lo, hi = 0.0, 1.0
    for _ in range(18):  # binary search on the fraction of the bounding box kept
        mid = (lo + hi) / 2
        hh, hw = max(1, int(h * mid / 2)), max(1, int(w * mid / 2))
        if mask[cy - hh:cy + hh, cx - hw:cx + hw].all():
            lo = mid
        else:
            hi = mid
    hh, hw = max(1, int(h * lo / 2)), max(1, int(w * lo / 2))
    return cy - hh, cy + hh, cx - hw, cx + hw


def _tile_vote(gref: np.ndarray, g_full: np.ndarray, rect: Tuple[int, int, int, int], min_px: int):
    """Match quadrant + centre tiles of the (rotated) moving map inside the reference.

    Returns (score, best_ncc, (tx, ty)) where (tx, ty) maps canvas pixels to reference
    pixels, score = summed distinctiveness of the tiles agreeing on that shift, or None.
    """
    y0, y1, x0, x1 = rect
    h, w = y1 - y0, x1 - x0
    max_h, max_w = int(0.8 * gref.shape[0]), int(0.8 * gref.shape[1])
    th, tw = min(max(h // 2, min_px), max_h, h), min(max(w // 2, min_px), max_w, w)
    if min(th, tw) < min_px:
        return None
    starts = {(y0, x0), (y0, x1 - tw), (y1 - th, x0), (y1 - th, x1 - tw),
              (y0 + (h - th) // 2, x0 + (w - tw) // 2)}
    votes = []
    for ty0, tx0 in starts:
        tile = g_full[ty0:ty0 + th, tx0:tx0 + tw]
        if float(tile.std()) < 1e-6:
            continue
        res = cv2.matchTemplate(gref, tile, cv2.TM_CCOEFF_NORMED)
        p1, p2, loc = _peak_stats(res, excl=max(3, min(th, tw) // 6))
        votes.append((p1 - p2, p1, loc[0] - tx0, loc[1] - ty0))
    if not votes:
        return None
    tol = max(2.0, 0.02 * max(gref.shape))
    best = None
    for d_i, p_i, sx, sy in votes:
        agree = [v for v in votes if abs(v[2] - sx) <= tol and abs(v[3] - sy) <= tol]
        score = sum(max(v[0], 0.0) for v in agree)
        if len(agree) == 1:
            score *= 0.5  # an unsupported single tile is weak evidence
        if best is None or score > best[0]:
            wsum = sum(max(v[0], 1e-6) for v in agree)
            mx = sum(max(v[0], 1e-6) * v[2] for v in agree) / wsum
            my = sum(max(v[0], 1e-6) * v[3] for v in agree) / wsum
            best = (score, max(v[1] for v in agree), (mx, my))
    return best


def _to3(A: np.ndarray) -> np.ndarray:
    return np.vstack([A, [0.0, 0.0, 1.0]]) if A.shape == (2, 3) else A


# ----------------------------------------------------------------------------
# Coarse global search
# ----------------------------------------------------------------------------


@dataclass
class CoarseResult:
    H: np.ndarray  # 3x3 moving -> reference (original pixels)
    scale: float
    angle: float
    score: float
    distinct: float
    n_hypotheses: int


def coarse_search(
    ref: np.ndarray,
    mov: np.ndarray,
    scales: Sequence[float],
    angles: Sequence[float],
    work_px: int = 240,
    min_template_px: int = 24,
    top_k: int = 1,
    sigma: float = 2.0,
):
    """Exhaustive scale x rotation x translation search on gradient-magnitude maps.

    `scales` are moving->reference pixel scale factors to test. Returns the best
    hypothesis (top_k=1) or a list of up to `top_k` well-separated hypotheses,
    best first, so a later verification stage can reject a spurious coarse peak.
    """
    c = min(1.0, work_px / float(max(ref.shape)))
    ref_c = cv2.resize(ref, None, fx=c, fy=c, interpolation=cv2.INTER_AREA) if c < 1 else ref
    gref = gradient_magnitude(ref_c, sigma=sigma)
    hyps: List[Tuple[float, float, float, float, np.ndarray]] = []
    n = 0
    for s in scales:
        sc = s * c  # moving pixel -> coarse reference pixel
        th, tw = mov.shape[0] * sc, mov.shape[1] * sc
        if min(th, tw) < min_template_px:
            continue
        # When the scaled moving image dwarfs the reference, the reference becomes the
        # template; beyond 4x linear size the search space only adds false peaks.
        if max(th / ref_c.shape[0], tw / ref_c.shape[1]) > 4.0:
            continue
        # Resample the moving image to the coarse reference scale once (area averaging,
        # no aliasing). Gradient magnitude is a rotation-invariant scalar field, so it
        # is computed once per scale and only rotated per angle hypothesis.
        pre = min(1.0, sc)
        mov_p = cv2.resize(mov, None, fx=pre, fy=pre, interpolation=cv2.INTER_AREA) if pre < 1 else mov
        rs = sc / pre
        g_p = gradient_magnitude(mov_p, sigma=sigma)
        for a in angles:
            n += 1
            M, (nh, nw) = _rot_scale_matrix(mov_p.shape, a, rs)
            g_full = cv2.warpAffine(g_p, M, (nw, nh), flags=cv2.INTER_LINEAR)
            valid = cv2.warpAffine(np.ones(mov_p.shape, np.uint8), M, (nw, nh), flags=cv2.INTER_NEAREST) > 0
            y0, y1, x0, x1 = _inscribed_rect(valid)
            if min(y1 - y0, x1 - x0) < min_template_px:
                continue
            big, small, swapped = gref, None, False
            if (y1 - y0) >= 1.25 * gref.shape[0] and (x1 - x0) >= 1.25 * gref.shape[1]:
                # moving footprint clearly larger than the reference: slide the reference inside it
                small, big, swapped = gref, g_full, True
            else:
                # Tile voting: the footprints may only partly overlap (e.g. an OHRC strip
                # running off the edge of a NAC swath), so a single whole-image template
                # is diluted by unmatched area. Match the four quadrants and the centre
                # independently and score the pose by the tiles that agree on one shift.
                vote = _tile_vote(gref, g_full, (y0, y1, x0, x1), min_template_px)
                if vote is None:
                    continue
                score, p1, (tx, ty) = vote
                A = _to3(M) @ np.diag([pre, pre, 1.0])
                T = np.array([[1, 0, tx], [0, 1, ty], [0, 0, 1]], float)
                hyps.append((score, p1, s, a, np.diag([1.0 / c, 1.0 / c, 1.0]) @ T @ A))
                continue
            res = cv2.matchTemplate(big, small, cv2.TM_CCOEFF_NORMED)
            if swapped:
                # only positions where the reference lies fully on valid moving pixels
                cover = cv2.matchTemplate(valid.astype(np.float32), np.ones(small.shape, np.float32), cv2.TM_CCORR)
                ok = cover >= 0.98 * small.size
                if int(ok.sum()) < 49:  # too few placements to judge peak distinctiveness
                    continue
                res = np.where(ok, res, np.nan).astype(np.float32)
            p1, p2, loc = _peak_stats(res, excl=max(3, min(small.shape) // 6))
            score = p1 - p2  # distinctiveness drives selection; absolute NCC is low cross-sensor
            if True:
                # warped-canvas <- original moving pixels
                A = _to3(M) @ np.diag([pre, pre, 1.0])
                if not swapped:
                    T = np.array([[1, 0, loc[0] - x0], [0, 1, loc[1] - y0], [0, 0, 1]], float)
                    H_c = T @ A
                else:
                    # reference (coarse) pixel q maps to warped-moving pixel q + loc
                    T = np.array([[1, 0, -loc[0]], [0, 1, -loc[1]], [0, 0, 1]], float)
                    H_c = T @ A
                H = np.diag([1.0 / c, 1.0 / c, 1.0]) @ H_c
                hyps.append((score, p1, s, a, H))
    hyps.sort(key=lambda h: -h[0])
    picked: List[CoarseResult] = []
    for score, p1, s, a, H in hyps:
        # non-maximum suppression in (angle, scale)
        if any(abs(((a - q.angle + 180) % 360) - 180) < 12 and abs(math.log(s / q.scale)) < 0.2 for q in picked):
            continue
        picked.append(CoarseResult(H=H, scale=s, angle=a, score=p1, distinct=score, n_hypotheses=n))
        if len(picked) >= top_k:
            break
    if top_k == 1:
        return picked[0] if picked else None
    return picked


# ----------------------------------------------------------------------------
# Fine template matching
# ----------------------------------------------------------------------------


@dataclass
class DenseMatch:
    mov_pt: Tuple[float, float]
    ref_pt: Tuple[float, float]
    score: float
    distinct: float


def _fine_matches(
    ref_ch: np.ndarray,
    ref_valid: np.ndarray,
    mov: np.ndarray,
    H: np.ndarray,
    grid: int,
    tpl: int,
    radius: int,
    min_score: float,
    min_distinct: float,
) -> List[DenseMatch]:
    h, w = ref_ch.shape[:2]
    warped = cv2.warpPerspective(mov, H, (w, h), flags=cv2.INTER_LINEAR)
    valid = cv2.warpPerspective(np.ones(mov.shape, np.uint8), H, (w, h), flags=cv2.INTER_NEAREST) > 0
    valid &= ref_valid
    mov_ch = cfog_channels(warped)
    half = tpl // 2
    inner = cv2.erode(valid.astype(np.uint8), np.ones((2 * (half + radius) + 1,) * 2, np.uint8)) > 0
    ys, xs = np.nonzero(inner)
    if len(xs) == 0:
        return []
    Hinv = np.linalg.inv(H)
    gx = np.linspace(xs.min(), xs.max(), grid)
    gy = np.linspace(ys.min(), ys.max(), grid)
    # texture: prefer template centres with structure inside each grid cell
    tex = cv2.GaussianBlur(gradient_magnitude(warped), (0, 0), half / 2.0)
    out: List[DenseMatch] = []
    cell_w = max(1.0, (xs.max() - xs.min()) / max(grid - 1, 1))
    cell_h = max(1.0, (ys.max() - ys.min()) / max(grid - 1, 1))
    for cy in gy:
        for cx in gx:
            y0, y1 = int(max(cy - cell_h / 2, 0)), int(min(cy + cell_h / 2 + 1, h))
            x0, x1 = int(max(cx - cell_w / 2, 0)), int(min(cx + cell_w / 2 + 1, w))
            sub = np.where(inner[y0:y1, x0:x1], tex[y0:y1, x0:x1], -1.0)
            if sub.max() <= 0:
                continue
            py, px = np.unravel_index(int(np.argmax(sub)), sub.shape)
            px, py = px + x0, py + y0
            T = mov_ch[py - half:py + half, px - half:px + half]
            S = ref_ch[py - half - radius:py + half + radius, px - half - radius:px + half + radius]
            if T.shape[:2] != (2 * half, 2 * half) or S.shape[0] < T.shape[0] or S.shape[1] < T.shape[1]:
                continue
            res = None
            for k in range(T.shape[2]):
                r = cv2.matchTemplate(np.ascontiguousarray(S[..., k]), np.ascontiguousarray(T[..., k]), cv2.TM_CCOEFF_NORMED)
                res = r if res is None else res + r
            res /= T.shape[2]
            p1, p2, loc = _peak_stats(res, excl=3)
            if p1 < min_score or (p1 - p2) < min_distinct:
                continue
            sx, sy = _subpixel(res, loc)
            rx, ry = px + (sx - radius), py + (sy - radius)
            m = Hinv @ np.array([px, py, 1.0])
            out.append(DenseMatch((float(m[0] / m[2]), float(m[1] / m[2])), (float(rx), float(ry)), float(p1), float(p1 - p2)))
    return out


# ----------------------------------------------------------------------------
# Public entry point
# ----------------------------------------------------------------------------


@dataclass
class DenseResult:
    H: Optional[np.ndarray]
    matches: List[DenseMatch]
    inlier_mask: np.ndarray
    diagnostics: Dict = field(default_factory=dict)


def homography_is_sane(H: np.ndarray, mov_shape: Tuple[int, int], max_aniso: float = 3.0) -> Tuple[bool, str]:
    """Reject folded, collapsed or wildly perspective solutions over the moving footprint."""
    h, w = mov_shape
    corners = np.float64([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2)
    den = H[2, 0] * corners[:, 0, 0] + H[2, 1] * corners[:, 0, 1] + H[2, 2]
    if np.any(den <= 1e-9):
        return False, "footprint crosses the horizon line"
    q = cv2.perspectiveTransform(corners, H).reshape(-1, 2)
    if not cv2.isContourConvex(q.astype(np.float32).reshape(-1, 1, 2)):
        return False, "projected footprint is not convex"
    sv = np.linalg.svd(H[:2, :2] / H[2, 2], compute_uv=False)
    if sv[1] <= 1e-9 or sv[0] / sv[1] > max_aniso:
        return False, f"anisotropy {sv[0] / max(sv[1], 1e-9):.1f} > {max_aniso}"
    return True, ""


def default_scales(scale_prior: Optional[float]) -> List[float]:
    if scale_prior is not None and scale_prior > 0:
        # Nominal GSDs are nadir values; off-nadir pointing (OHRC/NAC slews) and the
        # map-projection scale factor shift the true ratio by up to ~40 %.
        return [scale_prior * 2.0 ** (k / 8.0) for k in range(-4, 5)]
    return [2.0 ** (k / 3.0) for k in range(-9, 10)]  # 1/8 .. 8


def default_angles(angle_prior: Optional[float], tol: float = 6.0) -> List[float]:
    if angle_prior is not None:
        return list(np.arange(angle_prior - tol, angle_prior + tol + 1e-6, 2.0))
    return list(np.arange(0.0, 360.0, 10.0))


def _resize(a: np.ndarray, f: float) -> np.ndarray:
    return cv2.resize(a, None, fx=f, fy=f, interpolation=cv2.INTER_AREA) if f < 1.0 else a


def register_dense(
    ref_img: np.ndarray,
    mov_img: np.ndarray,
    scale_prior: Optional[float] = None,
    angle_prior: Optional[float] = None,
    initial_H: Optional[np.ndarray] = None,
    grid: int = 10,
    reproj_threshold: float = 1.5,
    min_inliers: int = 12,
    max_hypotheses: int = 6,
    max_work_px: int = 1400,
) -> DenseResult:
    """Register `mov_img` onto `ref_img`; returns homography moving -> reference.

    scale_prior: expected moving->reference pixel scale (gsd_mov / gsd_ref).
    angle_prior: expected rotation in degrees (0 for co-projected map data).
    initial_H:   optional full initial guess (original pixels); skips the coarse search.
    max_work_px: the reference is processed at most at this size; the moving image
                 is area-downsampled to roughly the reference working resolution so
                 that warping a much finer image (e.g. OHRC onto TC) does not alias.
    All inputs and outputs are in original pixel coordinates.
    """
    t0 = time.perf_counter()
    ref_full = _to_float(ref_img)
    mov_full = _to_float(mov_img)
    fr = min(1.0, max_work_px / float(max(ref_full.shape)))
    ref = _resize(ref_full, fr)
    Dr = np.diag([fr, fr, 1.0])
    diag: Dict = {"scale_prior": scale_prior, "angle_prior": angle_prior, "ref_work_scale": round(fr, 4)}

    ref_ch = cfog_channels(ref)
    ref_valid = np.ones(ref.shape, bool)
    # first search radius: residual of the locally refined pose (~1 deg / ~3 % over the
    # reference half-width) plus the coarse grid quantisation
    coarse_cell = max(ref.shape) / 240.0
    radius0 = int(np.clip(2 * coarse_cell + 0.035 * max(ref.shape), 16, 72))
    schedule = [(radius0, 0.10, 0.02), (8, 0.12, 0.03), (3, 0.12, 0.03)]
    tpl = int(np.clip(min(ref.shape) / 6, 32, 72)) // 2 * 2
    mov_cache: Dict[float, np.ndarray] = {}

    def refine(H_full: np.ndarray, log: Dict, quick: bool = False):
        """Fine matching for an initial moving->reference homography in original pixels.

        quick=True runs only the first (wide-radius) iteration on a 6x6 grid and is
        used to rank competing coarse hypotheses cheaply.
        """
        Hw = Dr @ H_full  # moving (original) -> reference working pixels
        s_est = math.sqrt(abs(np.linalg.det(Hw[:2, :2]))) if np.all(np.isfinite(Hw)) else 1.0
        fm = float(min(1.0, max(s_est / 0.8, 1e-3)))
        fm = round(fm, 3)
        if fm not in mov_cache:
            mov_cache[fm] = _resize(mov_full, fm)
        mov = mov_cache[fm]
        Dm_inv = np.diag([1.0 / fm, 1.0 / fm, 1.0])
        H = Hw @ Dm_inv  # moving working -> reference working
        matches, mask = [], np.zeros(0, bool)
        sched = schedule[:1] if quick else schedule
        g = 6 if quick else grid
        need = 6 if quick else min_inliers
        for it, (radius, min_score, min_distinct) in enumerate(sched):
            cand = _fine_matches(ref_ch, ref_valid, mov, H, g, tpl, radius, min_score, min_distinct)
            log[f"iter{it}_candidates"] = len(cand)
            if len(cand) < need:
                break
            src = np.float32([m.mov_pt for m in cand])
            dst = np.float32([m.ref_pt for m in cand])
            Hn, msk = cv2.findHomography(src, dst, cv2.USAC_MAGSAC, reproj_threshold + (2.0 if it == 0 else 0.0),
                                         maxIters=10000, confidence=0.999)
            if Hn is None or msk is None or int(msk.sum()) < need:
                break
            H, matches, mask = Hn, cand, msk.ravel().astype(bool)
            log[f"iter{it}_inliers"] = int(mask.sum())
            log["confirmed_iters"] = it + 1
        if not quick and log.get("confirmed_iters", 0) < 2:
            # The wide first pass tolerates ~3.5 px and on featureless or unrelated
            # texture can lock onto chance agreements; a genuine pose survives the
            # tighter radius/threshold of at least the second pass.
            if len(matches):
                log["failure_reason"] = "dense pose not confirmed by tighter refinement pass"
            mask = np.zeros(len(matches), bool)
        # back to original pixel grids
        H_out = np.linalg.inv(Dr) @ H @ np.diag([fm, fm, 1.0])
        H_out /= H_out[2, 2]
        out = [DenseMatch((m.mov_pt[0] / fm, m.mov_pt[1] / fm), (m.ref_pt[0] / fr, m.ref_pt[1] / fr), m.score, m.distinct)
               for m in matches]
        log["mov_work_scale"] = fm
        return H_out, out, mask

    if initial_H is not None:
        H, matches, mask = refine(np.asarray(initial_H, float), diag)
    else:
        hyps = coarse_search(ref, mov_full, default_scales(scale_prior * fr if scale_prior else None),
                             default_angles(angle_prior), top_k=max_hypotheses)
        if not hyps:
            diag["failure_reason"] = "coarse search found no valid scale/rotation hypothesis"
            return DenseResult(None, [], np.zeros(0, bool), diag)
        diag["coarse_hypotheses"] = hyps[0].n_hypotheses
        local_px = int(min(480, max(ref.shape)))
        ranked = []
        tried = []
        for rank, coarse in enumerate(hyps):
            # local pose refinement at twice the coarse resolution
            a_tol, a_step = (4.0, 2.0) if angle_prior is not None else (6.0, 2.0)
            fine = coarse_search(ref, mov_full, [coarse.scale * 2.0 ** (k / 16.0) for k in range(-2, 3)],
                                 list(np.arange(coarse.angle - a_tol, coarse.angle + a_tol + 1e-6, a_step)),
                                 work_px=local_px)
            if fine is not None:
                coarse = fine
            qlog: Dict = {}
            _, qm, qmask = refine(np.linalg.inv(Dr) @ coarse.H, qlog, quick=True)
            nq = int(qmask.sum()) if len(qm) else 0
            ranked.append((nq, rank, coarse))
            tried.append({"rank": rank, "scale": round(coarse.scale / fr, 4), "angle_deg": round(float(coarse.angle), 2),
                          "coarse_distinct": round(coarse.distinct, 3), "quick_inliers": nq})
            if nq >= 20:  # >55 % of the 6x6 verification grid agrees: stop searching
                break
        ranked.sort(key=lambda t: -t[0])
        best = None
        for nq, rank, coarse in ranked[:2]:
            if nq < 6:
                break
            log: Dict = {}
            H, matches, mask = refine(np.linalg.inv(Dr) @ coarse.H, log)
            n_in = int(mask.sum()) if len(matches) else 0
            tried[[t["rank"] for t in tried].index(rank)]["inliers"] = n_in
            if best is None or n_in > best[0]:
                best = (n_in, H, matches, mask, coarse, log)
            if n_in >= max(min_inliers, int(0.4 * grid * grid)):
                break
        if best is None:
            coarse = ranked[0][2]
            best = (0, None, [], np.zeros(0, bool), coarse, {})
        n_in, H, matches, mask, coarse, log = best
        diag.update(log)
        diag.update(coarse_scale=round(coarse.scale / fr, 4), coarse_angle_deg=round(float(coarse.angle), 2),
                    coarse_ncc=round(coarse.score, 3), coarse_distinct=round(coarse.distinct, 3),
                    hypotheses_verified=tried)

    diag["ms"] = round((time.perf_counter() - t0) * 1000.0, 1)
    min_required = max(min_inliers, int(0.12 * grid * grid))
    if len(matches) == 0 or mask.sum() < min_required:
        diag.setdefault("failure_reason", f"too few verified structural correspondences ({int(mask.sum()) if len(matches) else 0} < {min_required})")
        return DenseResult(None, matches, np.zeros(len(matches), bool), diag)
    sane, why = homography_is_sane(H, mov_full.shape)
    if not sane:
        diag["failure_reason"] = f"degenerate homography: {why}"
        return DenseResult(None, matches, np.zeros(len(matches), bool), diag)
    src = np.float64([m.mov_pt for m in matches])[mask]
    dst = np.float64([m.ref_pt for m in matches])[mask]
    proj = cv2.perspectiveTransform(src.reshape(-1, 1, 2), H).reshape(-1, 2)
    diag["inlier_rmse_px"] = float(np.sqrt(np.mean(np.sum((proj - dst) ** 2, axis=1))))
    return DenseResult(H, matches, mask, diag)
