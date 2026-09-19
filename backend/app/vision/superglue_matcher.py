"""SuperGlue feature matcher wrapper for PyTorch CPU inference."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np
import torch

from .superglue_model import SuperGlue


class SuperGlueMatcher:
    """SuperGlue feature matcher running deterministically on CPU."""

    def __init__(self, sp_weights: str = "", sg_weights: str = ""):
        self.sg_weights_path = Path(sg_weights) if sg_weights else Path(__file__).resolve().parent.parent.parent / "weights" / "superglue_outdoor.pth"
        if not self.sg_weights_path.exists():
            raise FileNotFoundError(f"SuperGlue weights not found: {self.sg_weights_path}")

        self.sp_weights_path = Path(sp_weights) if sp_weights else None
        self.device = torch.device("cpu")

        torch.manual_seed(26166)
        try:
            torch.use_deterministic_algorithms(True)
        except Exception:
            pass

        config = {
            "weights_path": str(self.sg_weights_path),
            "descriptor_dim": 256,
            "weights": "outdoor",
            "sinkhorn_iterations": 20,
            "match_threshold": 0.2,
        }
        self.model = SuperGlue(config)
        self.model.to(self.device)
        self.model.eval()

    def match(
        self,
        kp_a: np.ndarray,
        desc_a: np.ndarray,
        kp_b: np.ndarray,
        desc_b: np.ndarray,
        img_a_shape: Tuple[int, ...],
        img_b_shape: Tuple[int, ...],
    ) -> Dict[str, Any]:
        """Match keypoints and descriptors between two images using SuperGlue.

        Returns:
            {
                "matches": np.ndarray,  # (N, 2) index pairs into (kp_a, kp_b)
                "scores": np.ndarray,   # (N,) match confidences
                "ms": float,
            }
        """
        t0 = time.perf_counter()

        if kp_a is None or kp_b is None or len(kp_a) == 0 or len(kp_b) == 0:
            return {
                "matches": np.empty((0, 2), dtype=int),
                "scores": np.empty((0,), dtype=np.float32),
                "ms": 0.0,
            }

        h_a, w_a = img_a_shape[:2]
        h_b, w_b = img_b_shape[:2]

        # Convert 216-D RIFT2 descriptors to 256-D if necessary
        if desc_a.shape[1] < 256:
            pad_a = 256 - desc_a.shape[1]
            desc_a_padded = np.pad(desc_a, ((0, 0), (0, pad_a)), mode="constant").astype(np.float32)
        else:
            desc_a_padded = desc_a[:, :256].astype(np.float32)

        if desc_b.shape[1] < 256:
            pad_b = 256 - desc_b.shape[1]
            desc_b_padded = np.pad(desc_b, ((0, 0), (0, pad_b)), mode="constant").astype(np.float32)
        else:
            desc_b_padded = desc_b[:, :256].astype(np.float32)

        kpts0_t = torch.from_numpy(kp_a.astype(np.float32)).unsqueeze(0).to(self.device)
        kpts1_t = torch.from_numpy(kp_b.astype(np.float32)).unsqueeze(0).to(self.device)

        desc0_t = torch.from_numpy(desc_a_padded).unsqueeze(0).transpose(1, 2).to(self.device)
        desc1_t = torch.from_numpy(desc_b_padded).unsqueeze(0).transpose(1, 2).to(self.device)

        scores0 = torch.ones(kpts0_t.shape[:2], device=self.device)
        scores1 = torch.ones(kpts1_t.shape[:2], device=self.device)

        dummy_img0 = torch.empty((1, 1, h_a, w_a), device=self.device)
        dummy_img1 = torch.empty((1, 1, h_b, w_b), device=self.device)

        data = {
            "keypoints0": kpts0_t,
            "keypoints1": kpts1_t,
            "descriptors0": desc0_t,
            "descriptors1": desc1_t,
            "scores0": scores0,
            "scores1": scores1,
            "image0": dummy_img0,
            "image1": dummy_img1,
        }

        with torch.no_grad():
            pred = self.model(data)
            matches0 = pred["matches0"][0].cpu().numpy()
            conf0 = pred["matching_scores0"][0].cpu().numpy()

        valid = matches0 > -1
        idx_a = np.where(valid)[0]
        idx_b = matches0[valid]
        match_scores = conf0[valid]

        if len(idx_a) > 0:
            matches_arr = np.column_stack([idx_a, idx_b])
        else:
            matches_arr = np.empty((0, 2), dtype=int)

        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        return {
            "matches": matches_arr,
            "scores": match_scores.astype(np.float32),
            "ms": round(elapsed_ms, 2),
        }
