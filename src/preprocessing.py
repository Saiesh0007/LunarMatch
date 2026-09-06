import cv2
import numpy as np


def to_grayscale(image):
    if image.ndim == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def normalize_intensity(image):
    img = image.astype(np.float32)
    min_val, max_val = img.min(), img.max()
    if max_val - min_val == 0:
        return np.zeros_like(image, dtype=np.uint8)
    normalized = (img - min_val) / (max_val - min_val) * 255
    return normalized.astype(np.uint8)


def enhance_contrast(image, clip_limit=2.0, grid_size=8):
    clahe = cv2.createCLAHE(
        clipLimit=clip_limit,
        tileGridSize=(grid_size, grid_size),
    )
    return clahe.apply(image)


def denoise(image, strength=10):
    return cv2.fastNlMeansDenoising(image, h=strength)


DEFAULT_CONFIG = {
    "grayscale": True,
    "normalize": True,
    "clahe": True,
    "denoise": False,
    "clahe_clip": 2.0,
    "clahe_grid": 8,
    "denoise_strength": 10,
}


def preprocess(image, config=None):
    if config is None:
        config = DEFAULT_CONFIG

    result = image.copy()
    steps_applied = []

    if config.get("grayscale", True):
        result = to_grayscale(result)
        steps_applied.append("grayscale")

    if config.get("normalize", True):
        result = normalize_intensity(result)
        steps_applied.append("normalize")

    if config.get("clahe", True):
        result = enhance_contrast(
            result,
            clip_limit=config.get("clahe_clip", 2.0),
            grid_size=config.get("clahe_grid", 8),
        )
        steps_applied.append("clahe")

    if config.get("denoise", False):
        result = denoise(result, strength=config.get("denoise_strength", 10))
        steps_applied.append("denoise")

    return result, steps_applied
