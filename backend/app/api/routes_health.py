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
    Return comprehensive, scientifically honest implementation status matrix.
    Delineates IMPLEMENTED baseline components, SIMULATED demo components, and PLANNED research extensions.
    """
    items = [
        CapabilityItem(
            name="SIFT Feature Extraction",
            category="Detection & Description",
            status=ImplementationStatus.IMPLEMENTED,
            verified=True,
            notes="OpenCV SIFT implementation with configurable octave layers, peak and edge thresholds.",
        ),
        CapabilityItem(
            name="BFMatcher (L2 Norm)",
            category="Correspondence Search",
            status=ImplementationStatus.IMPLEMENTED,
            verified=True,
            notes="Brute-force descriptor matching over full L2 distance space.",
        ),
        CapabilityItem(
            name="FLANN Matcher",
            category="Correspondence Search",
            status=ImplementationStatus.IMPLEMENTED,
            verified=True,
            notes="Fast Library for Approximate Nearest Neighbors with KD-Tree indexing.",
        ),
        CapabilityItem(
            name="Lowe's Ratio Test",
            category="Outlier Rejection",
            status=ImplementationStatus.IMPLEMENTED,
            verified=True,
            notes="Dual nearest-neighbor ambiguity ratio rejection filter.",
        ),
        CapabilityItem(
            name="RANSAC Robust Estimation",
            category="Geometric Verification",
            status=ImplementationStatus.IMPLEMENTED,
            verified=True,
            notes="Random Sample Consensus with mathematical determinant and conditioning validation.",
        ),
        CapabilityItem(
            name="Homography Registration",
            category="Transformation",
            status=ImplementationStatus.IMPLEMENTED,
            verified=True,
            notes="Full 8-DOF planar projective coordinate warp via cv2.warpPerspective.",
        ),
        CapabilityItem(
            name="Affine Registration",
            category="Transformation",
            status=ImplementationStatus.IMPLEMENTED,
            verified=True,
            notes="6-DOF scale, rotation, translation, and shear warp via cv2.warpAffine.",
        ),
        CapabilityItem(
            name="Spatial Grid Balancing",
            category="Spatial Distribution",
            status=ImplementationStatus.IMPLEMENTED,
            verified=True,
            notes="N x N cell partitioning with top-k quality selection and coverage percentage metric.",
        ),
        CapabilityItem(
            name="Reprojection RMSE",
            category="Evaluation Metrics",
            status=ImplementationStatus.IMPLEMENTED,
            verified=True,
            notes="Measured pixel error calculation over verified inliers (reports N/A if unverified).",
        ),
        CapabilityItem(
            name="RIFT (Radiation-Invariant)",
            category="Multi-Modal Research",
            status=ImplementationStatus.SIMULATED,
            verified=True,
            notes="Deterministic simulation engine with fixed seed 26166. Advanced phase-congruency model planned.",
        ),
        CapabilityItem(
            name="SuperPoint Deep Features",
            category="Learned Detectors",
            status=ImplementationStatus.SIMULATED,
            verified=True,
            notes="Deterministic simulation engine with fixed seed 26166. Deep neural network weights planned.",
        ),
        CapabilityItem(
            name="LightGlue Graph Matcher",
            category="Deep Match Filtering",
            status=ImplementationStatus.PLANNED,
            verified=False,
            notes="Deep attention correspondence pruning scheduled for research roadmap.",
        ),
        CapabilityItem(
            name="RANSAC++ Spatial Consensus",
            category="Advanced Robust Geometry",
            status=ImplementationStatus.PLANNED,
            verified=False,
            notes="Non-uniform spatial sampling RANSAC variant scheduled for future release.",
        ),
        CapabilityItem(
            name="Sub-Pixel Refinement",
            category="Fine Alignment",
            status=ImplementationStatus.PLANNED,
            verified=False,
            notes="Gradient/patch optimization stub present; scientific validation planned.",
        ),
    ]

    return CapabilitiesResponse(
        capabilities=items,
        pipeline_version="1.0.0-mvp",
        verification_date="2026-09-06",
    )
