from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse

from ..config import settings
from ..utils.file_utils import load_json

router = APIRouter(prefix="/api/v1/results", tags=["Results"])

@router.get("/{run_id}")
def get_run_results(run_id: str):
    """Retrieve full persisted experiment log and metrics for a given run ID."""
    run_dir = settings.OUTPUTS_DIR / run_id
    if not run_dir.exists():
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    log_path = run_dir / "experiment_log.json"
    if not log_path.exists():
        raise HTTPException(status_code=404, detail=f"Experiment log for {run_id} not found")

    return load_json(log_path)

@router.get("/{run_id}/artifact/{filename}")
def get_run_artifact(run_id: str, filename: str):
    """Stream generated image (registered.png, overlay.png, etc.) or JSON artifact."""
    run_dir = settings.OUTPUTS_DIR / run_id
    artifact_path = run_dir / filename
    
    # Path traversal protection
    if not artifact_path.resolve().is_relative_to(run_dir.resolve()):
        raise HTTPException(status_code=403, detail="Forbidden path")

    if not artifact_path.exists():
        raise HTTPException(status_code=404, detail=f"Artifact {filename} for run {run_id} not found")

    if filename.endswith(".json"):
        return JSONResponse(content=load_json(artifact_path))
    elif filename.endswith(".png"):
        return FileResponse(path=str(artifact_path), media_type="image/png")
    else:
        return FileResponse(path=str(artifact_path))
