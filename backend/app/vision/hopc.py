from typing import List, Tuple

import cv2
import numpy as np
from scipy.ndimage import maximum_filter
from scipy.ndimage import rotate

from .rift2 import compute_phase_congruency_and_mim


def _normalise_gray(image_gray: np.ndarray) -> np.ndarray:
    if image_gray.ndim != 2:
        raise ValueError("image_gray must be a two-dimensional array")
    image = np.ascontiguousarray(image_gray, dtype=np.float32)
    if image.size and float(image.max()) > 1.0:
        image = image / 255.0
    return image


def _cell_histograms(response: np.ndarray, orientation: np.ndarray, cell_size: int, n_orientations: int) -> np.ndarray:
    height, width = response.shape
    cells_y = (height + cell_size - 1) // cell_size
    cells_x = (width + cell_size - 1) // cell_size
    histograms = np.zeros((cells_y, cells_x, n_orientations), dtype=np.float32)
    for cell_y in range(cells_y):
        y0, y1 = cell_y * cell_size, min(height, (cell_y + 1) * cell_size)
        for cell_x in range(cells_x):
            x0, x1 = cell_x * cell_size, min(width, (cell_x + 1) * cell_size)
            values = response[y0:y1, x0:x1]
            bins = orientation[y0:y1, x0:x1]
            for orientation_index in range(n_orientations):
                histograms[cell_y, cell_x, orientation_index] = np.sum(values[bins == orientation_index])
            cell_norm = np.linalg.norm(histograms[cell_y, cell_x])
            if cell_norm > 1e-6:
                histograms[cell_y, cell_x] /= cell_norm
    return histograms


def compute_hopc(
    image_gray: np.ndarray,
    n_orientations: int = 8,
    n_scales: int = 4,
    cell_size: int = 16,
    block_size: int = 6,
) -> np.ndarray:
    """Compute a dense Histogram of Oriented Phase Congruency map.

    Args:
        image_gray: Grayscale image in uint8 or float32 form.
        n_orientations: Number of orientation histogram bins.
        n_scales: Number of phase-congruency filter scales.
        cell_size: Spatial histogram cell size in pixels.
        block_size: Number of cells in each descriptor block.
    Returns:
        Float32 array of shape ``(H, W, n_orientations * block_size ** 2)``.
    Raises:
        ValueError: If dimensions or descriptor parameters are invalid.
    """
    if n_orientations < 1 or n_scales < 1 or cell_size < 1 or block_size < 1:
        raise ValueError("descriptor parameters must be positive")
    image = _normalise_gray(image_gray)
    pc_max, _, _, amplitudes = compute_phase_congruency_and_mim(
        image,
        n_scales=n_scales,
        n_orientations=n_orientations,
        return_amplitudes=True,
    )
    gradient_y, gradient_x = np.gradient(pc_max)
    magnitude = np.hypot(gradient_x, gradient_y).astype(np.float32)
    orientation = ((np.arctan2(gradient_y, gradient_x) + np.pi) / (2.0 * np.pi) * n_orientations).astype(np.int32) % n_orientations
    oriented_response = magnitude * np.mean(amplitudes, axis=2)
    histograms = _cell_histograms(oriented_response, orientation, cell_size, n_orientations)
    height, width = image.shape
    dense = np.zeros((height, width, n_orientations * block_size * block_size), dtype=np.float32)
    cells_y, cells_x = histograms.shape[:2]
    for cell_y in range(cells_y):
        y0, y1 = cell_y * cell_size, min(height, (cell_y + 1) * cell_size)
        for cell_x in range(cells_x):
            x0, x1 = cell_x * cell_size, min(width, (cell_x + 1) * cell_size)
            vector = []
            for block_y in range(block_size):
                source_y = min(max(cell_y - block_size // 2 + block_y, 0), cells_y - 1)
                for block_x in range(block_size):
                    source_x = min(max(cell_x - block_size // 2 + block_x, 0), cells_x - 1)
                    vector.extend(histograms[source_y, source_x])
            vector = np.asarray(vector, dtype=np.float32)
            norm = np.linalg.norm(vector)
            if norm > 1e-6:
                vector /= norm
                vector = np.minimum(vector, 0.2)
                vector /= max(np.linalg.norm(vector), 1e-6)
            dense[y0:y1, x0:x1] = vector
    return dense


def hopc_similarity(patch_src: np.ndarray, patch_ref: np.ndarray) -> float:
    """Compute orientation-shift-invariant HOPC similarity between patches.

    Args:
        patch_src: First grayscale image patch.
        patch_ref: Second grayscale image patch.
    Returns:
        Similarity in the inclusive range [0, 1].
    Raises:
        ValueError: If either patch is not a two-dimensional image.
    """
    src_image = _normalise_gray(patch_src)
    ref_image = _normalise_gray(patch_ref)
    src = compute_hopc(src_image).mean(axis=(0, 1))
    ref = compute_hopc(ref_image).mean(axis=(0, 1))
    orientations = 8
    block_count = len(src) // orientations
    if block_count == 0:
        return 0.0
    best = 0.0
    for shift in range(orientations):
        shifted = ref.reshape(block_count, orientations)
        shifted = np.roll(shifted, shift, axis=1).reshape(-1)
        denominator = np.linalg.norm(src) * np.linalg.norm(shifted)
        score = float(np.dot(src, shifted) / denominator) if denominator > 1e-6 else 0.0
        best = max(best, score)
    src_pc = compute_phase_congruency_and_mim(src_image)[0]
    ref_pc = compute_phase_congruency_and_mim(ref_image)[0]
    src_pc = (src_pc - src_pc.mean()) / (src_pc.std() + 1e-6)
    spatial_best = -1.0
    for angle in range(0, 360, 15):
        aligned = rotate(ref_pc, angle, reshape=False, order=1, mode="reflect")
        aligned = (aligned - aligned.mean()) / (aligned.std() + 1e-6)
        spatial_best = max(spatial_best, float(np.mean(src_pc * aligned)))
    score = spatial_best + 0.4 * (best - 0.5)
    return float(np.clip(score, 0.0, 1.0))


def hopc_keypoints_from_dense(image_gray: np.ndarray, hopc_map: np.ndarray, max_keypoints: int = 1000) -> Tuple[List[cv2.KeyPoint], np.ndarray]:
    """Subsample dense HOPC vectors at local descriptor-magnitude maxima.

    Args:
        image_gray: Source grayscale image.
        hopc_map: Dense map returned by :func:`compute_hopc`.
        max_keypoints: Maximum number of local maxima to retain.
    Returns:
        OpenCV keypoints and one HOPC descriptor per keypoint.
    Raises:
        ValueError: If the map shape or keypoint limit is invalid.
    """
    if hopc_map.ndim != 3 or max_keypoints < 1 or hopc_map.shape[:2] != image_gray.shape[:2]:
        raise ValueError("hopc_map must match the image and be three-dimensional")
    magnitude = np.linalg.norm(hopc_map, axis=2)
    maxima = magnitude == maximum_filter(magnitude, size=11, mode="nearest")
    ys, xs = np.nonzero(maxima)
    order = np.argsort(magnitude[ys, xs])[::-1][:max_keypoints]
    keypoints = [cv2.KeyPoint(float(xs[index]), float(ys[index]), 16.0, response=float(magnitude[ys[index], xs[index]])) for index in order]
    descriptors = np.asarray([hopc_map[ys[index], xs[index]] for index in order], dtype=np.float32)
    return keypoints, descriptors.reshape((-1, hopc_map.shape[2]))