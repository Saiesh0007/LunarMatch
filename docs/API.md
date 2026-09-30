# LunarMatch — REST API Specification

FastAPI backend documentation and endpoints specification.

## Base URL
- Local / Windows Desktop: `http://127.0.0.1:8000`
- Android Emulator: `http://10.0.2.2:8000`

---

## 1. System Health
### `GET /health`
Returns service status, version, and OpenCV computer vision library availability.
```json
{
  "status": "ok",
  "service": "LunarMatch API",
  "version": "1.0.0",
  "mode": "Operational",
  "cv_available": true
}
```

---

## 2. Capabilities Matrix
### `GET /api/v1/capabilities`
Returns the scientifically honest implementation and verification status matrix.
```json
{
  "capabilities": [
    {
      "name": "SIFT Feature Extraction",
      "category": "Detection & Description",
      "status": "IMPLEMENTED",
      "verified": true,
      "notes": "OpenCV SIFT implementation with configurable parameters."
    },
    {
      "name": "RIFT (Radiation-Invariant)",
      "category": "Multi-Modal Research",
      "status": "SIMULATED",
      "verified": true,
      "notes": "Deterministic simulation engine (Seed 26166). Advanced phase congruency model planned."
    }
  ],
  "pipeline_version": "1.0.0-mvp",
  "verification_date": "2026-09-06"
}
```

---

## 3. Images Management
### `POST /api/v1/images/upload`
Upload an image multipart/form-data.
- **Request:** `file` (binary)
- **Response:**
```json
{
  "image_id": "3b29c91d-...",
  "filename": "lunar_crater.png",
  "width": 2048,
  "height": 2048,
  "channels": 1,
  "format": "png",
  "file_size_kb": 1042.5,
  "preview_url": "/api/v1/images/3b29c91d-.../preview"
}
```

### `GET /api/v1/images/demo`
Lists bundled demonstration pairs with provenance disclosures.
```json
[
  {
    "pair_id": "pair_a",
    "name": "Demo Pair A — Synthetic Lunar Prototype",
    "reference_sensor": "OHRC",
    "moving_sensor": "TMC-2",
    "provenance_note": "SYNTHETIC PROTOTYPE: Procedurally rendered crater terrain with known affine perturbation."
  }
]
```

### `GET /api/v1/images/{image_id}/preview`
Serves image raw stream directly.

---

## 4. Pipeline Execution
### `POST /api/v1/pipeline/run`
Executes registration pipeline.
- **Request:**
```json
{
  "reference_image_id": "demo_pair_a_ref",
  "moving_image_id": "demo_pair_a_mov",
  "reference_sensor": "OHRC",
  "moving_sensor": "TMC-2",
  "feature_method": "SIFT",
  "matcher": "BF",
  "ratio_threshold": 0.75,
  "geometric_model": "homography",
  "spatial_balancing": true,
  "grid_size": 6,
  "max_features_per_cell": 5,
  "ransac_threshold": 3.0,
  "max_features": 2000,
  "preprocessing": {
    "normalize": true,
    "clahe": true,
    "denoise": true
  },
  "simulation_mode": false
}
```

- **Response:**
```json
{
  "run_id": "run_20260906_162511_afcba5",
  "status": "SUCCESSFUL",
  "execution_mode": "LIVE BASELINE",
  "stages": [ ... ],
  "metrics": {
    "metric_mode": "MEASURED",
    "keypoints_reference": 1420,
    "keypoints_moving": 1385,
    "candidate_matches": 312,
    "filtered_matches": 118,
    "ransac_inliers": 84,
    "inlier_ratio": 71.2,
    "spatial_coverage": 77.8,
    "spatial_coverage_before": 38.9,
    "rmse_px": 1.48,
    "runtime_ms": 145.2,
    "confidence_level": "HIGH",
    "confidence_score": 0.88,
    "confidence_explanation": "High-confidence registration with strong spatial distribution..."
  },
  "spatial_stats": {
    "grid_size": 6,
    "total_cells": 36,
    "occupied_cells_before": 14,
    "occupied_cells_after": 28,
    "coverage_percentage_before": 38.9,
    "coverage_percentage_after": 77.8,
    "coverage_gain_percentage": 38.9
  },
  "outputs": {
    "registered_image_url": "/api/v1/results/run_20260906_.../artifact/registered.png",
    "overlay_image_url": "/api/v1/results/run_20260906_.../artifact/overlay.png",
    "difference_image_url": "/api/v1/results/run_20260906_.../artifact/difference.png",
    "correspondence_image_url": "/api/v1/results/run_20260906_.../artifact/correspondences.png"
  },
  "transformation_matrix": [ ... ]
}
```

---

## 5. Robustness Laboratory
### `POST /api/v1/experiments/robustness`
Evaluates parameter degradation sweep.
```json
{
  "base_image_id": "demo_pair_a_ref",
  "experiment_type": "illumination",
  "variation_steps": 5,
  "min_val": -40.0,
  "max_val": 40.0,
  "feature_method": "SIFT",
  "matcher": "BF"
}
```
