from fastapi import APIRouter, HTTPException
from ..models.requests import PipelineRunRequest
from ..models.responses import PipelineRunResponse
from ..services.pipeline_service import pipeline_service
from ..utils.logging import logger

router = APIRouter(prefix="/api/v1/pipeline", tags=["Pipeline"])

@router.post("/run", response_model=PipelineRunResponse)
def run_pipeline(request: PipelineRunRequest):
    """
    Execute LunarMatch correspondence & registration pipeline.
    Runs either LIVE (OpenCV SIFT, RANSAC, Spatial Grid) or
    DEMO (Seed 26166 deterministic engine for research exploration).
    """
    try:
        response = pipeline_service.execute_pipeline(request)
        return response
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Pipeline execution fatal error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")
