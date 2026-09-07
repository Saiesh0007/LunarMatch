import os
import cv2
import numpy as np

def load_image(path):
    """
    Interface specified in Design.md:
    load_image(path) -> image, metadata
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image not found at: {path}")

    image = cv2.imread(path, cv2.IMREAD_UNCHANGED)

    # Validation requirements from Design.md (reject empty / unreadable)
    if image is None or image.size == 0:
        raise ValueError(f"Unreadable or empty image file: {path}")

    h, w = image.shape[:2]
    metadata = {
        "path": path,
        "shape": image.shape,
        "dtype": str(image.dtype),
        "height": h,
        "width": w
    }

    return image, metadata