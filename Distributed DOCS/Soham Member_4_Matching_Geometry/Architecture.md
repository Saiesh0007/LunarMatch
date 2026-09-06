# LunarMatch — SIH 2026 PS 26166

## Source of Truth

Official Problem Statement:
**26166 — Multi-modal, Sun angle and scale invariant image correspondence using Chandrayaan-2 optical images (OHRC, TMC and IIRS)**

The PS asks for a software solution that finds correspondence and registration between lunar images while addressing:
- illumination / sun-angle variation
- viewpoint variation
- scale variation
- different sensors and resolutions
- registered output with corresponding match points
- high-precision / sub-pixel accuracy target
- uniform spatial distribution of match points
- quantitative evaluation such as RMSE, inlier count and inlier ratio

The team's submitted concept is **LunarMatch Engine**. The PPT proposes:
- illumination-aware preprocessing
- resolution alignment
- RIFT + SuperPoint
- LightGlue / SuperGlue
- RANSAC++
- sub-pixel refinement
- spatially balanced correspondences
- a unified pipeline across OHRC, TMC and IIRS

## Immediate Prototype Principle

The internal-round prototype must prioritize a reliable end-to-end MVP over implementing every research component.

Minimum verified pipeline:

```text
Input
→ preprocessing
→ SIFT
→ descriptor matching
→ ratio filtering
→ RANSAC
→ transformation
→ registration
→ metrics
```

Enhanced modules are added only after the baseline works.

## Truthfulness Rule

Never claim that RIFT, SuperPoint, LightGlue/SuperGlue, RANSAC++, spatial balancing or sub-pixel refinement is implemented unless it actually runs and has been tested.

Use labels such as:
- IMPLEMENTED
- EXPERIMENTAL
- PLANNED

accurately.

## Integration Contract

All modules must exchange structured Python objects/dictionaries and must not depend on Streamlit/UI code.

Core conceptual interfaces:

```python
preprocess(image, sensor, config)
extract_features(image, method="sift")
match_features(desc_ref, desc_mov, method="bf")
estimate_transform(points_ref, points_mov, model="homography")
spatially_balance(matches, image_shape, grid=(4,4))
calculate_metrics(...)
register_image(moving, transformation, reference_shape)
run_lunarmatch(...)
```

The exact implementation can evolve, but the data contract must remain stable.

## Team Integration

Branches:

```text
main
develop
feature/preprocessing
feature/features
feature/matching
feature/spatial-metrics
feature/ui
```

No direct pushes to `main`.

Each member owns their module and tests. Member 1 owns integration.

## Demo Goal

The live prototype should show:

```text
Input lunar images
→ preprocessing
→ feature/keypoint visualization
→ correspondence visualization
→ RANSAC inliers
→ spatially distributed correspondences
→ registered image
→ RMSE / inlier count / inlier ratio / spatial coverage
```

At least one known-good demo pair must always be maintained.

# Member Role: Matching + Geometry Engineer

## Ownership

Descriptor matching, filtering, RANSAC, transformation estimation, image registration

## Module Boundary

This member owns only the components listed below.

Do not silently modify another member's module. Coordinate interface changes with Member 1.

## Dependencies

Upstream:
- image/data or outputs from upstream modules as defined below

Downstream:
- Member 1 integration pipeline
- other modules only through documented interfaces

## Expected Architecture

```text
UPSTREAM
   │
   ▼
[ MATCHING + GEOMETRY ENGINEER ]
   │
   ▼
STRUCTURED OUTPUT
   │
   ▼
Member 1 Integration
```

## Integration Principle

This module must work independently with test data before integration.

Do not import `app.py` or Streamlit into core processing code.
