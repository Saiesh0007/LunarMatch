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
