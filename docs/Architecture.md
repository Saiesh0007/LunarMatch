# LunarMatch — Architecture & Scientific Framework

**Target:** Smart India Hackathon 2026 | **Problem Statement:** 26166 | **Organization:** ISRO | **Team:** LunarMatch | **Domain:** Space Technology

---

## 1. System Overview
LunarMatch is an engineering prototype designed for multi-modal, cross-sensor correspondence and registration of lunar orbital imagery (such as Chandrayaan-2 OHRC, TMC-2 stereo, IIRS hyperspectral, and LRO NAC).

```
                      [ REFERENCE IMAGE ]               [ MOVING IMAGE ]
                     (Fixed Coordinate Frame)        (Image to Transform)
                                |                              |
                                +--------------+---------------+
                                               |
                                               v
                                   [ 01 INPUT VALIDATION ]
                                               |
                                               v
                                   [ 02 PREPROCESSING ]
                                   (Norm + CLAHE + Denoise)
                                               |
                                               v
                                   [ 03 FEATURE EXTRACTION ]
                                   (OpenCV SIFT Baseline)
                                               |
                                               v
                                   [ 04 FEATURE MATCHING ]
                                   (BFMatcher / FLANN 2-NN)
                                               |
                                               v
                                   [ 05 RATIO FILTERING ]
                                   (Lowe's Ratio Test: d1 < 0.75*d2)
                                               |
                                               v
                                [ 06 GEOMETRIC VERIFICATION ]
                                (RANSAC Homography / Affine)
                                               |
                                               v
                                  [ 07 SPATIAL BALANCING ]
                                (N x N Grid Capping & Coverage)
                                               |
                                               v
                                [ 08 TRANSFORMATION & WARP ]
                                (cv2.warpPerspective to Reference)
                                               |
                                               v
                                  [ 09 OUTPUT SYNTHESIS ]
                                (Registered + Overlay + Diff)
                                               |
                                               v
                                [ 10 QUANTITATIVE METRICS ]
                                (RMSE, Inliers, Spatial Coverage,
                                 Confidence Rating & Fail-Safe)
```

---

## 2. Core Operational Modes

LunarMatch exposes three clearly delineated execution modes:

### Mode 1: LIVE BASELINE (`metric_mode: MEASURED`)
- Uses actual FastAPI + OpenCV implementation:
  1. Grayscale conversion and intensity normalization
  2. Contrast Limited Adaptive Histogram Equalization (CLAHE)
  3. Bilateral noise filtering
  4. SIFT multiscale extrema feature detection and 128D orientation descriptors
  5. Exhaustive Brute-Force L2 or FLANN KD-Tree 2-NN correspondence matching
  6. Dual-pass Lowe's ratio test filter
  7. RANSAC robust homography/affine estimation with condition number and determinant checks
  8. $N \times N$ spatial grid balancing
  9. Warping into the reference coordinate system
  10. Measured reprojection RMSE calculation over inliers

### Mode 2: DEMO SIMULATION (`metric_mode: SIMULATED`, `seed: 26166`)
- Deterministic simulation engine for advanced/future research algorithms (RIFT, SuperPoint, SuperGlue).
- Visibly displays `SIMULATED PIPELINE`.
- Never claims that neural networks or unvalidated research models actually executed.
- Seed `26166` guarantees identical reproducible presentation outputs for identical inputs.

### Mode 3: LOCAL FALLBACK (`LOCAL DEMO`)
- Zero-network client-side fallback used when the backend is offline.
- Serves bundled demo assets (`pair_a_ref.png`, `pair_a_mov.png`) and deterministic demo telemetry.
- Visibly displays `LOCAL DEMO` (never claims "ONLINE" or "LIVE AI").

---

## 3. Scientific Terminology Preservation
- **Reference Image:** The fixed reference coordinate system. Never transformed.
- **Moving Image:** The image mapped into the reference coordinate system.
- **Keypoint:** 2D feature location with scale and orientation.
- **Descriptor:** 128-dimensional floating-point representation.
- **Candidate Match:** Raw 2-NN descriptor match.
- **Filtered Match:** Match passing Lowe's ratio test.
- **Inlier:** Geometrically verified match satisfying RANSAC consensus.
- **Spatial Coverage:** Percentage of uniform grid cells occupied by valid inliers.
- **Registration Confidence:** Prototype-level quality indicator derived from measurable metrics (NOT an AI probability).
