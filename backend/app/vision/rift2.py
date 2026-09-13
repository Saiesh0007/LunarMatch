import time
from typing import List, Tuple, Optional
import numpy as np
import cv2
from .extractor import BaseFeatureExtractor
from ..utils.logging import logger

def construct_log_gabor_filter_bank(
    rows: int,
    cols: int,
    n_scales: int = 4,
    n_orientations: int = 6,
    min_wavelength: float = 3.0,
    mult_factor: float = 2.0,
    sigma_onf: float = 0.55,
    sigma_theta: float = 0.65,
) -> List[List[np.ndarray]]:
    """
    Construct 2D Log-Gabor filter bank in frequency domain (Li et al., Kovesi 1999).
    Parameters:
        rows, cols: Image spatial dimensions
        n_scales: Number of scale octaves (default: 4)
        n_orientations: Number of directional orientations (default: 6)
        min_wavelength: Center wavelength of highest frequency filter (default: 3.0 px)
        mult_factor: Scaling factor between successive filters (default: 2.0)
        sigma_onf: Ratio of standard deviation to center frequency (radial, default: 0.55)
        sigma_theta: Angular spread standard deviation (default: 0.65)
    Returns:
        List of length n_scales, each containing list of n_orientations 2D filter arrays.
    """
    # Frequency coordinate grids centered at (0, 0)
    u = np.fft.fftfreq(cols).reshape(1, -1)
    v = np.fft.fftfreq(rows).reshape(-1, 1)
    radius = np.sqrt(u ** 2 + v ** 2)
    theta = np.arctan2(-v, u)

    # Prevent division by zero at DC
    radius_clean = radius.copy()
    radius_clean[0, 0] = 1.0

    # Low-pass filter to prevent wrap-around high-frequency ringing (Butterworth order 15)
    cutoff = 0.45
    low_pass = 1.0 / (1.0 + (radius / cutoff) ** 30)
    low_pass[0, 0] = 0.0

    filter_bank: List[List[np.ndarray]] = []

    for s in range(n_scales):
        wavelength = min_wavelength * (mult_factor ** s)
        fo = 1.0 / wavelength  # Center frequency
        # Radial log-Gabor component
        radial = np.exp(-((np.log(radius_clean / fo)) ** 2) / (2.0 * (np.log(sigma_onf) ** 2)))
        radial = radial * low_pass
        radial[0, 0] = 0.0

        scale_filters: List[np.ndarray] = []
        for o in range(n_orientations):
            angle_o = o * np.pi / n_orientations
            # Angular distance accounting for half-plane symmetry in frequency domain
            diff_theta = np.abs(theta - angle_o)
            diff_theta = np.minimum(diff_theta, np.pi - diff_theta)
            # Angular Gaussian component
            angular = np.exp(-(diff_theta ** 2) / (2.0 * (sigma_theta ** 2)))

            # 2D Log-Gabor filter
            filter_2d = (radial * angular).astype(np.float32)
            scale_filters.append(filter_2d)

        filter_bank.append(scale_filters)

    return filter_bank

def compute_phase_congruency_and_mim(
    image_gray: np.ndarray,
    n_scales: int = 4,
    n_orientations: int = 6,
    noise_threshold: float = 1e-3,
    return_amplitudes: bool = False,
):
    """
    Compute Phase Congruency principal moments and Maximum Index Map (MIM).
    Returns:
        pc_max: Maximum moment map (edge-like features) [H, W]
        pc_min: Minimum moment map (corner-like features) [H, W]
        mim: Maximum Index Map [H, W] with orientation indices in [0, n_orientations - 1]
        sum_amplitudes (optional): 3D array [H, W, n_orientations] of summed amplitude responses
    """
    img_f = image_gray.astype(np.float32)
    rows, cols = img_f.shape[:2]

    # Pre-construct filter bank
    filters = construct_log_gabor_filter_bank(rows, cols, n_scales, n_orientations)

    # 2D FFT of input image
    f_img = np.fft.fft2(img_f)

    sum_amplitudes = np.zeros((rows, cols, n_orientations), dtype=np.float32)
    energy_orientations = np.zeros((rows, cols, n_orientations), dtype=np.float32)

    for o in range(n_orientations):
        sum_e = np.zeros((rows, cols), dtype=np.float32)
        sum_o_resp = np.zeros((rows, cols), dtype=np.float32)
        sum_a = np.zeros((rows, cols), dtype=np.float32)

        for s in range(n_scales):
            # Fast frequency domain multiplication & IFFT
            filtered_fft = f_img * filters[s][o]
            spatial_resp = np.fft.ifft2(filtered_fft)

            even = np.real(spatial_resp).astype(np.float32)
            odd = np.imag(spatial_resp).astype(np.float32)
            amp = np.sqrt(even ** 2 + odd ** 2)

            sum_e += even
            sum_o_resp += odd
            sum_a += amp

        sum_amplitudes[:, :, o] = sum_a
        # Orientation energy
        energy = np.sqrt(sum_e ** 2 + sum_o_resp ** 2)
        energy_orientations[:, :, o] = np.maximum(0.0, energy - noise_threshold)

    # Compute Kovesi Phase Congruency principal moments from orientation components
    cov_x = np.zeros((rows, cols), dtype=np.float32)
    cov_y = np.zeros((rows, cols), dtype=np.float32)
    a = np.zeros((rows, cols), dtype=np.float32)
    b = np.zeros((rows, cols), dtype=np.float32)
    c = np.zeros((rows, cols), dtype=np.float32)

    for o in range(n_orientations):
        ang = o * np.pi / n_orientations
        pc_o = energy_orientations[:, :, o] / (sum_amplitudes[:, :, o] + 1e-4)
        cos_ang = np.cos(ang)
        sin_ang = np.sin(ang)

        cov_x += pc_o * cos_ang
        cov_y += pc_o * sin_ang
        a += (pc_o * cos_ang) ** 2
        b += 2.0 * (pc_o * cos_ang) * (pc_o * sin_ang)
        c += (pc_o * sin_ang) ** 2

    # Principal moments
    sqrt_term = np.sqrt(b ** 2 + (a - c) ** 2)
    pc_max = 0.5 * (c + a + sqrt_term)  # Edges
    pc_min = 0.5 * np.maximum(0.0, c + a - sqrt_term)  # Corners

    # Construct Maximum Index Map (MIM)
    mim = np.argmax(sum_amplitudes, axis=-1).astype(np.int32)

    if return_amplitudes:
        return pc_max, pc_min, mim, sum_amplitudes
    return pc_max, pc_min, mim

def _refine_subpixel_parabolic(response_map: np.ndarray, x: int, y: int) -> Tuple[float, float]:
    """Refine keypoint peak to sub-pixel accuracy (~0.1 px) via parabolic interpolation (Correction 2)."""
    h, w = response_map.shape[:2]
    if x <= 0 or x >= w - 1 or y <= 0 or y >= h - 1:
        return float(x), float(y)

    # Horizontal 1D slice
    dx1 = float(response_map[y, x + 1]) - float(response_map[y, x - 1])
    dx2 = 2.0 * float(response_map[y, x]) - float(response_map[y, x + 1]) - float(response_map[y, x - 1])
    shift_x = (dx1 / (2.0 * dx2 + 1e-6)) if abs(dx2) > 1e-6 else 0.0

    # Vertical 1D slice
    dy1 = float(response_map[y + 1, x]) - float(response_map[y - 1, x])
    dy2 = 2.0 * float(response_map[y, x]) - float(response_map[y + 1, x]) - float(response_map[y - 1, x])
    shift_y = (dy1 / (2.0 * dy2 + 1e-6)) if abs(dy2) > 1e-6 else 0.0

    shift_x = float(np.clip(shift_x, -0.5, 0.5))
    shift_y = float(np.clip(shift_y, -0.5, 0.5))

    return float(x) + shift_x, float(y) + shift_y

class RIFT2Extractor(BaseFeatureExtractor):
    """
    Radiation-variation Insensitive Feature Transform 2 (RIFT2) Extractor.
    Reference: Li et al., 2023 (arXiv:2303.00319) & Li et al., 2020 (IEEE TIP).
    Implements:
    - Log-Gabor filter bank & Kovesi phase congruency.
    - Maximum Index Map (MIM) construction.
    - FAST & corner keypoint detection with sub-pixel parabolic refinement.
    - Dominant index normalization (speedup over 6-ring convolution).
    - 216-dimensional (6x6x6) normalized descriptor with Gaussian weighting.
    """

    def __init__(
        self,
        n_scales: int = 4,
        n_orientations: int = 6,
        patch_size: int = 96,
        max_features: int = 2000,
        fast_threshold: float = 0.05,
    ):
        self.n_scales = n_scales
        self.n_orientations = n_orientations
        self.patch_size = patch_size
        self.max_features = max_features
        self.fast_threshold = fast_threshold

    def extract(
        self,
        img: np.ndarray,
        phase_map: Optional[np.ndarray] = None,
    ) -> Tuple[List[cv2.KeyPoint], np.ndarray]:
        """Extract RIFT2 features, optionally using a supplied phase-congruency map."""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()

        h, w = gray.shape[:2]
        if h < 32 or w < 32:
            return [], np.empty((0, 216), dtype=np.float32)

        # 1. Compute Phase Congruency & MIM, or use the supplied phase map.
        if phase_map is None:
            pc_max, pc_min, mim, sum_amps = compute_phase_congruency_and_mim(
                gray, n_scales=self.n_scales, n_orientations=self.n_orientations, return_amplitudes=True
            )
        else:
            pc_max = np.ascontiguousarray(phase_map, dtype=np.float32)
            if pc_max.shape != gray.shape:
                raise ValueError("phase_map must have the same shape as img")
            pc_min = pc_max
            sum_amps = np.repeat(
                pc_max[:, :, np.newaxis], self.n_orientations, axis=2
            ).astype(np.float32)
            mim = np.zeros(gray.shape, dtype=np.int32)

        # 2. Detect keypoints on pc_max (edges) and pc_min (corners)
        norm_max = cv2.normalize(pc_max, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        norm_min = cv2.normalize(pc_min, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        # Use adaptive FAST detector or Harris corner response on PC maps
        fast = cv2.FastFeatureDetector_create(threshold=12, nonmaxSuppression=True)
        kps_edge = fast.detect(norm_max, None)
        kps_corner = fast.detect(norm_min, None)

        raw_kps = list(kps_edge) + list(kps_corner)

        # Fallback to GoodFeaturesToTrack on PC maps if FAST returns few points
        if len(raw_kps) < 40:
            corners = cv2.goodFeaturesToTrack(norm_max, maxCorners=self.max_features, qualityLevel=0.01, minDistance=5)
            if corners is not None:
                for pt in corners:
                    raw_kps.append(cv2.KeyPoint(float(pt[0][0]), float(pt[0][1]), 16.0))

        if not raw_kps:
            return [], np.empty((0, 216), dtype=np.float32)

        # Sort by response and limit to max_features
        raw_kps = sorted(raw_kps, key=lambda k: k.response if k.response > 0 else 1.0, reverse=True)
        raw_kps = raw_kps[: self.max_features]

        # 3. Refine keypoints and assign canonical orientation
        half_p = self.patch_size // 2
        valid_kps: List[cv2.KeyPoint] = []
        descriptors_list: List[np.ndarray] = []

        # Precompute Gaussian weighting mask for the 96x96 patch
        sigma_patch = self.patch_size / 2.0  # sigma = 48 px
        y_grid, x_grid = np.ogrid[: self.patch_size, : self.patch_size]
        gaussian_weight = np.exp(-((x_grid - half_p) ** 2 + (y_grid - half_p) ** 2) / (2.0 * (sigma_patch ** 2))).astype(np.float32)

        for kp in raw_kps:
            ix, iy = int(round(kp.pt[0])), int(round(kp.pt[1]))
            # Boundary guard: ensure patch fits within image boundaries
            if ix < half_p or ix >= w - half_p or iy < half_p or iy >= h - half_p:
                continue

            # Sub-pixel parabolic refinement (Correction 2)
            sub_x, sub_y = _refine_subpixel_parabolic(pc_max, ix, iy)

            # Determine canonical orientation from local gradient of phase congruency
            # Sample 7x7 patch around keypoint on pc_max
            gx = float(pc_max[iy, min(w - 1, ix + 1)] - pc_max[iy, max(0, ix - 1)])
            gy = float(pc_max[min(h - 1, iy + 1), ix] - pc_max[max(0, iy - 1), ix])
            angle_deg = float(np.degrees(np.arctan2(gy, gx)))
            if angle_deg < 0:
                angle_deg += 360.0

            # 4. Extract rotation-aligned patch via bilinear interpolation (Correction 1 & 2)
            # Affine transform mapping rotated canonical patch -> image coordinates
            rot_mat = cv2.getRotationMatrix2D((sub_x, sub_y), angle_deg, 1.0)
            rot_mat[0, 2] += (half_p - sub_x)
            rot_mat[1, 2] += (half_p - sub_y)

            # Bilinearly interpolate each orientation channel's amplitude across the patch
            patch_amps = np.zeros((self.patch_size, self.patch_size, self.n_orientations), dtype=np.float32)
            for o in range(self.n_orientations):
                patch_amps[:, :, o] = cv2.warpAffine(
                    sum_amps[:, :, o],
                    rot_mat,
                    (self.patch_size, self.patch_size),
                    flags=cv2.INTER_LINEAR,
                    borderMode=cv2.BORDER_REFLECT,
                )

            # Compute MIM for the patch from continuous bilinearly-interpolated responses
            patch_mim = np.argmax(patch_amps, axis=-1).astype(np.int32)

            # 5. Dominant Index Normalization (RIFT2 speedup)
            # Find histogram peak of orientations in the patch
            hist, _ = np.histogram(patch_mim, bins=self.n_orientations, range=(0, self.n_orientations))
            dom_idx = int(np.argmax(hist))

            # Recode patch MIM: cyclically shift indices
            patch_mim_norm = (patch_mim - dom_idx) % self.n_orientations

            # 6. SIFT-style 6x6x6 grid descriptor (216 dimensions)
            grid_n = 6
            cell_size = self.patch_size // grid_n  # 16 px per cell
            desc_vector = np.zeros((grid_n * grid_n * self.n_orientations,), dtype=np.float32)

            idx = 0
            for r in range(grid_n):
                for c in range(grid_n):
                    r_start, r_end = r * cell_size, (r + 1) * cell_size
                    c_start, c_end = c * cell_size, (c + 1) * cell_size

                    cell_indices = patch_mim_norm[r_start:r_end, c_start:c_end]
                    cell_weights = gaussian_weight[r_start:r_end, c_start:c_end]

                    # Weighted histogram of orientation indices in cell
                    cell_hist = np.zeros(self.n_orientations, dtype=np.float32)
                    for o in range(self.n_orientations):
                        cell_hist[o] = float(np.sum(cell_weights[cell_indices == o]))

                    desc_vector[idx : idx + self.n_orientations] = cell_hist
                    idx += self.n_orientations

            # 7. Normalize descriptor (L2 norm + 0.2 threshold clamp + re-normalize)
            l2_norm = np.linalg.norm(desc_vector)
            if l2_norm > 1e-6:
                desc_vector = desc_vector / l2_norm
                desc_vector = np.clip(desc_vector, 0.0, 0.2)
                l2_norm2 = np.linalg.norm(desc_vector)
                if l2_norm2 > 1e-6:
                    desc_vector = desc_vector / l2_norm2

            # Store keypoint
            refined_kp = cv2.KeyPoint(
                x=float(sub_x),
                y=float(sub_y),
                size=float(self.patch_size),
                angle=float(angle_deg),
                response=float(kp.response),
            )
            valid_kps.append(refined_kp)
            descriptors_list.append(desc_vector)

        if not descriptors_list:
            return [], np.empty((0, 216), dtype=np.float32)

        descriptors = np.vstack(descriptors_list).astype(np.float32)
        logger.info(f"RIFT2 extracted {len(valid_kps)} keypoints with 216-D descriptors")
        return valid_kps, descriptors

def extract_rift2(image_gray: np.ndarray, max_features: int = 2000) -> Tuple[List[cv2.KeyPoint], np.ndarray]:
    """Expose high-level RIFT2 feature extraction API."""
    extractor = RIFT2Extractor(max_features=max_features)
    return extractor.extract(image_gray)


def compute_phase_congruency(image_gray: np.ndarray) -> np.ndarray:
    """Compute the base phase-congruency response map.

    Args:
        image_gray: Two-dimensional grayscale image.
    Returns:
        The maximum phase-congruency moment map as float32.
    Raises:
        ValueError: If the input is not a two-dimensional image.
    """
    if image_gray.ndim != 2:
        raise ValueError("image_gray must be a two-dimensional array")
    pc_max, _, _ = compute_phase_congruency_and_mim(image_gray)
    return np.ascontiguousarray(pc_max, dtype=np.float32)


def extract_rift2_on_pc(
    phase_map: np.ndarray,
    max_features: int = 2000,
) -> Tuple[List[cv2.KeyPoint], np.ndarray]:
    """Extract RIFT2 descriptors directly from a phase-congruency map.

    Args:
        phase_map: Grayscale phase-congruency response map.
        max_features: Maximum number of keypoints to retain.
    Returns:
        Keypoints and 216-dimensional descriptors.
    Raises:
        ValueError: If the phase map is not a two-dimensional array.
    """
    if phase_map.ndim != 2:
        raise ValueError("phase_map must be a two-dimensional array")
    extractor = RIFT2Extractor(max_features=max_features)
    return extractor.extract(phase_map, phase_map=phase_map)
