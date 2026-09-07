from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .api import (
    health_router,
    images_router,
    pipeline_router,
    experiments_router,
    results_router
)
from .utils.logging import logger

app = FastAPI(
    title="LunarMatch API",
    description=(
        "Multi-Modal Lunar Image Correspondence & Registration Engine. "
        "Target: Smart India Hackathon 2026 | Problem Statement: 26166 | "
        "Organization: ISRO | Team: LunarMatch | Domain: Space Technology"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for Flutter web, mobile emulator, and local desktop
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(health_router)
app.include_router(images_router)
app.include_router(pipeline_router)
app.include_router(experiments_router)
app.include_router(results_router)

@app.get("/", tags=["Root"])
def root_index():
    return {
        "service": "LunarMatch API",
        "description": "Multi-Modal Lunar Image Correspondence & Registration",
        "team": "LunarMatch",
        "problem_statement": "26166 (ISRO)",
        "docs_url": "/docs",
        "health_url": "/health",
        "capabilities_url": "/api/v1/capabilities",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
