# LunarMatch — Development Phases

## Phase 0 — Prototype Freeze and Scope

### Objective
Define exactly what will be demonstrated and prevent scope explosion.

### Deliverables
- repository structure
- requirements
- known-good image pairs
- baseline success criteria
- demo sequence

### Exit Criteria
A known image pair can be loaded and processed end-to-end.

---

## Phase 1 — Registration Baseline

### Objective
Build the first completely working registration engine.

### Pipeline

```text
Preprocess
→ SIFT
→ BF/FLANN
→ ratio test
→ RANSAC
→ transformation
→ warp
```

### Metrics
- keypoints
- candidate matches
- filtered matches
- inliers
- inlier ratio
- reprojection/RMSE where defined

### Exit Criteria
A known-good pair produces a visually aligned result and reproducible metrics.

---

## Phase 2 — Visualization and Demo UI

### Objective
Make the working algorithm understandable to a panel.

### Deliverables
- Streamlit interface
- side-by-side inputs
- keypoints
- correspondence lines
- inlier visualization
- registered overlay
- metrics dashboard

### Exit Criteria
A complete demo can be run without editing source code.

---

## Phase 3 — Spatially Balanced Correspondences

### Objective
Directly address the PS requirement for uniform match distribution.

### Method

```text
Candidate matches
→ divide image into grid
→ assign matches to cells
→ rank by quality
→ retain strong matches across cells
→ calculate spatial coverage
```

### Deliverables
- spatial balancing module
- coverage metric
- before/after visualization

### Exit Criteria
The system can demonstrate the difference between clustered and spatially distributed correspondences.

---

## Phase 4 — Illumination Robustness

### Objective
Improve matching under different lighting conditions.

### Candidate operations
- intensity normalization
- CLAHE
- denoising
- illumination normalization
- gradient/orientation-based representations where appropriate

### Validation
Use controlled brightness/contrast changes and, where available, real multi-sun-angle imagery.

### Exit Criteria
The system reports measured changes in match/inlier performance rather than relying on visual claims.

---

## Phase 5 — Scale and Resolution Robustness

### Objective
Handle images acquired at different spatial resolutions/scales.

### Candidate techniques
- scale normalization
- image pyramids
- controlled resizing
- scale-aware feature extraction

### Validation
Create controlled scale changes and test actual performance.

### Exit Criteria
The pipeline can recover useful correspondences across selected scale variations.

---

## Phase 6 — RIFT Integration

### Objective
Add a feature representation better suited to difficult multimodal/illumination cases.

### Deliverables
- RIFT adapter implementing the same extractor interface
- comparison with SIFT
- matched/inlier metrics
- visual comparison

### Exit Criteria
RIFT runs successfully on at least one test pair and its results are recorded.

If implementation becomes unstable before the prototype deadline, keep SIFT as the verified baseline and mark RIFT as the next-stage module.

---

## Phase 7 — Learned Correspondence

### Objective
Evaluate SuperPoint + LightGlue/SuperGlue as an advanced correspondence pipeline.

### Deliverables
- model loading
- inference
- correspondence visualization
- benchmark against baseline

### Risks
- model availability
- download time
- hardware constraints
- dependency conflicts
- inference latency

### Exit Criteria
The learned pipeline produces reproducible correspondences on the target test set.

This phase is optional for the first internal prototype.

---

## Phase 8 — Sub-Pixel Refinement

### Objective
Address the high-precision registration requirement.

### Deliverables
- local refinement method
- defined sub-pixel error metric
- numerical validation against a known reference

### Important
Do not call the registration "sub-pixel accurate" simply because the output looks aligned.

### Exit Criteria
A measurable sub-pixel refinement result is demonstrated under a defined evaluation protocol.

---

## Phase 9 — Benchmarking

### Objective
Turn the prototype into an evidence-backed research system.

### Test dimensions
- same modality
- cross modality
- illumination variation
- scale variation
- viewpoint variation
- difficult/low-texture regions

### Metrics
- RMSE
- inlier count
- inlier ratio
- spatial coverage
- processing time
- failure rate

### Deliverables
- CSV/JSON experiment logs
- plots/tables
- reproducible configurations

---

## Phase 10 — Geospatial / Product Integration

### Objective
Move from image registration demonstration toward a usable lunar data product.

### Candidate additions
- GeoTIFF support
- coordinate/reference-system handling
- metadata preservation
- geospatial footprints
- registered raster export

### Exit Criteria
The registered product preserves required metadata and can be used by downstream lunar-analysis workflows.

---

## Phase 11 — Final Research Prototype

### Target Pipeline

```text
Multimodal input
→ illumination-aware preprocessing
→ resolution alignment
→ RIFT / SuperPoint
→ LightGlue / SuperGlue
→ robust geometric estimation
→ spatial balancing
→ high-precision refinement
→ registered product
→ evaluation
```

The final system should be benchmarked rather than described only through architecture diagrams.

---

## Emergency 10-Hour Prototype Plan

If the deadline is immediate:

### Hours 0–2
Get image loading, preprocessing and SIFT registration working.

### Hours 2–4
Implement matching, RANSAC and registration metrics.

### Hours 4–6
Build Streamlit UI and visual outputs.

### Hours 6–7
Implement spatial balancing.

### Hours 7–8
Prepare robustness experiments.

### Hours 8–9
Test 3–5 known-good image pairs and freeze the demo.

### Hour 9–10
Rehearse the complete demonstration and prepare fallback image pairs.

### Emergency rule
A reliable SIFT + RANSAC + spatial-balancing pipeline is better than a broken RIFT/LightGlue pipeline.
