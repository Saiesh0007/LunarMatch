"""
Unit tests for LunarMatch Controlled Benchmark & Evaluation Suite (src/benchmark.py)
SIH 2026 Problem Statement 26166 — Member 5 (Siddharth)
"""

import unittest
import numpy as np
import tempfile
import os
import shutil

from src.benchmark import (
    create_ground_truth_transform,
    generate_synthetic_points_pair,
    run_benchmark_experiment,
    run_full_robustness_benchmark_suite,
)


class TestBenchmarkModule(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_ground_truth_transform(self):
        # Identity
        H_id = create_ground_truth_transform(0.0, 1.0, (0.0, 0.0), (200.0, 200.0))
        np.testing.assert_allclose(H_id, np.eye(3), atol=1e-6)

        # Translation
        H_trans = create_ground_truth_transform(0.0, 1.0, (15.0, 25.0), (200.0, 200.0))
        self.assertAlmostEqual(H_trans[0, 2], 15.0)
        self.assertAlmostEqual(H_trans[1, 2], 25.0)

        # Scale 2.0x
        H_scale = create_ground_truth_transform(0.0, 2.0, (0.0, 0.0), (200.0, 200.0))
        self.assertAlmostEqual(H_scale[0, 0], 2.0)
        self.assertAlmostEqual(H_scale[1, 1], 2.0)

    def test_generate_synthetic_points_pair(self):
        H_gt = create_ground_truth_transform(15.0, 1.1, (10.0, -5.0))
        pts_ref, pts_mov, H = generate_synthetic_points_pair(
            num_points=80,
            image_shape=(400, 400),
            transform_matrix=H_gt,
            cluster_ratio=0.7,
            noise_std=0.0,
        )
        self.assertEqual(pts_ref.shape, (80, 2))
        self.assertEqual(pts_mov.shape, (80, 2))
        self.assertEqual(H.shape, (3, 3))

    def test_run_benchmark_experiment(self):
        H_gt = create_ground_truth_transform(10.0, 1.05, (12.0, 8.0))
        pts_ref, pts_mov, _ = generate_synthetic_points_pair(
            num_points=100,
            image_shape=(400, 400),
            transform_matrix=H_gt,
            cluster_ratio=0.75,
            noise_std=0.2,
        )

        res = run_benchmark_experiment(
            experiment_name="Test Experiment",
            pts_ref=pts_ref,
            pts_mov=pts_mov,
            H_gt=H_gt,
            image_shape=(400, 400),
            grid=(4, 4),
            max_per_cell=5,
        )

        self.assertEqual(res["experiment_name"], "Test Experiment")
        self.assertEqual(res["total_points"], 100)
        self.assertIn("raw", res)
        self.assertIn("grid_balanced", res)
        self.assertIn("anms_balanced", res)
        self.assertIn("coverage_gain_grid", res)
        self.assertIn("coverage_gain_anms", res)
        self.assertIsInstance(res["raw"]["rmse_gt"], float)

    def test_run_full_robustness_benchmark_suite(self):
        summary = run_full_robustness_benchmark_suite(
            image_shape=(400, 400),
            output_dir=self.temp_dir,
        )

        self.assertEqual(summary["total_experiments"], 5)
        self.assertEqual(len(summary["experiments"]), 5)
        self.assertIn("average_grid_coverage_gain", summary)
        self.assertIn("average_anms_coverage_gain", summary)

        # Check JSON export
        export_file = os.path.join(self.temp_dir, "benchmark_results.json")
        self.assertTrue(os.path.exists(export_file))


if __name__ == "__main__":
    unittest.main()
