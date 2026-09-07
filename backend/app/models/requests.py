from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from .schemas import (
    SensorType,
    FeatureMethod,
    MatcherType,
    GeometricModel,
    PreprocessingConfig
)

class PipelineRunRequest(BaseModel):
    reference_image_id: str = Field(..., description="ID or path of the fixed reference image")
    moving_image_id: str = Field(..., description="ID or path of the moving image to transform")
    reference_sensor: SensorType = Field(SensorType.OHRC, description="Sensor for reference image")
    moving_sensor: SensorType = Field(SensorType.TMC_2, description="Sensor for moving image")
    feature_method: FeatureMethod = Field(FeatureMethod.SIFT, description="Feature extraction technique")
    matcher: MatcherType = Field(MatcherType.BF, description="Feature matching algorithm")
    ratio_threshold: float = Field(0.75, ge=0.4, le=0.95, description="Lowe's ratio test threshold")
    geometric_model: GeometricModel = Field(GeometricModel.HOMOGRAPHY, description="Transformation geometry")
    spatial_balancing: bool = Field(True, description="Enable spatial grid distribution filter")
    grid_size: int = Field(6, ge=2, le=16, description="NxN grid dimension for spatial balancing")
    max_features_per_cell: int = Field(5, ge=1, le=50, description="Max matches retained per grid cell")
    ransac_threshold: float = Field(3.0, ge=0.5, le=15.0, description="RANSAC inlier threshold in pixels")
    max_features: int = Field(2000, ge=100, le=10000, description="Max keypoints to extract")
    preprocessing: PreprocessingConfig = Field(default_factory=PreprocessingConfig)
    simulation_mode: bool = Field(False, description="Run deterministic simulation engine instead of live CV")
    fail_safe_override: bool = Field(False, description="For testing: force fail-safe trigger")

class RobustnessExperimentRequest(BaseModel):
    base_image_id: str = Field(..., description="Image ID to apply controlled variations to")
    experiment_type: str = Field("illumination", description="illumination | scale | rotation | translation | composite")
    variation_steps: int = Field(5, ge=3, le=10, description="Number of variation increments")
    min_val: float = Field(-50.0, description="Minimum parameter variation")
    max_val: float = Field(50.0, description="Maximum parameter variation")
    feature_method: FeatureMethod = Field(FeatureMethod.SIFT)
    matcher: MatcherType = Field(MatcherType.BF)
    ratio_threshold: float = Field(0.75)
    geometric_model: GeometricModel = Field(GeometricModel.HOMOGRAPHY)
    spatial_balancing: bool = Field(True)
    grid_size: int = Field(6)
