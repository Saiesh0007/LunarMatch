import base64
from io import BytesIO
from pathlib import Path
from typing import List, Tuple, Optional
import cv2
import numpy as np
from PIL import Image

def load_image(path: Path, grayscale: bool = True) -> np.ndarray:
    """Load image from disk using OpenCV."""
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")
    
    flag = cv2.IMREAD_GRAYSCALE if grayscale else cv2.IMREAD_COLOR
    img = cv2.imread(str(path), flag)
    if img is None:
        raise ValueError(f"Failed to decode image from: {path}")
    return img

def save_image(path: Path, img: np.ndarray) -> None:
    """Save image to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    success = cv2.imwrite(str(path), img)
    if not success:
        raise IOError(f"Failed to write image to {path}")

def image_to_base64(img: np.ndarray, format_ext: str = ".png") -> str:
    """Convert OpenCV image to base64 string."""
    success, buffer = cv2.imencode(format_ext, img)
    if not success:
        raise ValueError("Could not encode image to buffer")
    return base64.b64encode(buffer).decode("utf-8")

def create_overlay_image(ref_img: np.ndarray, warped_mov_img: np.ndarray, alpha: float = 0.5) -> np.ndarray:
    """
    Create a blended overlay between reference and registered moving image.
    Uses 2-channel false coloring for high visual clarity:
    Reference in Cyan/Green, Moving in Red/Magenta.
    """
    # Ensure both are same size
    h, w = ref_img.shape[:2]
    if warped_mov_img.shape[:2] != (h, w):
        warped_mov_img = cv2.resize(warped_mov_img, (w, h))

    # Convert grayscale to BGR if needed
    if len(ref_img.shape) == 2:
        ref_bgr = cv2.cvtColor(ref_img, cv2.COLOR_GRAY2BGR)
    else:
        ref_bgr = ref_img.copy()

    if len(warped_mov_img.shape) == 2:
        mov_bgr = cv2.cvtColor(warped_mov_img, cv2.COLOR_GRAY2BGR)
    else:
        mov_bgr = warped_mov_img.copy()

    # Blend
    blended = cv2.addWeighted(ref_bgr, 1.0 - alpha, mov_bgr, alpha, 0.0)
    return blended

def create_difference_image(ref_img: np.ndarray, warped_mov_img: np.ndarray) -> np.ndarray:
    """
    Compute absolute difference between reference and registered moving image.
    Outputs normalized difference map with a colormap for scientific visual assessment.
    """
    h, w = ref_img.shape[:2]
    if warped_mov_img.shape[:2] != (h, w):
        warped_mov_img = cv2.resize(warped_mov_img, (w, h))

    if len(ref_img.shape) == 3:
        ref_gray = cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY)
    else:
        ref_gray = ref_img

    if len(warped_mov_img.shape) == 3:
        mov_gray = cv2.cvtColor(warped_mov_img, cv2.COLOR_BGR2GRAY)
    else:
        mov_gray = warped_mov_img

    # Mask valid overlap regions (where warped moving image is non-zero)
    valid_mask = warped_mov_img > 0
    diff = cv2.absdiff(ref_gray, mov_gray)
    diff[~valid_mask] = 0

    # Colorize using JET/VIRIDIS colormap for high-contrast error visualization
    diff_color = cv2.applyColorMap(diff, cv2.COLORMAP_INFERNO)
    # Zero-out non-overlap regions in color map
    diff_color[~valid_mask] = [15, 23, 42]  # Dark cosmic blue background
    return diff_color

def draw_correspondences(
    ref_img: np.ndarray,
    mov_img: np.ndarray,
    pts_ref: List[Tuple[float, float]],
    pts_mov: List[Tuple[float, float]],
    inlier_mask: Optional[List[bool]] = None,
    color_inlier: Tuple[int, int, int] = (0, 229, 255),    # Cyan
    color_outlier: Tuple[int, int, int] = (80, 80, 220),   # Muted red
    max_draw: int = 150
) -> np.ndarray:
    """
    Render side-by-side correspondence lines connecting reference and moving keypoints.
    """
    h1, w1 = ref_img.shape[:2]
    h2, w2 = mov_img.shape[:2]

    # Convert to BGR if grayscale
    img1 = cv2.cvtColor(ref_img, cv2.COLOR_GRAY2BGR) if len(ref_img.shape) == 2 else ref_img.copy()
    img2 = cv2.cvtColor(mov_img, cv2.COLOR_GRAY2BGR) if len(mov_img.shape) == 2 else mov_img.copy()

    # Target canvas
    canvas_h = max(h1, h2)
    canvas_w = w1 + w2
    canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)

    canvas[:h1, :w1] = img1
    canvas[:h2, w1:w1+w2] = img2

    # Draw divider
    cv2.line(canvas, (w1, 0), (w1, canvas_h), (45, 55, 72), 2)

    n_matches = min(len(pts_ref), len(pts_mov))
    step = max(1, n_matches // max_draw) if n_matches > max_draw else 1

    for i in range(0, n_matches, step):
        pt1 = (int(round(pts_ref[i][0])), int(round(pts_ref[i][1])))
        pt2 = (int(round(pts_mov[i][0])) + w1, int(round(pts_mov[i][1])))

        is_inlier = inlier_mask[i] if (inlier_mask is not None and i < len(inlier_mask)) else True
        color = color_inlier if is_inlier else color_outlier
        thickness = 2 if is_inlier else 1

        cv2.circle(canvas, pt1, 4, color, -1)
        cv2.circle(canvas, pt2, 4, color, -1)
        cv2.line(canvas, pt1, pt2, color, thickness, cv2.LINE_AA)

    return canvas
