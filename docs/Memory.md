# LunarMatch — Project Memory

This file is the persistent project context for future development sessions.

## 1. Project Identity

**Project:** LunarMatch

**Competition:** Smart India Hackathon 2026

**Problem Statement ID:** 26166

**Problem Statement:** Multi-modal, Sun angle and scale invariant image correspondence using Chandrayaan-2 optical images (OHRC, TMC and IIRS)

**Organization:** Indian Space Research Organisation (ISRO)

**Department:** Department of Space / ISRO

**Category:** Software

**Theme:** Space Technology

**Team:** Spectrum

## 2. Official PS Requirements

The supplied SIH problem statement identifies the core challenge as registration/correspondence between lunar images acquired:
- at different times
- from different viewpoints
- with different sensors
- under different illumination
- at different scales/resolutions

The important requested properties are:
- illumination robustness
- viewpoint robustness
- scale robustness
- match-point correspondence
- registered product
- sub-pixel accuracy target
- uniform spatial distribution of match points
- quantitative evaluation such as RMSE, inlier match count and inlier ratio

The PS references Chandrayaan-2 optical payloads including OHRC, TMC-2 and IIRS and lists LRO NAC and SELENE as reference-image sources.

## 3. Existing Team Proposal

The team's submitted concept is called:

**LunarMatch Engine**

The PPT proposes a unified pipeline containing:
- illumination-aware preprocessing
- resolution alignment
- robust features: RIFT + SuperPoint
- learned matching: LightGlue / SuperGlue
- robust estimation: RANSAC++
- sub-pixel refinement
- spatially balanced correspondences

The PPT emphasizes:
- one pipeline for different lunar views
- multimodal differences
- viewpoint/geometric distortion
- illumination variation
- scale/resolution variation
- uniform match distribution
- sub-pixel accurate registration
- scalability

## 4. Research / Technology References Already in the Proposal

The PPT mentions classical approaches:
- SIFT
- ASIFT
- AKAZE
- RIFT

Learned approaches:
- SuperPoint
- SuperGlue
- LightGlue

Evaluation:
- RMSE
- inlier count
- inlier ratio
- spatial coverage

The PPT also references the Chandrayaan data portal and two research references supplied by the team.

## 5. Current Prototype Strategy

The prototype must prioritize a working end-to-end system over implementing every proposed research component.

### Minimum working path

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

### Enhanced path

```text
Input
→ illumination-aware preprocessing
→ resolution alignment
→ RIFT
→ robust matching
→ RANSAC
→ spatial balancing
→ registration
→ refinement
→ metrics
```

### Advanced path

```text
RIFT / SuperPoint
→ LightGlue / SuperGlue
→ robust geometric estimation
→ spatial balancing
→ sub-pixel refinement
```

## 6. Non-Negotiable Honesty Rule

Never claim that RIFT, SuperPoint, LightGlue, SuperGlue, RANSAC++, spatial balancing or sub-pixel refinement is implemented unless it has actually been implemented and tested.

A component can be described as:
- implemented
- experimental
- planned
- architectural extension

but these labels must remain accurate.

## 7. Demo Priorities

The strongest live demonstration is:

1. same-modality registration
2. cross-modal registration if a reliable pair is available
3. visible correspondence points
4. RANSAC inliers
5. spatially distributed points
6. registered output
7. quantitative metrics
8. controlled robustness test

## 8. Panel Positioning

The contribution is not "we invented SIFT."

The intended contribution is a unified lunar-registration pipeline that combines:
- modality-aware preprocessing
- scale/resolution handling
- robust correspondence
- geometric verification
- spatial balancing
- high-precision refinement
- measurable evaluation

## 9. Key Terminology

Use consistently:

- **Reference image:** fixed target coordinate system.
- **Moving image:** source image that is geometrically transformed.
- **Keypoint:** detected salient image location.
- **Descriptor:** numerical representation of a local feature.
- **Match:** candidate correspondence between two descriptors.
- **Inlier:** geometrically consistent match after robust estimation.
- **Registration:** transformation of the moving image into reference coordinates.
- **Spatial coverage:** how broadly selected correspondences cover the image.
- **RMSE:** root mean square registration/reprojection error under the chosen measurement definition.
- **Registration confidence:** prototype-level quality indicator, not an AI probability.

## 10. Current Development Principle

Build the smallest system that can demonstrate the PS requirements honestly, then add research components incrementally.
