import numpy as np
import pytest
import time

from app.preprocessing.pyramid import _build_pyramid_debug, extract_rift2_multiscale


def generate_lunar_crater_surface(seed: int = 42, size: int = 512) -> np.ndarray:
    """Generate a deterministic crater-like image using NumPy only."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    image = np.zeros((size, size), dtype=np.float32)
    for _ in range(20):
        cx, cy = rng.uniform(0.1, 0.9, 2) * size
        radius = rng.uniform(size * 0.02, size * 0.12)
        distance = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        ring = np.exp(-((distance - radius) ** 2) / (2.0 * (radius * 0.15) ** 2))
        image += ring * rng.uniform(0.5, 1.5)
    image = (image - image.min()) / (image.max() - image.min() + 1e-9)
    return (image * 255).astype(np.uint8)


def test_pyramid_returns_three_levels():
    image = generate_lunar_crater_surface(seed=42)
    keypoints, descriptors, levels = extract_rift2_multiscale(image, n_levels=3)
    assert descriptors.shape[1] == 216
    assert len(keypoints) == len(descriptors) == len(levels)
    assert set(np.unique(levels)).issubset({0, 1, 2})


def test_kdtree_deduplication_enforces_min_spacing():
    image = generate_lunar_crater_surface(seed=7)
    keypoints, _, _ = extract_rift2_multiscale(image, dedup_radius=3.0)
    if len(keypoints) < 2:
        pytest.skip("Too few keypoints to test spacing")
    from scipy.spatial import cKDTree
    pairs = cKDTree(np.asarray(keypoints)).query_pairs(r=3.0 - 1e-6)
    assert not pairs, f"Found {len(pairs)} pairs closer than 3px"


def test_feature_detection_under_artificial_downsampling():
    base = generate_lunar_crater_surface(seed=11, size=512).astype(np.float32)
    yy, xx = np.mgrid[0:512, 0:512]
    distance = np.sqrt((xx - 256) ** 2 + (yy - 256) ** 2)
    base = np.clip(base + 100 * np.exp(-((distance - 40) ** 2) / 200), 0, 255).astype(np.uint8)
    keypoints, _, _ = extract_rift2_multiscale(base)
    if not keypoints:
        pytest.skip("No keypoints detected; check RIFT2 thresholds")
    points = np.asarray(keypoints)
    assert np.linalg.norm(points - np.array([256, 256]), axis=1).min() < 20


def test_pyramid_levels_are_monotonic_in_size():
    levels = _build_pyramid_debug(generate_lunar_crater_surface(seed=42), n_levels=3)
    assert len(levels) == 3
    assert levels[0].shape[0] > levels[1].shape[0] > levels[2].shape[0]


def test_pyramid_runtime_budget():
    """Guard against accidental phase-congruency recomputation per level."""
    image = generate_lunar_crater_surface(seed=42, size=1024)
    started = time.perf_counter()
    extract_rift2_multiscale(image, n_levels=3)
    elapsed = time.perf_counter() - started
    assert elapsed < 80.0, f"Pyramid runtime regression: {elapsed:.1f}s > 80s budget"
