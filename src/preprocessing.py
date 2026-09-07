import cv2
import numpy as np

def preprocess(image, sensor=None, config=None):
    """
    Interface specified in Design.md:
    Inputs: (image, sensor, config)
    Outputs: {
        'image': processed_image,
        'metadata': metadata,
        'scale_factor': scale_factor
    }
    """
    if config is None:
        config = {}

    processed = image.copy()

    # 1. Grayscale where appropriate
    if len(processed.shape) == 3:
        processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)

    # Convert high bit-depth to uint8 if needed
    if processed.dtype != np.uint8:
        processed = cv2.normalize(processed, None, 0, 255, cv2.NORM_MINMAX)
        processed = processed.astype(np.uint8)

    # 2. Denoising
    processed = cv2.GaussianBlur(processed, (3, 3), 0)

    # 3. CLAHE / local contrast enhancement
    clip_limit = config.get("clahe_clip_limit", 2.0)
    tile_grid_size = config.get("clahe_grid_size", (8, 8))
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    processed = clahe.apply(processed)

    # 4. Scale handling (tracked working scale factor)
    scale_factor = float(config.get("scale_factor", 1.0))

    metadata = {
        "sensor": sensor,
        "processed_shape": processed.shape,
        "clahe_applied": True
    }

    return {
        "image": processed,
        "metadata": metadata,
        "scale_factor": scale_factor
    }