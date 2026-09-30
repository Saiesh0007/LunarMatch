"""LightGlue Matcher for LunarMatch pipeline.

Wraps LightGlue model for keypoint matching between image pairs.
"""

from pathlib import Path
import time
from typing import Any, Dict, Tuple

import numpy as np
import torch

from app.vision.lightglue_model import LightGlue


class LightGlueMatcher:
    """LightGlue wrapper for keypoint matching on CPU."""

    def __init__(self, weights_path: str):
        path = Path(weights_path)
        if not path.is_file():
            raise FileNotFoundError(f"LightGlue weights file not found: {weights_path}")

        self.device = torch.device("cpu")
        try:
            torch.use_deterministic_algorithms(True)
        except Exception:
            pass

        self.model = LightGlue(features="superpoint", weights=str(path))
        self.model.to(self.device).eval()

    def match(
        self,
        kp_a: np.ndarray,
        desc_a: np.ndarray,
        kp_b: np.ndarray,
        desc_b: np.ndarray,
        img_a_shape: Tuple[int, ...],
        img_b_shape: Tuple[int, ...] = (640, 640),
    ) -> Dict[str, Any]:
        """Match keypoints between image A and image B.

        Args:
            kp_a: Keypoints in image A, shape (N, 2).
            desc_a: Descriptors in image A, shape (N, D).
            kp_b: Keypoints in image B, shape (M, 2).
            desc_b: Descriptors in image B, shape (M, D).
            img_a_shape: (H, W) or (H, W, C) of image A.
            img_b_shape: (H, W) or (H, W, C) of image B.

        Returns:
            Dict containing:
              - "matches": (K, 2) int64 index pairs [idx_a, idx_b]
              - "scores": (K,) float32 match confidences
              - "ms": execution time in milliseconds
        """
        t0 = time.perf_counter()

        kp_a = np.asarray(kp_a, dtype=np.float32)
        desc_a = np.asarray(desc_a, dtype=np.float32)
        kp_b = np.asarray(kp_b, dtype=np.float32)
        desc_b = np.asarray(desc_b, dtype=np.float32)

        if len(kp_a) == 0 or len(kp_b) == 0:
            return {
                "matches": np.empty((0, 2), dtype=np.int64),
                "scores": np.empty((0,), dtype=np.float32),
                "ms": (time.perf_counter() - t0) * 1000.0,
            }

        # Ensure descriptors are 256-dim
        if desc_a.ndim == 2 and desc_a.shape[1] != 256:
            d = desc_a.shape[1]
            if d < 256:
                pad = np.zeros((desc_a.shape[0], 256 - d), dtype=np.float32)
                desc_a = np.hstack([desc_a, pad])
            else:
                desc_a = desc_a[:, :256]

        if desc_b.ndim == 2 and desc_b.shape[1] != 256:
            d = desc_b.shape[1]
            if d < 256:
                pad = np.zeros((desc_b.shape[0], 256 - d), dtype=np.float32)
                desc_b = np.hstack([desc_b, pad])
            else:
                desc_b = desc_b[:, :256]

        h0, w0 = img_a_shape[:2]
        h1, w1 = img_b_shape[:2]

        t_kp0 = torch.from_numpy(kp_a).unsqueeze(0).to(self.device)
        t_desc0 = torch.from_numpy(desc_a).unsqueeze(0).to(self.device)
        t_size0 = torch.tensor([[w0, h0]], dtype=torch.float32, device=self.device)

        t_kp1 = torch.from_numpy(kp_b).unsqueeze(0).to(self.device)
        t_desc1 = torch.from_numpy(desc_b).unsqueeze(0).to(self.device)
        t_size1 = torch.tensor([[w1, h1]], dtype=torch.float32, device=self.device)

        data = {
            "image0": {"keypoints": t_kp0, "descriptors": t_desc0, "image_size": t_size0},
            "image1": {"keypoints": t_kp1, "descriptors": t_desc1, "image_size": t_size1},
        }

        with torch.no_grad():
            pred = self.model(data)

        matches_t = pred["matches"][0]
        scores_t = pred["scores"][0]

        matches = matches_t.cpu().numpy().astype(np.int64)
        scores = scores_t.cpu().numpy().astype(np.float32)

        dt_ms = (time.perf_counter() - t0) * 1000.0

        return {
            "matches": matches,
            "scores": scores,
            "ms": dt_ms,
        }
