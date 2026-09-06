import cv2


def _extract_sift(image, n_features=0, contrast_threshold=0.04, edge_threshold=10):
    sift = cv2.SIFT_create(
        nfeatures=n_features,
        contrastThreshold=contrast_threshold,
        edgeThreshold=edge_threshold,
    )
    keypoints, descriptors = sift.detectAndCompute(image, None)
    return keypoints, descriptors


EXTRACTORS = {
    "sift": _extract_sift,
}


def extract(image, method="sift", **params):
    if method not in EXTRACTORS:
        raise ValueError(
            f"Unknown feature method: {method}. Available: {list(EXTRACTORS.keys())}"
        )
    keypoints, descriptors = EXTRACTORS[method](image, **params)
    if keypoints is None:
        keypoints = []
    if descriptors is None:
        import numpy as np
        descriptors = np.empty((0, 128), dtype=np.float32)
    return keypoints, descriptors
