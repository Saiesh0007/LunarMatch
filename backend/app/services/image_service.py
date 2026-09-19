import uuid
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
import cv2
import numpy as np
from PIL import Image

from ..config import settings
from ..models.responses import ImageUploadResponse, DemoPairInfo
from ..simulation.scenario_generator import generate_lunar_crater_surface, apply_controlled_variation
from ..utils.logging import logger

class ImageService:
    """Manages lunar image ingestion, caching, validation, and demo pair assets."""

    def __init__(self):
        self.raw_dir = settings.RAW_DIR
        self.examples_dir = settings.EXAMPLES_DIR
        self._ensure_demo_pairs()

    def _ensure_demo_pairs(self):
        """Ensure standard demo pairs exist on disk with verified provenance."""
        self.examples_dir.mkdir(parents=True, exist_ok=True)
        
        pair_a_ref = self.examples_dir / "pair_a_ref.png"
        pair_a_mov = self.examples_dir / "pair_a_mov.png"
        pair_b_ref = self.examples_dir / "pair_b_ref.png"
        pair_b_mov = self.examples_dir / "pair_b_mov.png"

        # Generate Demo Pair A (Moderate rotation + translation, sun azimuth 45 vs 55)
        if not pair_a_ref.exists() or not pair_a_mov.exists():
            logger.info("Generating Demo Pair A — Lunar Prototype imagery...")
            ref_a = generate_lunar_crater_surface(width=640, height=640, sun_azimuth_deg=45.0, seed=26166)
            mov_a, _ = apply_controlled_variation(
                ref_a, scale=1.03, rotation_deg=3.5, tx_px=14.0, ty_px=-10.0,
                contrast_factor=1.08, brightness_offset=-5.0, seed=26166
            )
            cv2.imwrite(str(pair_a_ref), ref_a)
            cv2.imwrite(str(pair_a_mov), mov_a)

        # Generate Demo Pair B (Challenging illumination gradient: sun azimuth 40 vs 110 degrees)
        if not pair_b_ref.exists() or not pair_b_mov.exists():
            logger.info("Generating Demo Pair B — High Illumination Delta Prototype...")
            ref_b = generate_lunar_crater_surface(width=640, height=640, sun_azimuth_deg=40.0, seed=38291)
            # Different sun azimuth simulates high multi-temporal illumination shift
            mov_b_base = generate_lunar_crater_surface(width=640, height=640, sun_azimuth_deg=100.0, seed=38291)
            mov_b, _ = apply_controlled_variation(
                mov_b_base, scale=0.98, rotation_deg=-2.8, tx_px=-8.0, ty_px=12.0,
                contrast_factor=0.92, brightness_offset=10.0, seed=38291
            )
            cv2.imwrite(str(pair_b_ref), ref_b)
            cv2.imwrite(str(pair_b_mov), mov_b)

    def save_upload(self, file_bytes: bytes, original_filename: str) -> ImageUploadResponse:
        """Validate and persist uploaded image file."""
        image_id = str(uuid.uuid4())
        ext = Path(original_filename).suffix.lower()
        if ext not in [".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"]:
            ext = ".png"

        saved_path = self.raw_dir / f"{image_id}{ext}"
        with open(saved_path, "wb") as f:
            f.write(file_bytes)

        # Read and validate with OpenCV
        img = cv2.imread(str(saved_path), cv2.IMREAD_UNCHANGED)
        if img is None:
            saved_path.unlink(missing_ok=True)
            raise ValueError(f"Uploaded file could not be decoded as a valid image: {original_filename}")

        h, w = img.shape[:2]
        channels = 1 if len(img.shape) == 2 else img.shape[2]
        size_kb = round(len(file_bytes) / 1024.0, 2)

        return ImageUploadResponse(
            image_id=image_id,
            filename=original_filename,
            width=w,
            height=h,
            channels=channels,
            format=ext.replace(".", ""),
            file_size_kb=size_kb,
            preview_url=f"/api/v1/images/{image_id}/preview",
        )

    def resolve_image_path(self, image_id_or_path: str) -> Path:
        """Resolve an image identifier or demo shortcut to an existing absolute Path."""
        demo_map = {
            "demo_pair_a_ref": self.examples_dir / "pair_a_ref.png",
            "demo_pair_a_mov": self.examples_dir / "pair_a_mov.png",
            "demo_pair_b_ref": self.examples_dir / "pair_b_ref.png",
            "demo_pair_b_mov": self.examples_dir / "pair_b_mov.png",
        }
        if image_id_or_path in demo_map:
            p = demo_map[image_id_or_path]
            try:
                if p.exists():
                    return p
            except (OSError, ValueError):
                return p

        for ext in [".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"]:
            candidate = self.raw_dir / f"{image_id_or_path}{ext}"
            try:
                if candidate.exists():
                    return candidate
            except (OSError, ValueError):
                return candidate

        p = Path(image_id_or_path)
        try:
            if p.exists() and p.is_file():
                return p
        except (OSError, ValueError):
            return p

        raise FileNotFoundError(f"Image resource could not be found: {image_id_or_path}")

    def get_demo_pairs(self) -> List[DemoPairInfo]:
        """Return metadata for known demonstration pairs with strict provenance labeling."""
        return [
            DemoPairInfo(
                pair_id="pair_a",
                name="Demo Pair A — Lunar Prototype",
                description="OHRC Optical vs TMC-2 Stereo alignment over impact crater basin.",
                reference_image_id="demo_pair_a_ref",
                moving_image_id="demo_pair_a_mov",
                reference_sensor="OHRC",
                moving_sensor="TMC-2",
                reference_preview_url="/api/v1/images/demo_pair_a_ref/preview",
                moving_preview_url="/api/v1/images/demo_pair_a_mov/preview",
                provenance_note="Procedurally rendered crater terrain with known affine perturbation.",
            ),
            DemoPairInfo(
                pair_id="pair_b",
                name="Demo Pair B — High Illumination Delta Prototype",
                description="LRO NAC vs IIRS Hyperspectral alignment with steep 60° solar illumination delta.",
                reference_image_id="demo_pair_b_ref",
                moving_image_id="demo_pair_b_mov",
                reference_sensor="LRO NAC",
                moving_sensor="IIRS",
                reference_preview_url="/api/v1/images/demo_pair_b_ref/preview",
                moving_preview_url="/api/v1/images/demo_pair_b_mov/preview",
                provenance_note="High shadow variation terrain designed to stress-test feature descriptor robustness.",
            ),
        ]

image_service = ImageService()
