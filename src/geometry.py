import cv2
import numpy as np


def extract_match_points(kp_a, kp_b, matches):
    pts_a = np.float32([kp_a[m.queryIdx].pt for m in matches])
    pts_b = np.float32([kp_b[m.trainIdx].pt for m in matches])
    return pts_a, pts_b


def estimate(pts_a, pts_b, model="affine", ransac_thresh=5.0):
    if len(pts_a) < 4:
        return None, None

    if model == "affine":
        transform, inlier_mask = cv2.estimateAffine2D(
            pts_b, pts_a, method=cv2.RANSAC, ransacReprojThreshold=ransac_thresh
        )
    elif model == "homography":
        transform, inlier_mask = cv2.findHomography(
            pts_b, pts_a, cv2.RANSAC, ransac_thresh
        )
    else:
        raise ValueError(f"Unknown model: {model}. Available: affine, homography")

    if transform is None:
        return None, None

    inlier_mask = inlier_mask.ravel().astype(bool)
    return transform, inlier_mask


def compute_inlier_stats(inlier_mask):
    if inlier_mask is None:
        return 0, 0.0
    count = int(np.sum(inlier_mask))
    ratio = count / len(inlier_mask) if len(inlier_mask) > 0 else 0.0
    return count, ratio
