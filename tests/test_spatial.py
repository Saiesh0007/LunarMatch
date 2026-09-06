"""
Unit tests for LunarMatch Spatial Balancing & Coverage Module (src/spatial.py)
SIH 2026 Problem Statement 26166 — Member 5 (Siddharth)
"""

import unittest
import numpy as np
from src.spatial import (
    _to_numpy_points,
    compute_grid_indices,
    compute_spatial_coverage,
    anms_spatial_balance,
    spatially_balance,
    get_grid_visualization_boxes,
)


class MockKeyPoint:
    """Mock of cv2.KeyPoint for testing without cv2 dependency."""
    def __init__(self, x: float, y: float, response: float = 1.0):
        self.pt = (float(x), float(y))
        self.response = float(response)


class TestSpatialModule(unittest.TestCase):

    def setUp(self):
        self.image_shape = (400, 400)  # (height, width)
        self.grid = (4, 4)             # 4 rows, 4 cols -> cell size 100x100

    def test_to_numpy_points(self):
        # Empty inputs
        self.assertEqual(_to_numpy_points(None).shape, (0, 2))
        self.assertEqual(_to_numpy_points([]).shape, (0, 2))
        self.assertEqual(_to_numpy_points(np.empty((0, 2))).shape, (0, 2))

        # List of tuples
        pts_list = [(10.0, 20.0), (30.0, 40.0)]
        arr = _to_numpy_points(pts_list)
        self.assertEqual(arr.shape, (2, 2))
        self.assertAlmostEqual(arr[0, 0], 10.0)
        self.assertAlmostEqual(arr[0, 1], 20.0)

        # Mock KeyPoint list
        kps = [MockKeyPoint(15.5, 25.5), MockKeyPoint(55.0, 75.0)]
        arr_kps = _to_numpy_points(kps)
        self.assertEqual(arr_kps.shape, (2, 2))
        self.assertAlmostEqual(arr_kps[0, 0], 15.5)
        self.assertAlmostEqual(arr_kps[0, 1], 25.5)

        # OpenCV 3D shape (N, 1, 2)
        cv_pts = np.array([[[10.0, 20.0]], [[30.0, 40.0]]])
        arr_cv = _to_numpy_points(cv_pts)
        self.assertEqual(arr_cv.shape, (2, 2))

        # Invalid shape
        with self.assertRaises(ValueError):
            _to_numpy_points(np.ones((5, 3)))

    def test_compute_grid_indices(self):
        # Image is 400x400, grid is 4x4. Cell size is 100x100
        # (x, y) = (50, 50) -> row 0, col 0
        # (x, y) = (150, 250) -> col 1, row 2
        # (x, y) = (399, 399) -> col 3, row 3
        # (x, y) = (400, 400) -> boundary clamped to col 3, row 3
        points = np.array([
            [50.0, 50.0],
            [150.0, 250.0],
            [399.0, 399.0],
            [400.0, 400.0],
            [0.0, 0.0]
        ])
        row_idx, col_idx = compute_grid_indices(points, self.image_shape, self.grid)

        self.assertEqual(row_idx[0], 0)
        self.assertEqual(col_idx[0], 0)

        self.assertEqual(row_idx[1], 2)
        self.assertEqual(col_idx[1], 1)

        self.assertEqual(row_idx[2], 3)
        self.assertEqual(col_idx[2], 3)

        self.assertEqual(row_idx[3], 3)
        self.assertEqual(col_idx[3], 3)

        self.assertEqual(row_idx[4], 0)
        self.assertEqual(col_idx[4], 0)

    def test_compute_spatial_coverage_empty(self):
        stats = compute_spatial_coverage([], self.image_shape, self.grid)
        self.assertEqual(stats["total_points"], 0)
        self.assertEqual(stats["occupied_cells"], 0)
        self.assertEqual(stats["coverage_ratio"], 0.0)
        self.assertFalse(stats["is_well_distributed"])
        self.assertEqual(stats["grid_occupancy"].shape, (4, 4))
        self.assertEqual(np.sum(stats["grid_occupancy"]), 0)

    def test_compute_spatial_coverage_uniform(self):
        # Place 1 point in each of the 16 cells
        pts = []
        for r in range(4):
            for c in range(4):
                pts.append([c * 100 + 50, r * 100 + 50])
        pts = np.array(pts)

        stats = compute_spatial_coverage(pts, self.image_shape, self.grid)
        self.assertEqual(stats["total_points"], 16)
        self.assertEqual(stats["occupied_cells"], 16)
        self.assertEqual(stats["total_cells"], 16)
        self.assertAlmostEqual(stats["coverage_ratio"], 1.0)
        self.assertTrue(stats["is_well_distributed"])
        self.assertAlmostEqual(stats["distribution_entropy"], 1.0, places=4)
        self.assertEqual(np.sum(stats["grid_occupancy"]), 16)

    def test_compute_spatial_coverage_clustered(self):
        # Place 20 points in cell (0, 0) only
        pts = np.random.uniform(10, 80, size=(20, 2))
        stats = compute_spatial_coverage(pts, self.image_shape, self.grid)

        self.assertEqual(stats["total_points"], 20)
        self.assertEqual(stats["occupied_cells"], 1)
        self.assertAlmostEqual(stats["coverage_ratio"], 1.0 / 16.0)
        self.assertFalse(stats["is_well_distributed"])
        self.assertAlmostEqual(stats["distribution_entropy"], 0.0)

    def test_spatially_balance_clustering_reduction(self):
        # Cell (0, 0) has 50 points
        # Cell (3, 3) has 2 points
        cell_00_pts = np.random.uniform(5, 95, size=(50, 2))
        cell_33_pts = np.array([[320.0, 320.0], [380.0, 380.0]])
        pts_ref = np.vstack([cell_00_pts, cell_33_pts])

        # Moving points correspond 1:1
        pts_mov = pts_ref + 5.0

        # Quality scores: lower score = better (e.g. descriptor distance)
        # Give first 10 points in cell 00 lowest scores
        scores = np.ones(52, dtype=np.float64) * 10.0
        scores[0:5] = [0.1, 0.2, 0.3, 0.4, 0.5]  # best 5

        result = spatially_balance(
            points_ref=pts_ref,
            points_mov=pts_mov,
            image_shape=self.image_shape,
            grid=self.grid,
            max_per_cell=5,
            scores=scores,
            score_order="ascending"
        )

        self.assertEqual(result["num_before"], 52)
        # 5 from cell 00 + 2 from cell 33 = 7 total
        self.assertEqual(result["num_after"], 7)
        self.assertEqual(result["balanced_pts_ref"].shape, (7, 2))
        self.assertEqual(result["balanced_pts_mov"].shape, (7, 2))

        # Check that top 5 best scores from cell 00 were selected (indices 0, 1, 2, 3, 4)
        for expected_idx in [0, 1, 2, 3, 4, 50, 51]:
            self.assertIn(expected_idx, result["selected_indices"])

        # Occupied cells count must remain 2 before and after
        self.assertEqual(result["coverage_before"], 2.0 / 16.0)
        self.assertEqual(result["coverage_after"], 2.0 / 16.0)

    def test_spatially_balance_descending_scores(self):
        # Higher score is better (e.g. keypoint response)
        pts_ref = np.array([
            [10.0, 10.0],  # score 10
            [20.0, 20.0],  # score 50 (best)
            [30.0, 30.0],  # score 40 (2nd best)
            [40.0, 40.0],  # score 5
        ])
        scores = [10.0, 50.0, 40.0, 5.0]

        result = spatially_balance(
            points_ref=pts_ref,
            image_shape=self.image_shape,
            grid=self.grid,
            max_per_cell=2,
            scores=scores,
            score_order="descending"
        )

        self.assertEqual(result["num_after"], 2)
        self.assertIn(1, result["selected_indices"])  # score 50
        self.assertIn(2, result["selected_indices"])  # score 40

    def test_spatially_balance_empty(self):
        result = spatially_balance([], image_shape=self.image_shape)
        self.assertEqual(result["num_before"], 0)
        self.assertEqual(result["num_after"], 0)
        self.assertEqual(result["coverage_before"], 0.0)
        self.assertEqual(result["coverage_after"], 0.0)
        self.assertEqual(result["balanced_pts_ref"].shape, (0, 2))

    def test_spatially_balance_mismatched_points(self):
        pts_ref = np.zeros((10, 2))
        pts_mov = np.zeros((8, 2))
        with self.assertRaises(ValueError):
            spatially_balance(pts_ref, pts_mov, image_shape=self.image_shape)

    def test_anms_spatial_balance_basic(self):
        # 30 points in a tight cluster + 10 points scattered
        rng = np.random.default_rng(123)
        clustered = rng.normal(50.0, 5.0, size=(30, 2))
        scattered = rng.uniform(10.0, 390.0, size=(10, 2))
        pts_ref = np.vstack([clustered, scattered])

        from src.spatial import anms_spatial_balance
        result = anms_spatial_balance(pts_ref, target_count=15)
        self.assertEqual(result["num_before"], 40)
        self.assertEqual(result["num_after"], 15)
        self.assertEqual(result["balanced_pts_ref"].shape, (15, 2))
        self.assertEqual(len(result["selected_indices"]), 15)

    def test_spatially_balance_anms_method(self):
        pts_ref = np.random.uniform(10.0, 390.0, size=(50, 2))
        pts_mov = pts_ref + 2.0
        result = spatially_balance(
            points_ref=pts_ref,
            points_mov=pts_mov,
            image_shape=self.image_shape,
            method="anms",
            target_count=20,
        )
        self.assertEqual(result["method"], "anms")
        self.assertEqual(result["num_after"], 20)
        self.assertEqual(result["balanced_pts_ref"].shape, (20, 2))
        self.assertEqual(result["balanced_pts_mov"].shape, (20, 2))

    def test_anms_without_scores_spreads_points(self):
        pts = np.array([[10.0, 10.0], [11.0, 10.0], [12.0, 10.0], [390.0, 390.0]])
        result = anms_spatial_balance(pts, target_count=2)
        selected = result["balanced_pts_ref"]
        self.assertTrue(any(np.linalg.norm(p - [390.0, 390.0]) < 1e-6 for p in selected))

    def test_anms_ascending_scores_are_supported(self):
        pts = np.array([[10.0, 10.0], [20.0, 20.0], [300.0, 300.0]])
        result = spatially_balance(
            pts, image_shape=self.image_shape, method="anms", target_count=2,
            scores=[0.1, 0.2, 0.9], score_order="ascending"
        )
        self.assertEqual(result["num_after"], 2)

    def test_anms_rejects_invalid_scores(self):
        with self.assertRaises(ValueError):
            anms_spatial_balance(np.zeros((3, 2)), target_count=2, scores=[1.0])

    def test_get_grid_visualization_boxes(self):
        boxes = get_grid_visualization_boxes((400, 400), (4, 4))
        self.assertEqual(len(boxes), 16)
        # Check first box
        self.assertEqual(boxes[0]["row"], 0)
        self.assertEqual(boxes[0]["col"], 0)
        self.assertEqual(boxes[0]["xmin"], 0.0)
        self.assertEqual(boxes[0]["ymin"], 0.0)
        self.assertEqual(boxes[0]["xmax"], 100.0)
        self.assertEqual(boxes[0]["ymax"], 100.0)
        # Check last box
        self.assertEqual(boxes[-1]["row"], 3)
        self.assertEqual(boxes[-1]["col"], 3)
        self.assertEqual(boxes[-1]["xmin"], 300.0)
        self.assertEqual(boxes[-1]["ymin"], 300.0)
        self.assertEqual(boxes[-1]["xmax"], 400.0)
        self.assertEqual(boxes[-1]["ymax"], 400.0)


if __name__ == "__main__":
    unittest.main()
