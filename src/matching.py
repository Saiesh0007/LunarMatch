import cv2
import numpy as np


def _match_bf(desc_a, desc_b, k=2):
    matcher = cv2.BFMatcher(cv2.NORM_L2)
    return matcher.knnMatch(desc_a, desc_b, k=k)


def _match_flann(desc_a, desc_b, k=2):
    index_params = dict(algorithm=1, trees=5)
    search_params = dict(checks=50)
    matcher = cv2.FlannBasedMatcher(index_params, search_params)
    desc_a = np.float32(desc_a)
    desc_b = np.float32(desc_b)
    return matcher.knnMatch(desc_a, desc_b, k=k)


MATCHERS = {
    "bf": _match_bf,
    "flann": _match_flann,
}


def filter_ratio(knn_matches, threshold=0.75):
    good = []
    for pair in knn_matches:
        if len(pair) == 2:
            m, n = pair
            if m.distance < threshold * n.distance:
                good.append(m)
    return good


def match(desc_a, desc_b, method="bf", ratio_thresh=0.75):
    if desc_a is None or desc_b is None or len(desc_a) < 2 or len(desc_b) < 2:
        return [], []

    if method not in MATCHERS:
        raise ValueError(
            f"Unknown matcher: {method}. Available: {list(MATCHERS.keys())}"
        )

    knn_matches = MATCHERS[method](desc_a, desc_b)
    good_matches = filter_ratio(knn_matches, threshold=ratio_thresh)
    return knn_matches, good_matches
