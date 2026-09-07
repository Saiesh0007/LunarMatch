import math
from typing import Tuple, List, Optional
import cv2
import numpy as np

def generate_lunar_crater_surface(
    width: int = 512,
    height: int = 512,
    sun_azimuth_deg: float = 45.0,
    sun_elevation_deg: float = 30.0,
    seed: int = 26166,
    craters: Optional[List[dict]] = None,
) -> np.ndarray:
    """
    Procedurally synthesize a realistic lunar crater terrain surface.
    Produces high-contrast crater rims, shadow bowls, central peaks, and regolith noise.
    """
    rng = np.random.RandomState(seed)

    # 1. Base terrain heightmap using multi-octave smooth noise
    heightmap = np.zeros((height, width), dtype=np.float32)
    
    # Layer octaves
    for octave, freq in enumerate([4, 8, 16, 32, 64]):
        amp = 1.0 / (2.0 ** octave)
        grid_w, grid_h = max(2, width // freq), max(2, height // freq)
        noise = rng.randn(grid_h, grid_w).astype(np.float32)
        noise_resized = cv2.resize(noise, (width, height), interpolation=cv2.INTER_CUBIC)
        heightmap += amp * noise_resized

    # Normalize base terrain
    heightmap = (heightmap - heightmap.min()) / (heightmap.max() - heightmap.min() + 1e-6)

    # 2. Add impact craters
    if craters is None:
        craters = [
            {"cx": 0.35, "cy": 0.40, "radius": 0.18, "depth": 0.55, "central_peak": True},
            {"cx": 0.70, "cy": 0.30, "radius": 0.12, "depth": 0.45, "central_peak": False},
            {"cx": 0.25, "cy": 0.75, "radius": 0.10, "depth": 0.40, "central_peak": False},
            {"cx": 0.65, "cy": 0.70, "radius": 0.16, "depth": 0.50, "central_peak": True},
            {"cx": 0.50, "cy": 0.55, "radius": 0.08, "depth": 0.35, "central_peak": False},
            {"cx": 0.82, "cy": 0.80, "radius": 0.06, "depth": 0.30, "central_peak": False},
            {"cx": 0.15, "cy": 0.20, "radius": 0.07, "depth": 0.32, "central_peak": False},
            {"cx": 0.85, "cy": 0.15, "radius": 0.09, "depth": 0.38, "central_peak": False},
        ]

    y_grid, x_grid = np.mgrid[0:height, 0:width].astype(np.float32)

    for c in craters:
        cx_px = c["cx"] * width
        cy_px = c["cy"] * height
        r_px = c["radius"] * min(width, height)
        depth = c["depth"]
        
        dist = np.sqrt((x_grid - cx_px) ** 2 + (y_grid - cy_px) ** 2)
        norm_dist = dist / (r_px + 1e-6)

        # Crater profile: elevated rim at norm_dist ~ 1.0, deep bowl at norm_dist < 1.0
        crater_mask = norm_dist <= 1.4
        
        # Parabolic bowl depression
        bowl = np.clip(1.0 - (norm_dist ** 2), 0.0, 1.0) * depth
        # Raised rim
        rim = np.exp(-((norm_dist - 1.0) ** 2) / 0.05) * (depth * 0.35)

        # Central peak if specified
        peak = 0.0
        if c.get("central_peak", False):
            peak = np.exp(-(norm_dist ** 2) / 0.02) * (depth * 0.4)

        heightmap -= bowl * crater_mask
        heightmap += (rim + peak) * crater_mask

    # 3. Shaded relief rendering via surface normal gradients
    sun_az_rad = math.radians(sun_azimuth_deg)
    sun_el_rad = math.radians(sun_elevation_deg)

    # Sun direction vector
    sun_x = math.cos(sun_el_rad) * math.sin(sun_az_rad)
    sun_y = math.cos(sun_el_rad) * math.cos(sun_az_rad)
    sun_z = math.sin(sun_el_rad)

    # Gradients (sobel)
    grad_x = cv2.Sobel(heightmap, cv2.CV_32F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(heightmap, cv2.CV_32F, 0, 1, ksize=3)

    # Surface normals: (-grad_x, -grad_y, 1.0)
    norm = np.sqrt(grad_x ** 2 + grad_y ** 2 + 1.0)
    normal_x = -grad_x / norm
    normal_y = -grad_y / norm
    normal_z = 1.0 / norm

    # Lambertian reflectance (dot product with sun vector)
    diffuse = normal_x * sun_x + normal_y * sun_y + normal_z * sun_z
    diffuse = np.clip(diffuse, 0.05, 1.0)  # ambient lunar earthshine / shadow bounce

    # Final pixel values
    lunar_image = (diffuse * 255.0).astype(np.uint8)
    return lunar_image

def apply_controlled_variation(
    base_img: np.ndarray,
    scale: float = 1.0,
    rotation_deg: float = 0.0,
    tx_px: float = 0.0,
    ty_px: float = 0.0,
    brightness_offset: float = 0.0,
    contrast_factor: float = 1.0,
    noise_std: float = 0.0,
    seed: int = 26166,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Apply known, controlled geometric and radiometric transformations to an image.
    Returns:
        transformed_img: Transformed image
        ground_truth_matrix: 3x3 Homography matrix mapping Moving -> Reference coordinates
    """
    h, w = base_img.shape[:2]
    center = (w / 2.0, h / 2.0)

    # Affine matrix (center rotation + scale + translation)
    M_affine = cv2.getRotationMatrix2D(center, rotation_deg, scale)
    M_affine[0, 2] += tx_px
    M_affine[1, 2] += ty_px

    # Transform image
    transformed = cv2.warpAffine(base_img, M_affine, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

    # Radiometric variations
    if contrast_factor != 1.0 or brightness_offset != 0.0:
        transformed = cv2.convertScaleAbs(transformed, alpha=contrast_factor, beta=brightness_offset)

    if noise_std > 0:
        rng = np.random.RandomState(seed)
        noise = rng.normal(0, noise_std, transformed.shape).astype(np.float32)
        noisy = np.clip(transformed.astype(np.float32) + noise, 0, 255).astype(np.uint8)
        transformed = noisy

    # Ground truth 3x3 homography mapping from Moving back to Reference coordinate system:
    # M_affine maps Reference -> Moving, so the inverse maps Moving -> Reference
    M_homog = np.eye(3, dtype=np.float32)
    M_homog[:2, :] = M_affine
    M_inv = np.linalg.inv(M_homog)

    return transformed, M_inv
