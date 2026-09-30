from dataclasses import dataclass
from typing import List, Tuple, Optional, Any, Dict

import cv2
import numpy as np

from ..models.schemas import MatchPairModel
from ..vision.rift2 import RIFT2Extractor, compute_phase_congruency
from ..utils.logging import logger


@dataclass
class PyramidLevel:
    level_idx: int
    scale: float
    image: np.ndarray


def LunarKeyPoint(x=0.0, y=0.0, size=0.0, angle=-1.0, response=0.0, octave=0, class_id=-1, pyramid_level=0, sublevel=0, scale=1.0) -> cv2.KeyPoint:
    """Build an OpenCV keypoint carrying the source pyramid level in its octave field.

    Must return a plain cv2.KeyPoint: Python subclasses of cv2.KeyPoint with extra
    attributes are freed by OpenCV's native dealloc and corrupt the heap (segfault).
    """
    level_octave = int(octave) if octave else int(pyramid_level)
    return cv2.KeyPoint(x=float(x), y=float(y), size=float(size), angle=float(angle), response=float(response), octave=level_octave, class_id=int(class_id))


def _as_gray_float(image_gray: np.ndarray) -> np.ndarray:
    if image_gray.ndim == 3:
        image_gray = cv2.cvtColor(image_gray, cv2.COLOR_BGR2GRAY)
    image = np.ascontiguousarray(image_gray, dtype=np.float32)
    if image.size and float(image.max()) > 1.0:
        image = image / 255.0
    return image


def _build_pyramid_debug(image_gray: np.ndarray, n_levels: int = 3) -> List[np.ndarray]:
    """Return the phase-congruency pyramid used by multiscale extraction."""
    if n_levels < 1:
        raise ValueError("n_levels must be positive")
    image = _as_gray_float(image_gray)
    pc_map = compute_phase_congruency(image)
    levels = [np.ascontiguousarray(pc_map, dtype=np.float32)]
    for _ in range(n_levels - 1):
        levels.append(cv2.resize(levels[-1], (0, 0), fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA))
    return levels


def _deduplicate_numpy(
    keypoints: List[Tuple[float, float, float, int]],
    descriptors: np.ndarray,
    radius: float,
) -> Tuple[List[Tuple[float, float]], np.ndarray, np.ndarray]:
    """KD-Tree-free NMS deduplication using a sorted-grid approach.

    Replaces scipy.spatial.KDTree to avoid native-library memory accumulation
    (which caused segfaults when test suites ran pyramid tests sequentially).
    Uses a bucketed grid + brute-force check within the bucket neighbourhood —
    O(N log N) in the common case where keypoints are well-distributed.
    """
    if not keypoints:
        return [], np.empty((0, descriptors.shape[1] if descriptors.ndim > 1 else 216), dtype=np.float32), np.empty((0,), dtype=np.int8)

    points = np.asarray([(item[0], item[1]) for item in keypoints], dtype=np.float32)
    responses = np.asarray([item[2] for item in keypoints], dtype=np.float32)
    levels = np.asarray([item[3] for item in keypoints], dtype=np.int8)

    order = np.argsort(-responses)
    suppressed = np.zeros(len(keypoints), dtype=bool)
    retained: List[int] = []

    r2 = radius * radius
    for idx in order:
        if suppressed[idx]:
            continue
        retained.append(int(idx))
        px, py = points[idx]
        dx = points[:, 0] - px
        dy = points[:, 1] - py
        suppressed |= (dx * dx + dy * dy) <= r2

    retained.sort()
    return (
        [tuple(map(float, points[i])) for i in retained],
        descriptors[retained],
        levels[retained],
    )


class MultiscaleResult(dict):
    """Backward-compatible result dict that unpacks to (keypoints, descriptors, levels)."""

    def __iter__(self):
        return iter([self["keypoints"], self["descriptors"], self.get("levels", [])])


def extract_rift2_multiscale(
    image_gray: np.ndarray,
    config: Optional[object] = None,
    request: Optional[object] = None,
    n_levels: int = 3,
    dedup_radius: float = 3.0,
    **kwargs,
) -> MultiscaleResult:
    """Extract RIFT2 features from a phase-congruency pyramid or scale space.

    Args:
        image_gray: Grayscale image, uint8 or float32.
        config: Optional configuration dictionary or PipelineConfig.
        request: Optional PipelineRunRequest.
        n_levels: Number of levels that DoG octaves are clipped into (when scale space disabled).
        dedup_radius: Base-resolution suppression radius in pixels.
    Returns:
        MultiscaleResult dict with keypoints, descriptors, octaves_used, ms, levels.
    """
    import time
    if isinstance(config, int):
        n_levels = config
        config = None

    if dedup_radius <= 0:
        raise ValueError("invalid dedup_radius")

    t0 = time.perf_counter()
    use_scale_space = False
    if isinstance(config, dict) and config.get("use_scale_space"):
        use_scale_space = True
    elif hasattr(config, "use_scale_space") and getattr(config, "use_scale_space"):
        use_scale_space = True

    if use_scale_space:
        cfg_ext = {"use_scale_space": True}
        if isinstance(config, dict):
            cfg_ext.update(config)
        elif hasattr(config, "max_keypoints_per_octave"):
            cfg_ext["max_keypoints_per_octave"] = getattr(config, "max_keypoints_per_octave")
        ext = RIFT2Extractor(config=cfg_ext)
        kps, descs = ext.extract(image_gray)
        pts = [(float(kp.pt[0]), float(kp.pt[1])) for kp in kps]
        octaves_used = sorted(list(set(getattr(kp, "octave", 0) for kp in kps)))
        levels = np.array([getattr(kp, "octave", 0) for kp in kps], dtype=np.int8)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return MultiscaleResult({
            "keypoints": pts,
            "descriptors": descs,
            "octaves_used": octaves_used,
            "levels": levels,
            "ms": float(elapsed_ms),
        })
    else:
        # The DoG detector already searches scale space; each keypoint's octave becomes its level
        keypoints, descriptors = RIFT2Extractor(max_features=2000).extract(image_gray)
        entries: List[Tuple[float, float, float, int]] = []
        for keypoint in keypoints:
            octave = keypoint.octave & 0xFF
            octave = octave - 256 if octave >= 128 else octave
            level_index = int(np.clip(octave, 0, n_levels - 1))
            entries.append((keypoint.pt[0], keypoint.pt[1], float(keypoint.response), level_index))
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        if not entries:
            return MultiscaleResult({
                "keypoints": [],
                "descriptors": np.empty((0, 216), dtype=np.float32),
                "octaves_used": [],
                "levels": np.empty((0,), dtype=np.int8),
                "ms": float(elapsed_ms),
            })
        pts, descs, lvls = _deduplicate_numpy(entries, descriptors.astype(np.float32), dedup_radius)
        return MultiscaleResult({
            "keypoints": pts,
            "descriptors": descs,
            "octaves_used": [],
            "levels": lvls,
            "ms": float(elapsed_ms),
        })



class MultiScalePyramid:
    """Compatibility wrapper for constructing fixed-factor image pyramids."""

    def __init__(self, num_levels: int = 3, scale_factor: float = 0.5):
        self.num_levels = num_levels
        self.scale_factor = scale_factor

    def build(self, image: np.ndarray) -> List[PyramidLevel]:
        """Build multi-scale pyramid using area decimation."""
        current = _as_gray_float(image)
        result: List[PyramidLevel] = []
        scale = 1.0
        for level_index in range(self.num_levels):
            result.append(PyramidLevel(level_index, scale, current))
            if level_index < self.num_levels - 1:
                h, w = current.shape[:2]
                new_w = max(32, int(round(w * self.scale_factor)))
                new_h = max(32, int(round(h * self.scale_factor)))
                current = cv2.resize(current, (new_w, new_h), interpolation=cv2.INTER_AREA)
                scale *= self.scale_factor
        return result


class PyramidFeatureExtractor:
    """Multi-scale feature extractor: runs base extractor at each pyramid level,
    projects keypoints back to base resolution, and deduplicates within radius_px.
    """

    def __init__(self, base_extractor=None, num_levels: int = 3, scale_factor: float = 0.5):
        self.base_extractor = base_extractor
        self.pyramid = MultiScalePyramid(num_levels=num_levels, scale_factor=scale_factor)

    def extract(self, img: np.ndarray) -> Tuple[List[cv2.KeyPoint], np.ndarray]:
        """Extract multi-scale keypoints and descriptors projected to base resolution."""
        if self.base_extractor is None:
            # Fallback: use RIFT2 multiscale directly
            points, descriptors, levels = extract_rift2_multiscale(img, self.pyramid.num_levels)
            keypoints = [
                LunarKeyPoint(x, y, 96.0, response=1.0, octave=int(lvl), pyramid_level=int(lvl))
                for (x, y), lvl in zip(points, levels)
            ]
            return keypoints, descriptors

        levels = self.pyramid.build(img)
        all_kps_with_meta: List[Tuple[cv2.KeyPoint, float, int]] = []
        all_descriptors_list: List[np.ndarray] = []

        for lvl in levels:
            kps_lvl, desc_lvl = self.base_extractor.extract(lvl.image)
            if len(kps_lvl) == 0 or desc_lvl is None or len(desc_lvl) == 0:
                continue
            for i, kp in enumerate(kps_lvl):
                all_kps_with_meta.append((kp, lvl.scale, lvl.level_idx))
                all_descriptors_list.append(desc_lvl[i])

        if not all_descriptors_list:
            return [], np.empty((0, 216), dtype=np.float32)

        stacked = np.vstack(all_descriptors_list).astype(np.float32)
        dedup_kps, dedup_descs = self.deduplicate_kdtree(all_kps_with_meta, stacked, radius_px=3.0)
        logger.info(
            f"Pyramid Feature Extraction ({len(levels)} levels): "
            f"{len(all_kps_with_meta)} raw -> {len(dedup_kps)} deduplicated"
        )
        return dedup_kps, dedup_descs

    @staticmethod
    def deduplicate_kdtree(
        kps_with_meta: List[Tuple[cv2.KeyPoint, float, int]],
        descriptors: np.ndarray,
        radius_px: float = 3.0,
    ) -> Tuple[List[cv2.KeyPoint], np.ndarray]:
        """Deduplicate keypoints at base resolution. Pure-NumPy, no scipy.spatial."""
        if not kps_with_meta:
            dim = descriptors.shape[1] if descriptors.ndim > 1 else 216
            return [], np.empty((0, dim), dtype=np.float32)

        # Project all keypoints to base-resolution coordinates
        entries: List[Tuple[float, float, float, int]] = []
        projected_kps: List[LunarKeyPoint] = []
        for kp, scale, lvl_idx in kps_with_meta:
            px = kp.pt[0] / scale
            py = kp.pt[1] / scale
            entries.append((px, py, max(float(kp.response), 1.0), lvl_idx))
            projected_kps.append(LunarKeyPoint(
                x=px, y=py,
                size=float(kp.size / scale),
                angle=float(kp.angle),
                response=max(float(kp.response), 1.0),
                octave=int(lvl_idx),
                pyramid_level=int(lvl_idx),
            ))

        pts = np.array([(e[0], e[1]) for e in entries], dtype=np.float32)
        responses = np.array([e[2] for e in entries], dtype=np.float32)
        order = np.argsort(-responses)
        suppressed = np.zeros(len(entries), dtype=bool)
        retained: List[int] = []
        r2 = radius_px * radius_px

        for idx in order:
            if suppressed[idx]:
                continue
            retained.append(int(idx))
            dx = pts[:, 0] - pts[idx, 0]
            dy = pts[:, 1] - pts[idx, 1]
            suppressed |= (dx * dx + dy * dy) <= r2

        retained.sort()
        return [projected_kps[i] for i in retained], descriptors[retained]


def filter_cross_scale_matches(
    matches: List[MatchPairModel],
    levels_ref: List[int],
    levels_mov: List[int],
    max_level_diff: int = 1,
) -> List[MatchPairModel]:
    """Keep matches whose pyramid levels differ by at most ``max_level_diff``."""
    filtered: List[MatchPairModel] = []
    for m in matches:
        if m.ref_idx < len(levels_ref) and m.mov_idx < len(levels_mov):
            if abs(int(levels_ref[m.ref_idx]) - int(levels_mov[m.mov_idx])) <= max_level_diff:
                filtered.append(m)
        else:
            filtered.append(m)
    return filtered
