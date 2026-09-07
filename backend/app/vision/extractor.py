from abc import ABC, abstractmethod
from typing import Tuple, List, Optional
import numpy as np
import cv2

class BaseFeatureExtractor(ABC):
    """Abstract base class for all feature extraction methods."""

    @abstractmethod
    def extract(self, img: np.ndarray) -> Tuple[List[cv2.KeyPoint], np.ndarray]:
        """Extract keypoints and descriptors from grayscale image."""
        pass
