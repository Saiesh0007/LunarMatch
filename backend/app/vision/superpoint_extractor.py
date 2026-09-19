"""SuperPoint Feature Extractor wrapper for PyTorch CPU inference."""
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

import cv2
import numpy as np
import torch

from .superpoint_model import SuperPoint


class SuperPointExtractor:
    """SuperPoint feature extractor wrapper running deterministically on CPU."""

    def __init__(self, weights_path: str, max_features: int = 2000, keypoint_threshold: float = 0.005):
        self.weights_path = Path(weights_path)
        if not self.weights_path.exists():
            raise FileNotFoundError(f"SuperPoint weights not found: {self.weights_path}")

        self.max_features = max_features
        self.keypoint_threshold = keypoint_threshold
        self.device = torch.device("cpu")

        # Reproducibility settings
        torch.manual_seed(26166)
        try:
            torch.use_deterministic_algorithms(True)
        except Exception:
            pass

        config = {
            "weights_path": str(self.weights_path),
            "max_keypoints": max_features,
            "keypoint_threshold": keypoint_threshold,
            "nms_radius": 4,
            "descriptor_dim": 256,
        }
        self.model = SuperPoint(config)
        self.model.to(self.device)
        self.model.eval()

    def extract(self, img: np.ndarray) -> Dict[str, Any]:
        """Extract keypoints and descriptors from a grayscale or RGB image.

        Returns:
            {
                "keypoints": np.ndarray,  # (N, 2) float32 in (x, y) coordinates
                "descriptors": np.ndarray,  # (N, 256) float32
                "scores": np.ndarray,  # (N,) float32
                "ms": float,
            }
        """
        t0 = time.perf_counter()

        if img is None or img.size == 0:
            return {
                "keypoints": np.empty((0, 2), dtype=np.float32),
                "descriptors": np.empty((0, 256), dtype=np.float32),
                "scores": np.empty((0,), dtype=np.float32),
                "ms": 0.0,
            }

        if len(img.shape) == 3 and img.shape[2] == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        elif len(img.shape) == 3 and img.shape[2] == 4:
            gray = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)
        else:
            gray = img.copy()

        # Normalize to float tensor [0.0, 1.0] with shape (1, 1, H, W)
        tensor = torch.from_numpy(gray.astype(np.float32) / 255.0).unsqueeze(0).unsqueeze(0).to(self.device)

        with torch.no_grad():
            out = self.model({"image": tensor})
            # out['keypoints']: list of tensors (N, 2) in (x, y) format
            # out['descriptors']: list of tensors (256, N)
            # out['scores']: list of tensors (N,)
            kpts = out["keypoints"][0].cpu().numpy().astype(np.float32)
            scores = out["scores"][0].cpu().numpy().astype(np.float32)
            desc_t = out["descriptors"][0].t().cpu().numpy().astype(np.float32)  # transpose to (N, 256)

        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        return {
            "keypoints": kpts,
            "descriptors": desc_t,
            "scores": scores,
            "ms": round(elapsed_ms, 2),
        }
