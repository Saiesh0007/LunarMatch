from dataclasses import dataclass
from typing import List, Tuple

import cv2
import numpy as np
from scipy.spatial import KDTree

from ..models.schemas import MatchPairModel
from ..vision.rift2 import compute_phase_congruency, extract_rift2_on_pc


@dataclass
class PyramidLevel:
    level_idx: int
    scale: float
    image: np.ndarray


class LunarKeyPoint(cv2.KeyPoint):
    """OpenCV keypoint carrying the source pyramid level."""

    def __init__(self, x=0.0, y=0.0, size=0.0, angle=-1.0, response=0.0, octave=0, class_id=-1, pyramid_level=0):
        super().__init__(x=float(x), y=float(y), size=float(size), angle=float(angle), response=float(response), octave=int(octave), class_id=int(class_id))
        self.pyramid_level = int(pyramid_level)


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


def _deduplicate(
    keypoints: List[Tuple[float, float, float, int]],
    descriptors: np.ndarray,
    radius: float,
) -> Tuple[List[Tuple[float, float]], np.ndarray, np.ndarray]:
    if not keypoints:
        return [], np.empty((0, 216), dtype=np.float32), np.empty((0,), dtype=np.int8)
    points = np.asarray([(item[0], item[1]) for item in keypoints], dtype=np.float32)
    tree = KDTree(points)
    responses = np.asarray([item[2] for item in keypoints], dtype=np.float32)
    levels = np.asarray([item[3] for item in keypoints], dtype=np.int8)
    suppressed = np.zeros(len(keypoints), dtype=bool)
    retained = []
    for index in np.argsort(-responses):
        if suppressed[index]:
            continue
        retained.append(int(index))
        suppressed[tree.query_ball_point(points[index], r=radius)] = True
    retained.sort()
    return [tuple(map(float, points[i])) for i in retained], descriptors[retained], levels[retained]


def extract_rift2_multiscale(
    image_gray: np.ndarray,
    n_levels: int = 3,
    dedup_radius: float = 3.0,
) -> Tuple[List[Tuple[float, float]], np.ndarray, np.ndarray]:
    """Extract RIFT2 features from a phase-congruency pyramid.

    Args:
        image_gray: Grayscale image, uint8 or float32.
        n_levels: Number of pyramid levels.
        dedup_radius: Base-resolution suppression radius in pixels.
    Returns:
        Base-resolution keypoint coordinates, descriptors, and int8 levels.
    Raises:
        ValueError: If the image or pyramid arguments are invalid.
    """
    if image_gray.ndim not in (2, 3) or n_levels < 1 or dedup_radius <= 0:
        raise ValueError("invalid image, n_levels, or dedup_radius")
    levels = _build_pyramid_debug(image_gray, n_levels=n_levels)
    entries = []
    descriptor_parts = []
    for level_index, pc_level in enumerate(levels):
        keypoints, descriptors = extract_rift2_on_pc(pc_level, max_features=1000)
        if not keypoints or descriptors is None or len(descriptors) == 0:
            continue
        scale = 2.0 ** level_index
        for keypoint in keypoints:
            entries.append((keypoint.pt[0] * scale, keypoint.pt[1] * scale, max(float(keypoint.response), 1.0), level_index))
        descriptor_parts.append(descriptors.astype(np.float32))
    if not descriptor_parts:
        return [], np.empty((0, 216), dtype=np.float32), np.empty((0,), dtype=np.int8)
    return _deduplicate(entries, np.vstack(descriptor_parts), dedup_radius)


class MultiScalePyramid:
    """Compatibility wrapper for constructing fixed-factor image pyramids."""

    def __init__(self, num_levels: int = 3, scale_factor: float = 0.5):
        self.num_levels = num_levels
        self.scale_factor = scale_factor

    def build(self, image: np.ndarray) -> List[PyramidLevel]:
        current = _as_gray_float(image)
        result = []
        scale = 1.0
        for level_index in range(self.num_levels):
            result.append(PyramidLevel(level_index, scale, current))
            if level_index < self.num_levels - 1:
                current = cv2.resize(current, (0, 0), fx=self.scale_factor, fy=self.scale_factor, interpolation=cv2.INTER_AREA)
                scale *= self.scale_factor
        return result


class PyramidFeatureExtractor:
    """Compatibility adapter exposing the legacy extractor object API."""

    def __init__(self, base_extractor=None, num_levels: int = 3, scale_factor: float = 0.5):
        self.num_levels = num_levels
        self.scale_factor = scale_factor

    def extract(self, image: np.ndarray):
        points, descriptors, levels = extract_rift2_multiscale(image, self.num_levels)
        keypoints = [LunarKeyPoint(x, y, 96.0, response=1.0, octave=int(level), pyramid_level=int(level)) for (x, y), level in zip(points, levels)]
        return keypoints, descriptors

    @staticmethod
    def deduplicate_kdtree(kps_with_meta, descriptors, radius_px=3.0):
        entries = [(kp.pt[0] / scale, kp.pt[1] / scale, max(float(kp.response), 1.0), level) for kp, scale, level in kps_with_meta]
        points, dedup_desc, levels = _deduplicate(entries, descriptors, radius_px)
        keypoints = [LunarKeyPoint(x, y, 96.0, response=1.0, octave=int(level), pyramid_level=int(level)) for (x, y), level in zip(points, levels)]
        return keypoints, dedup_desc


def filter_cross_scale_matches(matches: List[MatchPairModel], levels_ref: List[int], levels_mov: List[int], max_level_diff: int = 1) -> List[MatchPairModel]:
    """Keep matches whose pyramid levels differ by at most ``max_level_diff``."""
    return [m for m in matches if m.ref_idx >= len(levels_ref) or m.mov_idx >= len(levels_mov) or abs(int(levels_ref[m.ref_idx]) - int(levels_mov[m.mov_idx])) <= max_level_diff]
from dataclasses import dataclass
from typing import List, Tuple, Optional, Any
import numpy as np
import cv2
from scipy.spatial import KDTree
from ..vision.extractor import BaseFeatureExtractor
from ..models.schemas import MatchPairModel
from ..utils.logging import logger

@dataclass
class PyramidLevel:
    level_idx: int
    scale: float
    image: np.ndarray

class LunarKeyPoint(cv2.KeyPoint):
    """
    Subclass of cv2.KeyPoint carrying explicit pyramid_level and scale metadata.
    Fully compatible with OpenCV C++ functions while exposing pyramid_level.
    """
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        size: float = 0.0,
        angle: float = -1.0,
        response: float = 0.0,
        octave: int = 0,
        class_id: int = -1,
        pyramid_level: int = 0,
    ):
        super().__init__(
            x=float(x),
            y=float(y),
            size=float(size),
            angle=float(angle),
            response=float(response),
            octave=int(octave),
            class_id=int(class_id),
        )
        self.pyramid_level = int(pyramid_level)

class MultiScalePyramid:
    """
    Multi-scale pyramid without extra cross-level Gaussian blurring.
    Preserves crisp phase congruency edge/corner responses across scales (0.5x, 0.25x).
    """

    def __init__(self, num_levels: int = 3, scale_factor: float = 0.5):
        self.num_levels = num_levels
        self.scale_factor = scale_factor

    def build(self, img: np.ndarray) -> List[PyramidLevel]:
        """Build multi-scale pyramid levels using area/bilinear decimation."""
        if len(img.shape) == 3:
            base = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            base = img.copy()

        levels: List[PyramidLevel] = []
        current = base
        current_scale = 1.0

        for lvl in range(self.num_levels):
            levels.append(PyramidLevel(level_idx=lvl, scale=current_scale, image=current))

            if lvl < self.num_levels - 1:
                # Downsample by scale_factor using INTER_AREA to avoid high-frequency aliasing
                # while avoiding Gaussian pre-smoothing which attenuates phase congruency
                h, w = current.shape[:2]
                new_w = max(32, int(round(w * self.scale_factor)))
                new_h = max(32, int(round(h * self.scale_factor)))
                current = cv2.resize(current, (new_w, new_h), interpolation=cv2.INTER_AREA)
                current_scale *= self.scale_factor

        return levels

class PyramidFeatureExtractor:
    """
    Multi-scale feature extractor:
    - Runs base extractor (e.g. RIFT2) at each pyramid level independently at native patch scale.
    - Projects keypoint coordinates back to base resolution.
    - Attaches pyramid_level metadata.
    - Deduplicates redundant keypoints using scipy.spatial.KDTree within radius_px.
    """

    def __init__(self, base_extractor: BaseFeatureExtractor, num_levels: int = 3, scale_factor: float = 0.5):
        self.base_extractor = base_extractor
        self.pyramid = MultiScalePyramid(num_levels=num_levels, scale_factor=scale_factor)

    def extract(self, img: np.ndarray) -> Tuple[List[cv2.KeyPoint], np.ndarray]:
        """Extract multi-scale keypoints and descriptors projected to base resolution."""
        levels = self.pyramid.build(img)
        all_kps_with_meta: List[Tuple[cv2.KeyPoint, float, int]] = []
        all_descriptors_list: List[np.ndarray] = []

        for lvl in levels:
            kps_lvl, desc_lvl = self.base_extractor.extract(lvl.image)
            if len(kps_lvl) == 0 or desc_lvl is None or len(desc_lvl) == 0:
                continue

            for idx, kp in enumerate(kps_lvl):
                all_kps_with_meta.append((kp, lvl.scale, lvl.level_idx))
                all_descriptors_list.append(desc_lvl[idx])

        if not all_descriptors_list:
            desc_dim = 216
            return [], np.empty((0, desc_dim), dtype=np.float32)

        stacked_descs = np.vstack(all_descriptors_list).astype(np.float32)

        # Deduplicate using KD-Tree within 3.0 px radius
        dedup_kps, dedup_descs = self.deduplicate_kdtree(all_kps_with_meta, stacked_descs, radius_px=3.0)

        logger.info(
            f"Pyramid Feature Extraction ({len(levels)} levels): {len(all_kps_with_meta)} raw -> "
            f"{len(dedup_kps)} deduplicated keypoints"
        )
        return dedup_kps, dedup_descs

    @staticmethod
    def deduplicate_kdtree(
        kps_with_meta: List[Tuple[cv2.KeyPoint, float, int]],
        descriptors: np.ndarray,
        radius_px: float = 3.0,
    ) -> Tuple[List[cv2.KeyPoint], np.ndarray]:
        """
        Deduplicate keypoints projected to base image resolution using KDTree.
        If multiple keypoints fall within radius_px, retain the one with highest response.
        """
        if len(kps_with_meta) == 0:
            return [], np.empty((0, descriptors.shape[1] if descriptors.ndim > 1 else 216), dtype=np.float32)

        # Compute projected coordinates at base resolution
        proj_pts: List[Tuple[float, float]] = []
        projected_kps: List[cv2.KeyPoint] = []

        for kp, scale, lvl_idx in kps_with_meta:
            px = kp.pt[0] / scale
            py = kp.pt[1] / scale
            proj_pts.append((px, py))

            # Create LunarKeyPoint with base coordinate and level attribute
            base_kp = LunarKeyPoint(
                x=float(px),
                y=float(py),
                size=float(kp.size / scale),
                angle=float(kp.angle),
                response=float(kp.response if kp.response > 0 else 1.0),
                octave=int(lvl_idx),
                pyramid_level=int(lvl_idx),
            )
            projected_kps.append(base_kp)

        pts_arr = np.array(proj_pts, dtype=np.float32)
        kdtree = KDTree(pts_arr)

        # Sort indices by response descending
        responses = np.array([kp.response for kp in projected_kps], dtype=np.float32)
        sorted_indices = np.argsort(-responses)

        retained_indices: List[int] = []
        suppressed = np.zeros(len(kps_with_meta), dtype=bool)

        for idx in sorted_indices:
            if suppressed[idx]:
                continue
            retained_indices.append(idx)
            # Find neighbors within radius_px
            neighbors = kdtree.query_ball_point(pts_arr[idx], r=radius_px)
            suppressed[neighbors] = True

        retained_indices = sorted(retained_indices)
        final_kps = [projected_kps[i] for i in retained_indices]
        final_descs = descriptors[retained_indices]

        return final_kps, final_descs

def filter_cross_scale_matches(
    matches: List[MatchPairModel],
    levels_ref: List[int],
    levels_mov: List[int],
    max_level_diff: int = 1,
) -> List[MatchPairModel]:
    """
    Enforce pyramid level difference constraint |level_s - level_r| <= max_level_diff.
    Prevents cross-scale aliasing between distant pyramid levels (e.g. level 0 and level 2).
    """
    filtered: List[MatchPairModel] = []
    for m in matches:
        if m.ref_idx < len(levels_ref) and m.mov_idx < len(levels_mov):
            lvl_r = levels_ref[m.ref_idx]
            lvl_m = levels_mov[m.mov_idx]
            if abs(lvl_r - lvl_m) <= max_level_diff:
                filtered.append(m)
        else:
            # If metadata not available, keep match
            filtered.append(m)
    return filtered
