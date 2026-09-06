"""
Unit tests for LunarMatch Metrics & Evaluation Module (src/metrics.py)
SIH 2026 Problem Statement 26166 — Member 5 (Siddharth)
"""

import unittest
import numpy as np
from src.metrics import (
    transform_points,
    compute_reprojection_errors,
    assess_registration_confidence,
    calculate_metrics,
    format_metrics_summary,
)


class TestMetricsModule(unittest.TestCase):

    def setUp(self):
        # Sample points
        self.pts_ref = np.array([
            [100.0, 100.0],
            [200.0, 100.0],
            [200.0, 200.0],
            [100.0, 200.0]
        ], dtype=np.float64)

        self.identity_homography = np.eye(3, dtype=np.float64)
        self.identity_affine = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=np.float64)

    def test_transform_points_identity(self):
        # Homography
        transformed_h = transform_points(self.pts_ref, self.identity_homography, model_type="homography")
        np.testing.assert_allclose(transformed_h, self.pts_ref)

        # Affine 2x3
        transformed_a = transform_points(self.pts_ref, self.identity_affine, model_type="affine")
        np.testing.assert_allclose(transformed_a, self.pts_ref)

    def test_transform_points_translation(self):
        # Translation of (+15, +25)
        T_homography = np.array([
            [1.0, 0.0, 15.0],
            [0.0, 1.0, 25.0],
            [0.0, 0.0, 1.0]
        ])
        transformed = transform_points(self.pts_ref, T_homography, model_type="homography")
        expected = self.pts_ref + np.array([15.0, 25.0])
        np.testing.assert_allclose(transformed, expected)

    def test_transform_points_invalid_inputs(self):
        # Empty array
        res = transform_points([], self.identity_homography)
        self.assertEqual(res.shape, (0, 2))

        # Invalid matrix shape for homography
        with self.assertRaises(ValueError):
            transform_points(self.pts_ref, np.ones((2, 2)), model_type="homography")

        # Unsupported model type
        with self.assertRaises(ValueError):
            transform_points(self.pts_ref, self.identity_homography, model_type="invalid_model")

    def test_compute_reprojection_errors_exact_match(self):
        errors = compute_reprojection_errors(
            points_ref=self.pts_ref,
            points_mov=self.pts_ref,
            transform_matrix=self.identity_homography,
            model_type="homography"
        )
        self.assertEqual(errors["rmse"], 0.0)
        self.assertEqual(errors["mae"], 0.0)
        self.assertEqual(errors["max_error"], 0.0)
        self.assertEqual(len(errors["point_errors"]), 4)

    def test_compute_reprojection_errors_known_offset(self):
        # Shift moving points by (3, 4) -> distance = sqrt(3^2 + 4^2) = 5.0
        pts_mov = self.pts_ref - np.array([3.0, 4.0])

        errors = compute_reprojection_errors(
            points_ref=self.pts_ref,
            points_mov=pts_mov,
            transform_matrix=self.identity_homography,  # without accounting for offset
            model_type="homography"
        )
        self.assertAlmostEqual(errors["rmse"], 5.0, places=3)
        self.assertAlmostEqual(errors["mae"], 5.0, places=3)
        self.assertAlmostEqual(errors["median_error"], 5.0, places=3)
        self.assertAlmostEqual(errors["max_error"], 5.0, places=3)
        self.assertAlmostEqual(errors["std_error"], 0.0, places=3)

    def test_compute_reprojection_errors_empty_and_none(self):
        # Empty points
        res1 = compute_reprojection_errors([], [], self.identity_homography)
        self.assertIsNone(res1["rmse"])

        # None matrix
        res2 = compute_reprojection_errors(self.pts_ref, self.pts_ref, None)
        self.assertIsNone(res2["rmse"])

    def test_assess_registration_confidence_reliable(self):
        score, status, diagnostics = assess_registration_confidence(
            num_inliers=40,
            inlier_ratio=0.65,
            spatial_coverage=0.60,
            rmse=0.85
        )
        self.assertEqual(status, "RELIABLE")
        self.assertGreaterEqual(score, 0.85)

    def test_assess_registration_confidence_failed(self):
        score, status, diagnostics = assess_registration_confidence(
            num_inliers=2,
            inlier_ratio=0.05,
            spatial_coverage=0.06,
            rmse=15.0
        )
        self.assertEqual(status, "FAILED")
        self.assertLess(score, 0.30)
        self.assertTrue(any("Critical" in d or "Insufficient" in d for d in diagnostics))

    def test_calculate_metrics_structure(self):
        metrics = calculate_metrics(
            num_keypoints_ref=120,
            num_keypoints_mov=110,
            num_candidate_matches=90,
            num_filtered_matches=60,
            num_inliers=40,
            spatial_coverage_before=0.50,
            spatial_coverage_after=0.50,
            rmse=1.25,
            runtime_seconds=0.456,
            model_type="homography"
        )

        # Check required keys
        self.assertEqual(metrics["num_keypoints_ref"], 120)
        self.assertEqual(metrics["num_keypoints_mov"], 110)
        self.assertEqual(metrics["num_candidate_matches"], 90)
        self.assertEqual(metrics["num_filtered_matches"], 60)
        self.assertEqual(metrics["num_inliers"], 40)
        self.assertAlmostEqual(metrics["inlier_ratio"], 40.0 / 60.0, places=3)
        self.assertAlmostEqual(metrics["candidate_filter_retention"], 60.0 / 90.0, places=3)
        self.assertEqual(metrics["rmse"], 1.25)
        self.assertEqual(metrics["status"], "RELIABLE")
        self.assertIn("diagnostics", metrics)

    def test_format_metrics_summary(self):
        metrics = calculate_metrics(
            num_keypoints_ref=100,
            num_keypoints_mov=100,
            num_candidate_matches=80,
            num_filtered_matches=50,
            num_inliers=35,
            spatial_coverage_before=0.40,
            spatial_coverage_after=0.40,
            rmse=1.10,
            runtime_seconds=0.35,
            model_type="homography"
        )
        summary = format_metrics_summary(metrics)
        self.assertIsInstance(summary, str)
        self.assertIn("LunarMatch Evaluation Summary", summary)
        self.assertIn("RANSAC Inliers", summary)
        self.assertIn("Reprojection RMSE", summary)


if __name__ == "__main__":
    unittest.main()
