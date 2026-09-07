from typing import List, Tuple, Optional
import numpy as np
from ..models.schemas import MatchPairModel, ImplementationStatus
from ..utils.logging import logger

class SubPixelRefinement:
    """
    Sub-pixel correspondence refinement interface.
    
    IMPLEMENTATION STATUS: PLANNED
    In accordance with Non-Negotiable Rule A, sub-pixel accuracy is NOT claimed
    as fully implemented. This modular interface defines the API contract for future
    gradient/patch correlation refinement (e.g. Lucas-Kanade or quadratic interpolation).
    """

    STATUS: ImplementationStatus = ImplementationStatus.PLANNED

    @staticmethod
    def refine(
        ref_img: np.ndarray,
        mov_img: np.ndarray,
        matches: List[MatchPairModel]
    ) -> Tuple[List[MatchPairModel], dict]:
        """
        Stub for future sub-pixel optimization.
        Currently returns unmodified coordinates with transparent audit metadata.
        """
        logger.info("Sub-pixel refinement called: [STATUS: PLANNED / PROTOTYPE PASS-THROUGH]")
        return matches, {
            "status": SubPixelRefinement.STATUS.value,
            "applied": False,
            "note": "Sub-pixel optimization is planned for Phase 2 research integration.",
        }
