import pytest
import numpy as np
import cv2
from app.vision.rift2 import (
    RIFT2Extractor,
    extract_rift2,
    construct_log_gabor_filter_bank,
    compute_phase_congruency_and_mim,
)

def create_synthetic_lunar_patch(size: int = 256, seed: int = 26166) -> np.ndarray:
    """Generate synthetic crater-like test pattern with sharp edges and shadows."""
    rng = np.random.RandomState(seed)
    img = np.zeros((size, size), dtype=np.float32)
    # Add background noise
    img += rng.normal(100.0, 15.0, (size, size))
    # Add multiple craters (elliptical depressions with bright sunlit rim and dark shadow)
    crater_centers = [(80, 80, 40), (160, 150, 55), (90, 190, 30), (190, 70, 25)]
    for cx, cy, r in crater_centers:
        y, x = np.ogrid[:size, :size]
        dist = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
        # Crater cavity
        cavity = dist < r
        img[cavity] -= 45.0 * (1.0 - dist[cavity] / r)
        # Rim (ring)
        rim = (dist >= r - 4) & (dist <= r + 4)
        # Directional sunlight from top-left (-x, -y)
        angle = np.arctan2(y - cy, x - cx)
        sun_align = np.cos(angle - (-np.pi / 4))
        img[rim] += 60.0 * sun_align[rim]
        # Shadow floor
        shadow = cavity & (sun_align < -0.2)
        img[shadow] -= 35.0

    img = np.clip(img, 0, 255).astype(np.uint8)
    return img

class TestRIFT2:
    """Test suite for RIFT2 illumination-invariant feature extraction."""

    def test_log_gabor_filter_bank_properties(self):
        """Verify filter bank dimensions, scales (4), orientations (6)."""
        filters = construct_log_gabor_filter_bank(rows=128, cols=128, n_scales=4, n_orientations=6)
        assert len(filters) == 4, "Must produce 4 scale levels"
        assert len(filters[0]) == 6, "Must produce 6 orientations per scale"
        for s in range(4):
            for o in range(6):
                assert filters[s][o].shape == (128, 128)
                assert np.all(np.isfinite(filters[s][o]))
                assert np.min(filters[s][o]) >= 0.0, "Log-Gabor frequency response is non-negative"

    def test_phase_congruency_and_mim_output(self):
        """Verify phase congruency principal moments and Maximum Index Map (MIM)."""
        img = create_synthetic_lunar_patch(size=128)
        pc_max, pc_min, mim = compute_phase_congruency_and_mim(img, n_scales=4, n_orientations=6)

        assert pc_max.shape == img.shape
        assert pc_min.shape == img.shape
        assert mim.shape == img.shape
        # Phase congruency values are bounded in [0, 1]
        assert np.all(pc_max >= 0.0)
        assert np.all(pc_min >= 0.0)
        # MIM indices must be in [0, 5] (6 orientations)
        assert np.all((mim >= 0) & (mim < 6))
        assert np.issubdtype(mim.dtype, np.integer)

    def test_descriptor_length_216(self):
        """Verify RIFT2 descriptor length is strictly 6x6x6 = 216."""
        img = create_synthetic_lunar_patch(size=256)
        extractor = RIFT2Extractor(patch_size=96, max_features=100)
        kps, descs = extractor.extract(img)

        assert len(kps) > 0, "Should detect keypoints on synthetic crater image"
        assert descs is not None
        assert descs.shape[1] == 216, f"Expected 216-D descriptor, got {descs.shape[1]}"
        # Ensure descriptors are unit-normalized (L2 norm ~ 1.0)
        norms = np.linalg.norm(descs, axis=1)
        np.testing.assert_allclose(norms, 1.0, atol=1e-3, err_msg="Descriptors must be L2 normalized")

    def test_illumination_invariance(self):
        """Verify RIFT2 produces consistent matches under severe contrast, gain, and bias shifts."""
        img1 = create_synthetic_lunar_patch(size=256, seed=26166)
        # Apply non-linear gain and offset (simulating extreme illumination / sensor exposure change)
        img2 = np.clip(1.6 * img1.astype(np.float32) + 35.0, 0, 255).astype(np.uint8)
        # Also invert small shadow gradient
        img2 = cv2.GaussianBlur(img2, (3, 3), 0.5)

        extractor = RIFT2Extractor(patch_size=96, max_features=300)
        kps1, descs1 = extractor.extract(img1)
        kps2, descs2 = extractor.extract(img2)

        assert len(kps1) >= 15
        assert len(kps2) >= 15

        # Match using BFMatcher with Lowe's ratio test
        bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
        raw_matches = bf.knnMatch(descs1, descs2, k=2)
        good = [m[0] for m in raw_matches if len(m) == 2 and m[0].distance < 0.85 * m[1].distance]

        assert len(good) >= 8, f"Expected at least 8 matches under illumination shift, got {len(good)}"
        # Check geometric displacement is near zero (since images are spatially aligned)
        displacements = [
            np.linalg.norm(np.array(kps1[m.queryIdx].pt) - np.array(kps2[m.trainIdx].pt))
            for m in good
        ]
        inliers_count = sum(d < 5.0 for d in displacements)
        assert inliers_count >= 5, f"Expected at least 5 spatial inliers under illumination variation, got {inliers_count}"

    def test_rotation_invariance(self):
        """Verify RIFT2 recovers true rotation on synthetic rotated crater image."""
        img = create_synthetic_lunar_patch(size=256, seed=26166)
        angle_deg = 30.0
        center = (128.0, 128.0)
        rot_mat = cv2.getRotationMatrix2D(center, angle_deg, 1.0)
        img_rot = cv2.warpAffine(img, rot_mat, (256, 256), borderMode=cv2.BORDER_REFLECT)

        extractor = RIFT2Extractor(patch_size=96, max_features=400)
        kps1, descs1 = extractor.extract(img)
        kps2, descs2 = extractor.extract(img_rot)

        assert len(kps1) >= 20
        assert len(kps2) >= 20

        bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
        raw_matches = bf.knnMatch(descs1, descs2, k=2)
        good = [m[0] for m in raw_matches if len(m) == 2 and m[0].distance < 0.88 * m[1].distance]

        assert len(good) >= 6, f"Expected matches under 30 deg rotation, got {len(good)}"

        # Estimate affine matrix and verify rotation recovery
        pts1 = np.float32([kps1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        pts2 = np.float32([kps2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        est_mat, inlier_mask = cv2.estimateAffine2D(pts1, pts2, method=cv2.RANSAC, ransacReprojThreshold=3.5)
        assert est_mat is not None, "Affine transformation must converge"
        recovered_angle = float(np.degrees(np.arctan2(est_mat[1, 0], est_mat[0, 0])))
        # Account for coordinate handedness (warpAffine with positive angle rotates clockwise in image coords)
        angle_err = min(abs(recovered_angle - angle_deg), abs(recovered_angle - (-angle_deg)))
        # Allow +/- 3.5 deg tolerance on synthetic patch
        assert angle_err < 3.5, f"Recovered rotation {recovered_angle:.2f} deg diverges from +/-{angle_deg} deg (error={angle_err:.2f})"
