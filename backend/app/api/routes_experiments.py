from fastapi import APIRouter, HTTPException
from ..models.requests import RobustnessExperimentRequest
from ..models.responses import RobustnessExperimentResponse
from ..services.experiment_service import experiment_service
from ..utils.logging import logger

router = APIRouter(prefix="/api/v1/experiments", tags=["Experiments"])

@router.post("/robustness", response_model=RobustnessExperimentResponse)
def run_robustness_experiment(request: RobustnessExperimentRequest):
    """
    Execute controlled prototype robustness experiment.
    Evaluates inlier count, ratio, coverage, and RMSE across algorithmic parameter sweeps
    under controlled illumination, scale, rotation, and noise variations.
    """
    try:
        return experiment_service.run_robustness_experiment(request)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Experiment execution error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Experiment error: {str(e)}")
