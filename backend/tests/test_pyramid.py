import pytest
import numpy as np
import cv2
from app.preprocessing.pyramid import (
    MultiScalePyramid,
    PyramidFeatureExtractor,
    filter_cross_scale_matches,
)
from app.vision.rift2 import RIFT2Extractor
from app.models.schemas import MatchPairModel

def create_synthetic_lunar_patch(size: int = 512, seed: int = 26166) -> np.ndarray:
    """Generate synthetic crater image for scale testing."""
    rng = np.random.RandomState(seed)
    img = np.zeros((size, size), dtype=np.float32)
    img += rng.normal(100.0, 15.0, (size, size))
    # Prominent craters of various radii
    craters = [(150, 150, 60), (320, 300, 90), (180, 380, 45), (380, 140, 50)]
    for cx, cy, r in craters:
        y, x = np.ogrid[:size, :size]
        dist = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
        cavity = dist < r
        img[cavity] -= 45.0 * (1.0 - dist[cavity] / r)
        rim = (dist >= r - 6) & (dist <= r + 6)
        angle = np.arctan2(y - cy, x - cx)
        sun_align = np.cos(angle - (-np.pi / 4))
        img[rim] += 60.0 * sun_align[rim]
    return np.clip(img, 0, 255).astype(np.uint8)

class TestPyramid:
    """Test suite for Multi-Scale Gaussian/Phase Congruency Pyramid."""

    def test_pyramid_level_dimensions(self):
        """Verify pyramid produces 3 levels with scale factors 1.0, 0.5, 0.25 without extra blurring."""
        img = create_synthetic_lunar_patch(size=512)
        pyr = MultiScalePyramid(num_levels=3, scale_factor=0.5)
        levels = pyr.build(img)

        assert len(levels) == 3
        # Level 0: 512x512
        assert levels[0].image.shape == (512, 512)
        assert levels[0].scale == 1.0
        assert levels[0].level_idx == 0

        # Level 1: 256x256
        assert levels[1].image.shape == (256, 256)
        assert levels[1].scale == 0.5
        assert levels[1].level_idx == 1

        # Level 2: 128x128
        assert levels[2].image.shape == (128, 128)
        assert levels[2].scale == 0.25
        assert levels[2].level_idx == 2

    def test_kdtree_deduplication(self):
        """Verify KDTree deduplication within 3 px radius on projected coordinates."""
        pyr_ext = PyramidFeatureExtractor(base_extractor=RIFT2Extractor(max_features=200), num_levels=3)
        # Create keypoints at multiple levels with identical projected base coordinates
        kp0 = cv2.KeyPoint(100.0, 100.0, 16.0)
        kp1 = cv2.KeyPoint(50.1, 50.1, 16.0)  # at scale 0.5 -> projected (100.2, 100.2) within 3px!
        kp2 = cv2.KeyPoint(200.0, 200.0, 16.0)

        # Attach metadata
        setattr(kp0, "pyramid_level", 0)
        setattr(kp1, "pyramid_level", 1)
        setattr(kp2, "pyramid_level", 0)

        kps_with_scales = [(kp0, 1.0, 0), (kp1, 0.5, 1), (kp2, 1.0, 0)]
        descs = np.ones((3, 216), dtype=np.float32)

        dedup_kps, dedup_descs = pyr_ext.deduplicate_kdtree(kps_with_scales, descs, radius_px=3.0)
        assert len(dedup_kps) == 2, f"Expected 2 unique keypoints after deduplication, got {len(dedup_kps)}"
        assert dedup_descs.shape[0] == 2

    def test_feature_detection_under_artificial_downsampling(self):
        """Verify features at scale 0.5 are detected and cross-scale correspondence succeeds."""
        img_base = create_synthetic_lunar_patch(size=512, seed=26166)
        # Downsample artificially by 0.5x
        img_down = cv2.resize(img_base, (256, 256), interpolation=cv2.INTER_AREA)

        extractor = PyramidFeatureExtractor(base_extractor=RIFT2Extractor(max_features=250), num_levels=3)
        kps_base, descs_base = extractor.extract(img_base)
        kps_down, descs_down = extractor.extract(img_down)

        assert len(kps_base) >= 30
        assert len(kps_down) >= 20

        # Verify keypoints carry pyramid_level attribute
        for kp in kps_base:
            assert hasattr(kp, "pyramid_level"), "Keypoint must record pyramid_level metadata"

        # Match across scales
        bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
        raw_matches = bf.knnMatch(descs_base, descs_down, k=2)
        good = [m[0] for m in raw_matches if len(m) == 2 and m[0].distance < 0.88 * m[1].distance]

        assert len(good) >= 8, f"Expected at least 8 cross-scale matches under 0.5x downsampling, got {len(good)}"

        # Verify scale recovery: pts_base / pts_down should have ratio ~ 2.0 (512 / 256)
        scale_ratios = []
        for m in good:
            p_base = np.array(kps_base[m.queryIdx].pt)
            p_down = np.array(kps_down[m.trainIdx].pt)
            # Distance from center
            d_base = np.linalg.norm(p_base - 256.0)
            d_down = np.linalg.norm(p_down - 128.0)
            if d_down > 20.0:
                scale_ratios.append(d_base / d_down)

        if scale_ratios:
            median_scale = np.median(scale_ratios)
            # Expect scale ratio close to 2.0 (+/- 0.35)
            assert abs(median_scale - 2.0) < 0.35, f"Recovered scale ratio {median_scale:.2f} diverges from 2.0"

    def test_scale_level_matching_constraint(self):
        """Verify enforcement of |level_s - level_r| <= 1."""
        matches = [
            MatchPairModel(ref_idx=0, mov_idx=0, distance=0.2, ref_pt=[10, 10], mov_pt=[10, 10]),
            MatchPairModel(ref_idx=1, mov_idx=1, distance=0.3, ref_pt=[20, 20], mov_pt=[20, 20]),
            MatchPairModel(ref_idx=2, mov_idx=2, distance=0.4, ref_pt=[30, 30], mov_pt=[30, 30]),
        ]
        # Levels for ref: [0, 0, 0]
        # Levels for mov: [0, 1, 2] -> index 2 has |0 - 2| = 2 > 1 (must be rejected!)
        levels_ref = [0, 0, 0]
        levels_mov = [0, 1, 2]

        filtered = filter_cross_scale_matches(matches, levels_ref, levels_mov, max_level_diff=1)
        assert len(filtered) == 2, f"Expected 2 matches (|level_diff| <= 1), got {len(filtered)}"
        assert filtered[0].ref_idx == 0
        assert filtered[1].ref_idx == 1
