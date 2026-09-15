from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .schemas import (
    RegistrationStatus,
    ConfidenceLevel,
    ExecutionMode,
    MetricMode,
    RegistrationMetrics,
    SpatialGridStats,
    ImplementationStatus
)

class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "LunarMatch API"
    version: str = "1.0.0"
    mode: str = "Operational"
    cv_available: bool = True

class ImageUploadResponse(BaseModel):
    image_id: str
    filename: str
    width: int
    height: int
    channels: int
    format: str
    file_size_kb: float
    preview_url: str

class DemoPairInfo(BaseModel):
    pair_id: str
    name: str
    description: str
    reference_image_id: str
    moving_image_id: str
    reference_sensor: str
    moving_sensor: str
    reference_preview_url: str
    moving_preview_url: str
    provenance_note: str

class PipelineStageInfo(BaseModel):
    stage_number: int
    name: str
    status: str  # PENDING | PROCESSING | COMPLETED | FAILED | SKIPPED
    duration_ms: float = 0.0
    details: Optional[str] = None

class ArtifactPaths(BaseModel):
    registered_image_url: Optional[str] = None
    overlay_image_url: Optional[str] = None
    difference_image_url: Optional[str] = None
    correspondence_image_url: Optional[str] = None
    artifacts_dir: str

class PipelineRunResponse(BaseModel):
    run_id: str
    status: RegistrationStatus
    execution_mode: ExecutionMode
    stages: List[PipelineStageInfo]
    metrics: RegistrationMetrics
    spatial_stats: Optional[SpatialGridStats] = None
    outputs: ArtifactPaths
    warnings: List[str] = []
    failure_reason: Optional[str] = None
    diagnostic_details: Dict[str, Any] = {}
    transformation_matrix: Optional[List[List[float]]] = None
    configuration: Dict[str, Any]

class RobustnessPointResult(BaseModel):
    variation_value: float
    variation_label: str
    inliers: int
    inlier_ratio: float
    spatial_coverage: float
    rmse_px: Optional[float]
    runtime_ms: float
    status: RegistrationStatus

class RobustnessExperimentResponse(BaseModel):
    experiment_id: str
    experiment_type: str
    base_image_id: str
    disclaimer: str = "CONTROLLED SYNTHETIC EXPERIMENT — For algorithmic robustness profiling only"
    points: List[RobustnessPointResult]
    summary: Dict[str, Any]

class CapabilityItem(BaseModel):
    name: str
    category: str
    status: ImplementationStatus
    notes: str

class CapabilitiesResponse(BaseModel):
    capabilities: List[CapabilityItem]
    pipeline_version: str = "1.0.0"
    build_date: str = "2026-09-14"
