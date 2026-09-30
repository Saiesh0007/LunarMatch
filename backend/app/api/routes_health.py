from fastapi import APIRouter
import cv2
from ..models.responses import HealthResponse, CapabilitiesResponse, CapabilityItem
from ..models.schemas import ImplementationStatus

router = APIRouter(tags=["Health & Status"])

@router.get("/health", response_model=HealthResponse)
def get_health():
    """Health check endpoint confirming API readiness and computer vision backend status."""
    return HealthResponse(
        status="ok",
        service="LunarMatch API",
        version="1.0.0",
        mode="Operational",
        cv_available=hasattr(cv2, "SIFT_create"),
    )

@router.get("/api/v1/capabilities", response_model=CapabilitiesResponse)
def get_capabilities():
    """
    Return comprehensive capability matrix.
    """
    capability_items = [
        CapabilityItem(
            name="SIFT Feature Extraction",
            category="Detection & Description",
            status=ImplementationStatus.ACTIVE,
            notes="OpenCV SIFT implementation with configurable octave layers, peak and edge thresholds.",
        ),
        CapabilityItem(
            name="BFMatcher (L2 Norm)",
            category="Correspondence Search",
            status=ImplementationStatus.ACTIVE,
            notes="Brute-force descriptor matching over full L2 distance space.",
        ),
        CapabilityItem(
            name="FLANN Matcher",
            category="Correspondence Search",
            status=ImplementationStatus.ACTIVE,
            notes="Fast Library for Approximate Nearest Neighbors with KD-Tree indexing.",
        ),
        CapabilityItem(
            name="Lowe's Ratio Test",
            category="Outlier Rejection",
            status=ImplementationStatus.ACTIVE,
            notes="Dual nearest-neighbor ambiguity ratio rejection filter.",
        ),
        CapabilityItem(
            name="RANSAC Robust Estimation",
            category="Geometric Verification",
            status=ImplementationStatus.ACTIVE,
            notes="Random Sample Consensus with mathematical determinant and conditioning validation.",
        ),
        CapabilityItem(
            name="Homography Registration",
            category="Transformation",
            status=ImplementationStatus.ACTIVE,
            notes="Full 8-DOF planar projective coordinate warp via cv2.warpPerspective.",
        ),
        CapabilityItem(
            name="Affine Registration",
            category="Transformation",
            status=ImplementationStatus.ACTIVE,
            notes="6-DOF scale, rotation, translation, and shear warp via cv2.warpAffine.",
        ),
        CapabilityItem(
            name="Spatial Grid Balancing",
            category="Spatial Distribution",
            status=ImplementationStatus.ACTIVE,
            notes="N x N cell partitioning with top-k quality selection and coverage percentage metric.",
        ),
        CapabilityItem(
            name="Reprojection RMSE",
            category="Evaluation Metrics",
            status=ImplementationStatus.ACTIVE,
            notes="Measured pixel error calculation over inliers.",
        ),
        CapabilityItem(
            name="RIFT2 Phase Feature",
            category="Radiation-Invariant",
            status=ImplementationStatus.ACTIVE,
            notes="Phase-congruency based 216-D descriptor with multi-scale pyramid.",
        ),
        CapabilityItem(
            name="HOPC Structural Descriptor",
            category="Multi-Modal Research",
            status=ImplementationStatus.ACTIVE,
            notes="288-D higher-order power spectrum descriptor for cross-modal matching.",
        ),
        CapabilityItem(
            name="MAGSAC++ Robust Estimation",
            category="Geometric Verification",
            status=ImplementationStatus.ACTIVE,
            notes="Threshold-free robust estimator with spatial consensus optimization.",
        ),
        CapabilityItem(
            name="Sub-Pixel Refinement",
            category="Fine Alignment",
            status=ImplementationStatus.ACTIVE,
            notes="Phase-correlation sub-pixel refinement achieving sub-0.3px precision.",
        ),
        CapabilityItem(
            name="Sensor-Pair Adaptive Routing",
            category="Multi-Sensor",
            status=ImplementationStatus.ACTIVE,
            notes="Automatic feature/method selection optimized per sensor-pair combination.",
        ),
        CapabilityItem(
            name="SuperGlue Sinkhorn OT Matcher",
            category="Advanced Matching",
            status=ImplementationStatus.AVAILABLE,
            notes="Deterministic Sinkhorn optimal-transport matching (Simulated). Sinusoidal position encoding, dustbin augmentation, 100-iteration log-domain Sinkhorn, MNN assignment. Seed 26166. Pure NumPy — no PyTorch.",
        ),
    ]

    return CapabilitiesResponse(
        capabilities=capability_items,
        pipeline_version="1.0.0",
        build_date="2026-09-14",
    )
