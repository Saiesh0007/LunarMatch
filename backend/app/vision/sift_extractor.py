from typing import Tuple, List, Optional
import cv2
import numpy as np
from .extractor import BaseFeatureExtractor
from ..utils.logging import logger

class SIFTExtractor(BaseFeatureExtractor):
    """
    Scale-Invariant Feature Transform (SIFT) Extractor using OpenCV.
    Tested baseline feature detector and 128D descriptor.
    """

    def __init__(
        self,
        nfeatures: int = 2000,
        n_octave_layers: int = 3,
        contrast_threshold: float = 0.04,
        edge_threshold: float = 10.0,
        sigma: float = 1.6,
    ):
        self.nfeatures = nfeatures
        self.sift = cv2.SIFT_create(
            nfeatures=nfeatures,
            nOctaveLayers=n_octave_layers,
            contrastThreshold=contrast_threshold,
            edgeThreshold=edge_threshold,
            sigma=sigma,
        )

    def extract(self, img: np.ndarray) -> Tuple[List[cv2.KeyPoint], np.ndarray]:
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img

        keypoints, descriptors = self.sift.detectAndCompute(gray, None)
        if descriptors is None:
            descriptors = np.empty((0, 128), dtype=np.float32)
        
        logger.info(f"SIFT extracted {len(keypoints)} keypoints from shape {img.shape[:2]}")
        return keypoints, descriptors
