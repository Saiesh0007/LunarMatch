from pathlib import Path
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from ..models.responses import ImageUploadResponse, DemoPairInfo
from ..services.image_service import image_service

router = APIRouter(prefix="/api/v1/images", tags=["Images"])

@router.post("/upload", response_model=ImageUploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """Upload a lunar image file (PNG, JPG, TIFF) for registration."""
    try:
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        return image_service.save_upload(content, file.filename or "upload.png")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process image: {str(e)}")

@router.get("/demo", response_model=List[DemoPairInfo])
def list_demo_pairs():
    """List bundled lunar demonstration image pairs with transparent provenance disclosures."""
    return image_service.get_demo_pairs()

@router.get("/{image_id}/preview")
def get_image_preview(image_id: str):
    """Retrieve and stream image file for visual preview."""
    try:
        resolved_path = image_service.resolve_image_path(image_id)
        return FileResponse(
            path=str(resolved_path),
            media_type="image/png",
            filename=resolved_path.name
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Image {image_id} not found")
