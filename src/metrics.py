import numpy as np


def compute_rmse(pts_ref, pts_mov, transform):
    n = len(pts_mov)
    if n == 0:
        return None

    if transform.shape == (2, 3):
        ones = np.ones((n, 1), dtype=np.float32)
        pts_h = np.hstack([pts_mov, ones])
        projected = pts_h @ transform.T
    elif transform.shape == (3, 3):
        ones = np.ones((n, 1), dtype=np.float32)
        pts_h = np.hstack([pts_mov, ones])
        projected_h = pts_h @ transform.T
        projected = projected_h[:, :2] / projected_h[:, 2:3]
    else:
        return None

    errors = np.sqrt(np.sum((pts_ref - projected) ** 2, axis=1))
    return float(np.sqrt(np.mean(errors ** 2)))


def evaluate(kp_ref_count, kp_mov_count, candidate_count, good_count,
             inlier_count, inlier_mask, pts_ref, pts_mov, transform,
             spatial_coverage=None, runtime=None):
    inlier_ratio = inlier_count / good_count if good_count > 0 else None

    rmse = None
    if transform is not None and inlier_mask is not None:
        inlier_pts_ref = pts_ref[inlier_mask]
        inlier_pts_mov = pts_mov[inlier_mask]
        if len(inlier_pts_ref) > 0:
            rmse = compute_rmse(inlier_pts_ref, inlier_pts_mov, transform)

    return {
        "keypoints_ref": kp_ref_count,
        "keypoints_mov": kp_mov_count,
        "candidate_matches": candidate_count,
        "good_matches": good_count,
        "inlier_count": inlier_count,
        "inlier_ratio": inlier_ratio,
        "rmse": rmse,
        "spatial_coverage": spatial_coverage,
        "runtime": runtime,
    }


def format_metrics(metrics):
    lines = []
    for key, val in metrics.items():
        if val is None:
            lines.append(f"{key}: N/A")
        elif isinstance(val, float):
            lines.append(f"{key}: {val:.4f}")
        else:
            lines.append(f"{key}: {val}")
    return "\n".join(lines)
