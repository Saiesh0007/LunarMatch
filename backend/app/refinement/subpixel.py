from typing import Any, Dict, Tuple

import numpy as np
import cv2
from scipy.ndimage import fourier_shift


def derive_gsd_meters_per_pixel(image_path: str) -> float:
    """Read projected raster pixel size from a georeferenced image.

    Args:
        image_path: Path to a raster image readable by rasterio.
    Returns:
        Pixel size in meters, or NaN when CRS/metadata is unavailable.
    Raises:
        None: Metadata and optional-dependency failures return NaN safely.
    """
    try:
        import rasterio
        with rasterio.open(image_path) as dataset:
            if dataset.crs is None:
                return float("nan")
            return float(abs(dataset.transform.a))
    except Exception:
        return float("nan")


def _extract_patch(image: np.ndarray, point: np.ndarray, patch_size: int) -> np.ndarray | None:
    half = patch_size // 2
    x, y = int(round(float(point[0]))), int(round(float(point[1])))
    if x - half < 0 or y - half < 0 or x + half > image.shape[1] or y + half > image.shape[0]:
        return None
    return np.ascontiguousarray(image[y - half:y + half, x - half:x + half], dtype=np.float32)


def _parabolic_offset(values: np.ndarray, index: int) -> Tuple[float, float]:
    left = float(values[(index - 1) % len(values)])
    center = float(values[index])
    right = float(values[(index + 1) % len(values)])
    curvature = left - 2.0 * center + right
    if curvature >= -1e-8:
        return 0.0, 16.0
    offset = 0.5 * (left - right) / curvature
    uncertainty = np.sqrt(max(0.0, 1.0 / (-curvature + 1e-8)))
    return float(np.clip(offset, -0.5, 0.5)), float(np.clip(uncertainty, 0.0, 16.0))


def _phase_correlation(src_patch: np.ndarray, ref_patch: np.ndarray, search_radius: int) -> Tuple[float, float, float, float, float]:
    window = np.outer(np.hanning(src_patch.shape[0]), np.hanning(src_patch.shape[1])).astype(np.float32)
    src_windowed = src_patch - float(src_patch.mean())
    ref_windowed = ref_patch - float(ref_patch.mean())
    offset, response = cv2.phaseCorrelate(src_windowed, ref_windowed, window=window)
    dx, dy = float(offset[0]), float(offset[1])
    if abs(dx) > search_radius or abs(dy) > search_radius:
        return dx, dy, 0.0, 16.0, 16.0
    source_fft = np.fft.fftn(src_windowed)
    target = ref_windowed - float(ref_windowed.mean())

    frequencies_y = np.fft.fftfreq(src_patch.shape[0])[:, None]
    frequencies_x = np.fft.fftfreq(src_patch.shape[1])[None, :]

    def scores(candidate_x: np.ndarray, candidate_y: np.ndarray) -> np.ndarray:
        phases = np.exp(-2j * np.pi * (candidate_y[:, None, None] * frequencies_y + candidate_x[:, None, None] * frequencies_x))
        translated = np.fft.ifftn(source_fft[None, :, :] * phases, axes=(-2, -1)).real
        denominators = np.linalg.norm(translated, axis=(-2, -1)) * np.linalg.norm(target)
        return np.divide(np.sum(translated * target[None, :, :], axis=(-2, -1)), denominators, out=np.full(len(candidate_x), -1.0), where=denominators > 1e-8)

    # Refine the phase-correlation seed against a local Fourier-shift correlation surface.
    for step, radius in ((0.1, 0.3), (0.02, 0.04)):
        x_candidates = np.arange(dx - radius, dx + radius + step / 2.0, step)
        y_candidates = np.arange(dy - radius, dy + radius + step / 2.0, step)
        x_scores = scores(x_candidates, np.full(len(x_candidates), dy))
        dx = float(x_candidates[int(np.argmax(x_scores))])
        y_scores = scores(np.full(len(y_candidates), dx), y_candidates)
        dy = float(y_candidates[int(np.argmax(y_scores))])
    uncertainty = float(np.clip((1.0 - float(response)) * 4.0, 0.0, 16.0))
    return dx, dy, float(np.clip(response, 0.0, 1.0)), uncertainty, uncertainty

    height, width = surface.shape
    candidate_rows = np.arange(-search_radius, search_radius + 1) % height
    candidate_cols = np.arange(-search_radius, search_radius + 1) % width
    local = surface[np.ix_(candidate_rows, candidate_cols)]
    local_index = np.unravel_index(int(np.argmax(local)), local.shape)
    row_index = int(candidate_rows[local_index[0]])
    col_index = int(candidate_cols[local_index[1]])
    row_shift = row_index if row_index <= height // 2 else row_index - height
    col_shift = col_index if col_index <= width // 2 else col_index - width
    row_values = surface[:, col_index]
    col_values = surface[row_index, :]
    row_offset, uncertainty_y = _parabolic_offset(row_values, row_index)
    col_offset, uncertainty_x = _parabolic_offset(col_values, col_index)
    local_rows = [(row_index + delta) % height for delta in (-1, 0, 1)]
    local_cols = [(col_index + delta) % width for delta in (-1, 0, 1)]
    peak = float(surface[np.ix_(local_rows, local_cols)].sum() / max(float(surface.sum()), 1e-8))
    return float(col_shift + col_offset), float(row_shift + row_offset), float(np.clip(peak, 0.0, 1.0)), uncertainty_x, uncertainty_y


def refine_subpixel(
    src_image: np.ndarray,
    ref_image: np.ndarray,
    src_points: np.ndarray,
    ref_points: np.ndarray,
    patch_size: int = 64,
    search_radius: int = 3,
    peak_response_threshold: float = 0.2,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """Refine matched points with local phase correlation.

    Args:
        src_image: Source grayscale image.
        ref_image: Reference grayscale image.
        src_points: Source coordinates with shape ``(N, 2)``.
        ref_points: Reference coordinates with shape ``(N, 2)``.
        patch_size: Side length of the square correlation patch.
        search_radius: Integer search radius around the zero-shift peak.
        peak_response_threshold: Minimum normalized peak response.
    Returns:
        Refined source points, refined reference points, and diagnostics.
    Raises:
        ValueError: If images, point arrays, or parameters are invalid.
    """
    src = np.asarray(src_image, dtype=np.float32)
    ref = np.asarray(ref_image, dtype=np.float32)
    source_points = np.asarray(src_points, dtype=np.float32)
    reference_points = np.asarray(ref_points, dtype=np.float32)
    if src.ndim != 2 or ref.ndim != 2 or source_points.shape != reference_points.shape or source_points.ndim != 2 or source_points.shape[1] != 2:
        raise ValueError("images must be 2D and points must have shape (N, 2)")
    if patch_size < 8 or search_radius < 0 or not 0.0 <= peak_response_threshold <= 1.0:
        raise ValueError("invalid patch or threshold parameters")
    refined_source = source_points.copy()
    refined_reference = reference_points.copy()
    results = []
    n_refined = 0
    n_out_of_bounds = 0
    residuals = []
    for match_id, (source_point, reference_point) in enumerate(zip(source_points, reference_points)):
        source_patch = _extract_patch(src, source_point, patch_size)
        reference_patch = _extract_patch(ref, reference_point, patch_size)
        if source_patch is None or reference_patch is None:
            n_out_of_bounds += 1
            results.append({"match_id": match_id, "residual_px": float("nan"), "uncertainty_x": float("nan"), "uncertainty_y": float("nan"), "peak_response": 0.0, "refinement_status": "rejected_out_of_bounds"})
            continue
        dx, dy, peak, uncertainty_x, uncertainty_y = _phase_correlation(source_patch, reference_patch, search_radius)
        if peak < peak_response_threshold:
            results.append({"match_id": match_id, "residual_px": float("nan"), "uncertainty_x": float("nan"), "uncertainty_y": float("nan"), "peak_response": peak, "refinement_status": "rejected_low_peak"})
            continue
        refined_reference[match_id] += np.array([dx, dy], dtype=np.float32)
        residual = float(np.hypot(dx, dy))
        residuals.append(residual)
        n_refined += 1
        results.append({"match_id": match_id, "residual_px": residual, "uncertainty_x": uncertainty_x, "uncertainty_y": uncertainty_y, "peak_response": peak, "refinement_status": "refined"})
    return refined_source, refined_reference, {
        "n_refined": n_refined,
        "n_rejected_refinement": len(results) - n_refined,
        "n_rejected_out_of_bounds": n_out_of_bounds,
        "per_match": results,
        "mean_residual_px": float(np.mean(residuals)) if residuals else float("nan"),
        "median_residual_px": float(np.median(residuals)) if residuals else float("nan"),
        "p95_residual_px": float(np.percentile(residuals, 95)) if residuals else float("nan"),
    }
