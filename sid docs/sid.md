# Siddharth's Work Log & Architecture Map (Member 5: Spatial + Evaluation)

Welcome! This document tracks everything **Siddharth (Member 5)** builds in the **LunarMatch** project in plain, simple terms.

---

## 1. What is My Role?

In this SIH 2026 project, I am the **Spatial + Evaluation Engineer**.
My main responsibilities are:
1. **Preventing Match Clustering (Spatial Balancing):** Making sure our match points don't just bunch up in one high-contrast crater, but spread evenly across the whole lunar image using Grid Capping and Adaptive Non-Maximal Suppression (ANMS).
2. **Measuring Performance (Metrics & Evaluation):** Calculating real, honest numbers like:
   - How many match points we found (Candidates vs Filtered vs Inliers).
   - What percentage of matches are geometrically valid (Inlier Ratio).
   - How well distributed the points are across the moon surface (Spatial Coverage & Distribution Entropy).
   - How accurate the image alignment is (Reprojection RMSE, MAE, Median error).
   - Overall registration confidence score (`RELIABLE`, `LOW_CONFIDENCE`, `FAILED`) with diagnostic root causes.
3. **Controlled Robustness Benchmarking (Phase 5):** Running automated ground-truth transformation experiments (Illumination, Scale, Rotation, Translation, Severe Crater Clustering) to prove spatial balancing superiority.

---

## 2. Modules Owned & Status

| File | Purpose | Status | Plain English Explanation |
|---|---|---|---|
| `src/spatial.py` | Spatial Balancing & Coverage | ✅ Completed & Tested | Divides the lunar image into a grid (e.g., 4x4) or runs continuous ANMS to ensure match points are well distributed instead of crowded into one crater. |
| `src/metrics.py` | Quantitative Evaluation | ✅ Completed & Tested | Calculates the true mathematical scores (RMSE, inlier ratio, confidence) without fake or hardcoded numbers. |
| `src/benchmark.py` | Controlled Benchmark Suite | ✅ Completed & Tested | Tests our spatial algorithms on synthetic lunar transformations with known Ground Truth $H_{\text{gt}}$ to measure exact pixel error. |
| `tests/test_spatial.py` | Unit Tests for Spatial | ✅ 12/12 Passed | Automated tests checking that grid and ANMS spatial balancing never crash and correctly spread points. |
| `tests/test_metrics.py` | Unit Tests for Metrics | ✅ 10/10 Passed | Automated tests verifying all mathematical formulas, projections, and transformation errors. |
| `tests/test_benchmark.py` | Unit Tests for Benchmark | ✅ 4/4 Passed | Automated tests verifying synthetic point pairs, ground truth transformations, and benchmark report generation. |

---

## 3. What We Have Built (Deep Dive)

### A. Spatial Balancing & Coverage (`src/spatial.py`)
1. **Grid Mapping (`compute_grid_indices`)**:
   - Takes pixel coordinates $(x, y)$ and finds which grid cell $(row, col)$ they belong to.
2. **Coverage Calculator (`compute_spatial_coverage`)**:
   - Checks how many grid cells have at least one match point.
   - Formula: $\text{Coverage Ratio} = \frac{\text{Occupied Cells}}{\text{Total Cells}}$.
   - Calculates **distribution entropy** (Shannon Entropy normalized to $[0.0, 1.0]$ measuring how uniformly scattered the points are).
3. **Spatial Balancing (`spatially_balance`)**:
   - **Method 1 - Grid Capping (`method="grid"`)**: If a single crater has 100 matches, caps each cell to the top `max_per_cell` (e.g., 5 or 10) best-quality matches.
   - **Method 2 - ANMS (`method="anms"`)**: Continuous radius suppression where suppression radius $r_i = \min_j \|p_i - p_j\|$ subject to response strength $s_j > c_{\text{robust}} \cdot s_i$. Selects points with maximal radii for optimal continuous spatial spread.
   - Returns filtered points for both reference and moving images synchronized 1:1.
4. **UI Grid Boxes (`get_grid_visualization_boxes`)**:
   - Returns coordinate boxes so Shreyash (Member 6) can draw the grid overlay in the Streamlit UI.

### B. Metrics & Evaluation (`src/metrics.py`)
1. **Coordinate Projection (`transform_points`)**:
   - Takes moving image $(x, y)$ points and projects them onto the reference frame using the calculated Homography (3x3) or Affine (2x3 or 3x3) matrix.
2. **Reprojection Error & RMSE (`compute_reprojection_errors`)**:
   - Compares the actual reference points with where the transformation placed the moving points:
     $$\text{Residual} = p_{\text{ref}} - T(p_{\text{mov}})$$
     $$\text{RMSE} = \sqrt{\frac{1}{N} \sum \|p_{\text{ref}} - T(p_{\text{mov}})\|^2}$$
   - Also computes Mean Absolute Error (MAE), Median Error, and Max Error.
3. **Registration Confidence & Fail-Safe Diagnostics (`assess_registration_confidence`)**:
   - Evaluates whether the alignment is trustworthy:
     - `RELIABLE`: High inliers ($\ge 12$), high ratio ($\ge 35\%$), good coverage ($\ge 25\%$), low RMSE ($\le 3.0$ px).
     - `LOW_CONFIDENCE`: Acceptable for inspection, but marginal.
     - `FAILED`: Insufficient matches ($< 4$) or severe error.
   - Provides clear diagnostic strings explaining why an alignment failed.
4. **All-in-One Calculation (`calculate_metrics`) & Report Formatter (`format_metrics_summary`)**:
   - Prepares clean structured results for Member 1 (Pipeline integration) and Member 6 (UI display).

### C. Controlled Benchmark Suite (`src/benchmark.py`)
1. **Ground-Truth Matrix Synthesis (`create_ground_truth_transform`)**:
   - Synthesizes exact 3x3 affine/projective transformation matrices combining rotation, uniform scale, and $(tx, ty)$ translation around center $(cx, cy)$.
2. **Lunar Point Cluster Simulation (`generate_synthetic_points_pair`)**:
   - Generates simulated lunar crater point distributions with configurable cluster ratios (e.g. 70% to 90% points in a tight crater rim) + background spread.
3. **Controlled Benchmark Comparison (`run_benchmark_experiment`)**:
   - Directly benchmarks:
     1. Raw (Unbalanced) Matches
     2. Grid Balanced Matches
     3. ANMS Balanced Matches
   - Evaluates ground-truth reprojection RMSE and spatial coverage gains.
4. **Full Robustness Battery (`run_full_robustness_benchmark_suite`)**:
   - Runs 5 distinct stress-test scenarios:
     - Pure Translation (+20, +15px)
     - Rotation (15 deg)
     - Scale (1.25x)
     - Combined Geometric Distortion (25 deg, 1.15x, +15/-10px)
     - Severe Crater Clustering (90% in one crater)
   - Exports JSON report to `outputs/metrics/benchmark_results.json`.

---

## 4. Test Results Summary

Ran full test suite: **26 tests passed across all 3 modules in 0.18s**:
- `tests/test_spatial.py`: 12 passed
- `tests/test_metrics.py`: 10 passed
- `tests/test_benchmark.py`: 4 passed

---

## 5. Integration Notes for Other Teammates

- **For Saiesh (Member 1 - Tech Lead / Pipeline):**
  - Call `src.spatial.spatially_balance(points_ref, points_mov, image_shape, method="grid"|"anms", ...)` after RANSAC or after matching.
  - Call `src.metrics.compute_reprojection_errors(...)` and `src.metrics.calculate_metrics(...)` at the end of the pipeline.
- **For Shreyash (Member 6 - UI / Demo):**
  - Use `result["metrics"]` directly for the Streamlit dashboard metrics cards.
  - Use `get_grid_visualization_boxes(...)` to render grid overlays on the before/after match plots.
  - Use `src.benchmark.run_full_robustness_benchmark_suite()` to power the benchmark evaluation tab in the dashboard.
