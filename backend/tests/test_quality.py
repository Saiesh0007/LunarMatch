import numpy as np

from app.evaluation.quality import evaluate_registration


def good_matrix():
    return np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])


def evaluate(**overrides):
    values = dict(overlap_ratio=0.5, inlier_count=50, inlier_ratio=0.5, spatial_coverage=0.8, rmse_pixels=1.0, transform_matrix=good_matrix())
    values.update(overrides)
    return evaluate_registration(**values)


def test_all_criteria_pass():
    assert evaluate()["decision"] == "ACCEPTED"


def test_overlap_too_low():
    result = evaluate(overlap_ratio=0.01)
    assert result["decision"] == "REGISTRATION_NOT_RELIABLE"
    assert "overlap_ratio" in result["failed_criteria"]


def test_too_few_inliers():
    result = evaluate(inlier_count=2)
    assert "inlier_count" in result["failed_criteria"]


def test_rmse_too_high():
    result = evaluate(rmse_pixels=3.0)
    assert "rmse_pixels" in result["failed_criteria"]


def test_degenerate_determinant():
    matrix = np.array([[0.01, 0, 0], [0, 0.01, 0], [0, 0, 1]], dtype=float)
    result = evaluate(transform_matrix=matrix)
    assert "homography_determinant" in result["failed_criteria"]


def test_ill_conditioned_matrix():
    matrix = np.array([[1e8, 0, 0], [0, 1e-8, 0], [0, 0, 1]], dtype=float)
    result = evaluate(transform_matrix=matrix)
    assert "condition_number_H" in result["failed_criteria"]


def test_cross_resolution_determinant_uses_expected_scale():
    # 19.6 m moving onto 78 m reference: linear scale 0.25, determinant ~0.0625
    matrix = np.array([[0.25, 0.0, 10.0], [0.0, 0.26, 5.0], [0.0, 0.0, 1.0]])
    assert "homography_determinant" not in evaluate(transform_matrix=matrix, expected_scale=0.25)["failed_criteria"]
    assert "homography_determinant" in evaluate(transform_matrix=good_matrix(), expected_scale=0.25)["failed_criteria"]


def test_unknown_scale_accepts_similarity_rejects_shear_and_mirror():
    assert "homography_determinant" not in evaluate(transform_matrix=np.diag([0.25, 0.26, 1.0]))["failed_criteria"]
    assert "homography_determinant" in evaluate(transform_matrix=np.diag([1.0, 0.2, 1.0]))["failed_criteria"]
    assert "homography_determinant" in evaluate(transform_matrix=np.diag([-1.0, 1.0, 1.0]))["failed_criteria"]


def test_footprint_coverage_ignores_cells_outside_moving_footprint():
    from app.evaluation.quality import footprint_coverage
    # 400x400 moving image scaled by 0.25 into the top-left 100x100 of a 200x200 reference:
    # on a 6x6 grid (33 px cells) the footprint holds the 3x3 top-left cell centres
    H = np.diag([0.25, 0.25, 1.0])
    pts = [[x, y] for x in (16, 50, 83) for y in (16, 50, 83)]
    assert footprint_coverage(pts, H, (400, 400), (200, 200)) == 1.0
    assert footprint_coverage(pts[:3], H, (400, 400), (200, 200)) == 3 / 9
    assert footprint_coverage(pts, None, (400, 400), (200, 200)) is None
