import cv2
import numpy as np


def load_image(path):
    image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if image is None:
        raise FileNotFoundError(f"Cannot read image: {path}")
    return image


def validate_image(image):
    if image is None:
        return False
    if not isinstance(image, np.ndarray):
        return False
    if image.size == 0:
        return False
    if image.ndim < 2:
        return False
    return True


def load_pair(ref_path, mov_path):
    ref = load_image(ref_path)
    mov = load_image(mov_path)
    if not validate_image(ref):
        raise ValueError(f"Invalid reference image: {ref_path}")
    if not validate_image(mov):
        raise ValueError(f"Invalid moving image: {mov_path}")
    return ref, mov
