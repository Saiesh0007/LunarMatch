# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**LunarMatch** is a prototype software pipeline for **SIH 2026 Problem Statement 26166 (ISRO / Space Technology)**: multi-modal, sun angle, and scale-invariant image correspondence and registration using Chandrayaan-2 optical imagery (OHRC, TMC/TMC-2, IIRS) and lunar reference imagery (LRO NAC, SELENE).

## Common Commands

### Environment & Dependencies
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Application Execution
```bash
# Run Streamlit UI demo
streamlit run app.py
```

### Testing
```bash
# Run all tests
pytest

# Run a single test file
pytest tests/test_pipeline.py

# Run a specific test function
pytest tests/test_features.py -k test_sift_extraction
```

### Linting & Formatting
```bash
flake8 src/ tests/
black --check src/ tests/
```

---

## High-Level Architecture & Pipeline

LunarMatch processes image pairs through a modular pipeline:

```text
Reference & Moving Images (OHRC / TMC / IIRS / LRO NAC)
        ↓
Image Validation & I/O (src/io.py)
        ↓
Illumination-Aware Preprocessing & Normalization (src/preprocessing.py)
        ↓
Scale / Resolution Alignment (src/preprocessing.py)
        ↓
Feature Extraction (src/features.py) — SIFT (baseline) | RIFT (experimental)
        ↓
Descriptor Matching & Ratio Filtering (src/matching.py) — BF / FLANN + Lowe's test
        ↓
Geometric Verification (src/geometry.py) — RANSAC affine/homography estimation
        ↓
Spatial Balancing (src/spatial.py) — Grid-based uniform match distribution
        ↓
Transformation & Warping (src/geometry.py)
        ↓
High-Precision Sub-Pixel Refinement (src/refinement.py, optional/experimental)
        ↓
Registered Lunar Product + Metrics Evaluation (src/metrics.py)
```

---

## Module & File Ownership Structure

| Module | Core Responsibility | Primary Interfaces |
|---|---|---|
| `src/pipeline.py` & `src/config.py` | Orchestration, end-to-end execution | `run_lunarmatch(ref, mov, ref_sensor, mov_sensor, config) -> dict` |
| `src/io.py` | Ingestion, format validation, metadata | `load_image(path) -> (image, metadata)` |
| `src/preprocessing.py` | Grayscale conversion, CLAHE, denoising, scale normalization | `preprocess(image, sensor, config) -> {"image", "metadata", "scale_factor"}` |
| `src/features.py` | Keypoint and descriptor extraction | `extract_features(image, method="sift") -> {"keypoints", "descriptors"}` |
| `src/matching.py` | Feature matching & Lowe's ratio test | `match_features(desc_ref, desc_mov, method="bf") -> matches` |
| `src/geometry.py` | RANSAC estimation, transformation, image warping | `estimate_transform(pts_ref, pts_mov, model="homography") -> (matrix, inliers)`<br>`warp_image(moving, transform, ref_shape) -> registered` |
| `src/spatial.py` | Grid-based spatial match balancing & coverage | `spatially_balance(matches, image_shape, grid=(4,4)) -> balanced_matches` |
| `src/metrics.py` | Quantitative metrics (RMSE, inliers, ratio, coverage, runtime) | `evaluate(matches, inliers, transformation, ...) -> dict` |
| `app.py` | Streamlit demo interface & visualization | Calls only `run_lunarmatch(...)` |

---

## Core Domain Rules & Conventions

- **Coordinate Conventions:**
  - **Reference (Fixed) Image:** Target coordinate space.
  - **Moving (Source) Image:** Transformed and warped into the reference coordinate system. Never invert these roles.
- **Match Lifecycle Hierarchy:**
  `Candidate matches → Filtered matches (ratio test) → Geometrically verified inliers (RANSAC) → Spatially balanced correspondences`.
- **Honesty & Status Classification:**
  Components must be accurately tagged: `IMPLEMENTED`, `EXPERIMENTAL`, or `PLANNED`.
  - Baseline MVP uses **SIFT + BF/FLANN + RANSAC + Grid Spatial Balancing**.
  - Advanced models (**RIFT**, **SuperPoint**, **LightGlue**, **sub-pixel refinement**) are experimental extensions and must not be claimed as complete without empirical validation.
- **No Fabricated Metrics:** All reported values (RMSE, inlier count, inlier ratio, spatial coverage) must be dynamically computed from actual runs.
- **Fail-Safe Operation:** If correspondences are insufficient or geometric estimation fails, return clear failure diagnostic reasons (e.g. low inlier ratio, insufficient keypoints) rather than producing an unverified/corrupted registration.
- **Data Directories:**
  - `data/raw/` — original, unmodified imagery.
  - `data/processed/` — preprocessed images.
  - `data/examples/` — known-good image pairs for offline deterministic demo fallbacks.
  - `outputs/` — warped products, correspondence plots, and benchmark JSON/CSV logs.
