# LunarMatch — Project Specification

## 1. Project Overview

**LunarMatch** is a proposed software solution for SIH 2026 Problem Statement 26166.

The system addresses image correspondence and registration across lunar observations acquired under different:
- sensors
- illumination conditions
- viewpoints
- scales/resolutions

The initial target imagery includes Chandrayaan-2 OHRC, TMC/TMC-2 and IIRS, with lunar reference imagery such as LRO NAC and SELENE.

## 2. Problem

Lunar surface features can appear substantially different when captured:
- at different sun azimuth/elevation
- from different viewpoints
- at different altitudes
- using different sensors
- at different spatial resolutions

A simple pixel-to-pixel comparison is therefore insufficient for robust registration.

The requested solution must produce:
- correspondence points
- registered imagery
- quantitative evaluation
- high-precision alignment
- spatially useful match distributions

## 3. Proposed Solution

LunarMatch uses a modular correspondence pipeline.

### Core idea

```text
Different lunar images
        ↓
appearance normalization
        ↓
scale/resolution handling
        ↓
robust local features
        ↓
feature correspondence
        ↓
geometric verification
        ↓
spatially balanced matches
        ↓
registration
        ↓
high-precision refinement
        ↓
registered lunar product + metrics
```

## 4. Prototype Objective

The prototype is not required to implement every final research component.

The prototype objective is to prove that the central workflow works:

> Given a reference and moving lunar image, LunarMatch can identify reliable correspondences, reject false matches, estimate a geometric transformation, register the moving image, and report quantitative quality metrics.

## 5. MVP Scope

### Implement first

- image input
- preprocessing
- SIFT feature extraction
- descriptor matching
- ratio filtering
- RANSAC
- transformation estimation
- image warping
- correspondence visualization
- RMSE/reprojection metric where valid
- inlier count
- inlier ratio
- spatial coverage
- registered-image visualization

### Add if stable

- RIFT
- illumination-specific preprocessing
- scale experiments
- learned matching

### Do later

- validated sub-pixel refinement
- large-scale dataset processing
- geospatial product pipeline
- cloud deployment

## 6. Technology Stack

### Core
- Python
- OpenCV
- NumPy

### Optional numerical/image processing
- scikit-image

### Geospatial
- rasterio
- GDAL

Use geospatial libraries when the actual dataset format/metadata requires them.

### Interface
- Streamlit

### Advanced models
- RIFT implementation
- SuperPoint
- LightGlue / SuperGlue

Advanced models are optional for the first working MVP.

## 7. Repository Structure

```text
LunarMatch/
│
├── app.py
├── requirements.txt
├── README.md
│
├── src/
│   ├── __init__.py
│   ├── io.py
│   ├── preprocessing.py
│   ├── features.py
│   ├── matching.py
│   ├── geometry.py
│   ├── spatial.py
│   ├── registration.py
│   ├── refinement.py
│   └── metrics.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── examples/
│
├── outputs/
│   ├── matches/
│   ├── registered/
│   └── metrics/
│
├── experiments/
│   ├── configs/
│   └── results/
│
└── docs/
    ├── Architecture.md
    ├── Design.md
    ├── Memory.md
    ├── Phases.md
    ├── Project.md
    └── Rules.md
```

## 8. Core Interfaces

### Feature extractor

```text
extract(image)
→ keypoints, descriptors
```

### Matcher

```text
match(descriptors_a, descriptors_b)
→ candidate_matches
```

### Geometric estimator

```text
estimate(points_a, points_b)
→ transformation, inlier_mask
```

### Registrar

```text
register(reference, moving, transformation)
→ registered_image
```

### Metrics

```text
evaluate(matches, inliers, transformation)
→ metrics
```

These interfaces allow the baseline and advanced algorithms to coexist.

## 9. Evaluation

The prototype should record:

| Metric | Meaning |
|---|---|
| Keypoints | detected feature locations |
| Candidate matches | initial descriptor correspondences |
| Good matches | matches retained by descriptor filtering |
| Inlier count | geometrically consistent matches |
| Inlier ratio | inliers / selected matches |
| RMSE | defined registration/reprojection error |
| Spatial coverage | distribution of selected correspondences |
| Runtime | processing time |

Metrics must be calculated from actual runs.

## 10. Robustness Evaluation

The test suite should include controlled transformations:

### Illumination
- brightness increase
- brightness decrease
- contrast changes

### Scale
- downscale
- upscale

### Geometry
- rotation
- translation
- affine distortion

### Multimodal
- OHRC ↔ TMC
- OHRC ↔ IIRS
- Chandrayaan ↔ lunar reference imagery

Only use pairs that genuinely have overlapping content.

## 11. Expected Outputs

### Software
A runnable prototype.

### Registered product
An aligned moving image in the reference image coordinate system.

### Correspondence product
Visual and/or machine-readable match points.

### Evaluation report
Metrics such as:
- RMSE
- inlier count
- inlier ratio
- spatial coverage

## 12. Impact

Potential downstream uses identified in the team proposal include:
- scientific lunar terrain/geology/resource analysis
- mission planning and support
- multisensor lunar data integration
- map mosaicing
- change detection
- scientifically aligned lunar datasets

These are intended application areas; prototype validation should focus on correspondence and registration.

## 13. Success Criteria for the Internal Prototype

The prototype is considered successful when it can:

1. load two valid lunar images
2. identify meaningful features
3. produce candidate correspondences
4. reject obvious false matches
5. estimate a stable transformation
6. generate a visibly improved registered image
7. display corresponding match points
8. calculate meaningful metrics
9. show spatial distribution
10. handle at least one controlled variation experiment

## 14. Definition of Done

A feature is "done" only when:
- it runs from the UI or documented command
- it has been tested on the target image type
- its output is saved or reproducible
- its metrics are real
- its limitations are documented

## 15. Current Project Position

The team has cleared the internal PPT presentation round and is preparing a prototype demonstration.

Therefore, the immediate goal is a reliable MVP rather than a complete production system.
