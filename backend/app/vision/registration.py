from typing import Tuple, Optional
import cv2
import numpy as np
from ..models.schemas import GeometricModel
from ..utils.image_utils import create_overlay_image, create_difference_image
from ..utils.logging import logger

class ImageRegistration:
    """Coordinate transformation and output synthesis for Reference and Moving lunar images."""

    @staticmethod
    def warp_and_render(
        ref_img: np.ndarray,
        mov_img: np.ndarray,
        matrix: np.ndarray,
        model_type: GeometricModel = GeometricModel.HOMOGRAPHY,
        alpha_overlay: float = 0.5,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Warp Moving image into Reference image coordinate space.
        Returns:
            registered_img: Warped moving image
            overlay_img: Blended overlay (Reference + Registered Moving)
            difference_img: Absolute difference map highlighting registration accuracy
        """
        h_ref, w_ref = ref_img.shape[:2]

        if model_type == GeometricModel.HOMOGRAPHY:
            registered_img = cv2.warpPerspective(
                mov_img,
                matrix,
                (w_ref, h_ref),
                flags=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=0,
            )
        else:
            # Affine is 2x3
            registered_img = cv2.warpAffine(
                mov_img,
                matrix,
                (w_ref, h_ref),
                flags=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=0,
            )

        # Generate overlay and difference maps
        overlay_img = create_overlay_image(ref_img, registered_img, alpha=alpha_overlay)
        difference_img = create_difference_image(ref_img, registered_img)

        logger.info(f"Image Registration completed: Warped to reference dimensions ({w_ref}x{h_ref})")
        return registered_img, overlay_img, difference_img
