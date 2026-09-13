from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class SensorType(str, Enum):
    OHRC = "OHRC"
    TMC = "TMC"
    TMC_2 = "TMC-2"
    IIRS = "IIRS"
    LRO_NAC = "LRO NAC"
    SELENE = "SELENE"
    OTHER = "Other"

class FeatureMethod(str, Enum):
    RIFT2 = "rift2"
    RIFT2_MULTISCALE = "rift2_multiscale"
    SIFT = "sift"
    BOTH = "both"
    HOPC = "hopc"
    HOPC_RIFT2_FUSION = "hopc_rift2_fusion"
    SIFT_UPPER = "SIFT"
    RIFT_SIMULATED = "RIFT — SIMULATED"
    SUPERPOINT_SIMULATED = "SuperPoint — SIMULATED"

class MatcherType(str, Enum):
    BF = "BF"
    FLANN = "FLANN"

class GeometricModel(str, Enum):
    AFFINE = "affine"
    HOMOGRAPHY = "homography"

class EstimatorMethod(str, Enum):
    MAGSAC = "magsac"
    RANSAC = "ransac"

class RegistrationStatus(str, Enum):
    SUCCESSFUL = "SUCCESSFUL"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    NOT_RELIABLE = "NOT_RELIABLE"
    FAILED = "FAILED"

class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    REJECTED = "REJECTED"

class ExecutionMode(str, Enum):
    LIVE_BASELINE = "LIVE BASELINE"
    DEMO_SIMULATION = "DEMO SIMULATION"
    LOCAL_FALLBACK = "LOCAL FALLBACK"

class MetricMode(str, Enum):
    MEASURED = "MEASURED"
    SIMULATED = "SIMULATED"

class ImplementationStatus(str, Enum):
    IMPLEMENTED = "IMPLEMENTED"
    SIMULATED = "SIMULATED"
    PLANNED = "PLANNED"

class PreprocessingConfig(BaseModel):
    normalize: bool = True
    clahe: bool = True
    denoise: bool = True
    clip_limit: float = 2.0
    tile_grid_size: int = 8

class KeypointModel(BaseModel):
    x: float
    y: float
    size: Optional[float] = None
    angle: Optional[float] = None
    response: Optional[float] = None

class MatchPairModel(BaseModel):
    ref_idx: int
    mov_idx: int
    distance: float
    ref_pt: List[float]  # [x, y]
    mov_pt: List[float]  # [x, y]
    is_inlier: bool = False
    is_spatially_selected: bool = False

class SpatialGridStats(BaseModel):
    grid_size: int
    total_cells: int
    occupied_cells_before: int
    occupied_cells_after: int
    coverage_percentage_before: float
    coverage_percentage_after: float
    coverage_gain_percentage: float

class RegistrationMetrics(BaseModel):
    metric_mode: MetricMode = MetricMode.MEASURED
    simulation_seed: Optional[int] = None
    keypoints_reference: int
    keypoints_moving: int
    candidate_matches: int
    filtered_matches: int
    ransac_inliers: int
    inlier_ratio: float           # percentage 0.0 - 100.0
    spatial_coverage: float       # percentage 0.0 - 100.0
    spatial_coverage_before: float
    rmse_px: Optional[float] = None  # None / N/A if unreliable
    runtime_ms: float
    confidence_level: ConfidenceLevel
    confidence_score: float       # normalized score 0.0 - 1.0 (derived quality indicator)
    confidence_explanation: str
