# Siddharth's Work Log & Architecture Map (Member 5: Spatial + Evaluation)

Welcome! This document tracks everything **Siddharth (Member 5)** builds in the **LunarMatch** project in plain and simple terms.

---

## 1. What is My Role?

In this SIH 2026 project, I am the **Spatial + Evaluation Engineer**.
My main responsibilities are:
1. **Preventing Match Clustering (Spatial Balancing):** Making sure our match points don't just bunch up in one high-contrast crater, but spread evenly across the whole lunar image.
2. **Measuring Performance (Metrics & Evaluation):** Calculating real, honest numbers like:
   - How many match points we found (Candidates vs Filtered vs Inliers).
   - What percentage of matches are geometrically valid (Inlier Ratio).
   - How well distributed the points are across the moon surface (Spatial Coverage).
   - How accurate the image alignment is (Reprojection RMSE error).
   - Overall registration confidence score (`RELIABLE`, `LOW_CONFIDENCE`, `FAILED`).

---

## 2. Modules Owned & Status

| File | Purpose | Status | Plain English Explanation |
|---|---|---|---|
| `src/spatial.py` | Spatial Balancing & Coverage | ✅ Completed & Tested | Divides the lunar image into a grid (e.g., 4x4) and ensures match points are well distributed instead of crowded into one corner. |
| `src/metrics.py` | Quantitative Evaluation | ✅ Completed & Tested | Calculates the true mathematical scores (RMSE, inlier ratio, confidence) without fake or hardcoded numbers. |
| `tests/test_spatial.py` | Unit Tests for Spatial | ✅ 10/10 Passed | Automated tests checking that spatial balancing never crashes, even with 0 points or messy data. |
| `tests/test_metrics.py` | Unit Tests for Metrics | ✅ 10/10 Passed | Automated tests verifying all mathematical formulas and transformation errors. |

---

## 3. What We Have Built (Deep Dive)

### A. Spatial Balancing & Coverage (`src/spatial.py`)
1. **Grid Mapping (`compute_grid_indices`)**:
   - Takes pixel coordinates $(x, y)$ and finds which grid cell $(row, col)$ they belong to.
2. **Coverage Calculator (`compute_spatial_coverage`)**:
   - Checks how many grid cells have at least one match point.
   - Formula: $\text{Coverage Ratio} = \frac{\text{Occupied Cells}}{\text{Total Cells}}$.
   - Calculates **distribution entropy** (measures how uniformly scattered the points are).
3. **Spatial Balancing (`spatially_balance`)**:
   - If a single crater has 100 matches, we don't need all 100 because they bias the alignment.
   - We cap each cell to the top `max_per_cell` (e.g., 10) best-quality matches.
   - Returns the filtered points for both reference and moving images.
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
     - `RELIABLE`: High inliers ($\ge 15$), high ratio ($\ge 35\%$), good coverage ($\ge 35\%$), low RMSE ($\le 3.0$ px).
     - `LOW_CONFIDENCE`: Acceptable for inspection, but marginal.
     - `FAILED`: Insufficient matches or severe error.
   - Provides clear diagnostic strings explaining why an alignment failed.
4. **All-in-One Calculation (`calculate_metrics`) & Report Formatter (`format_metrics_summary`)**:
   - Prepares clean structured results for Member 1 (Pipeline integration) and Member 6 (UI display).

---

## 4. Test Results Summary

Ran full test suite: **20 tests passed across both modules in ~0.11s**:
- `tests/test_spatial.py`: 10 passed
- `tests/test_metrics.py`: 10 passed

---

## 5. Integration Notes for Other Teammates

- **For Saiesh (Member 1 - Tech Lead / Pipeline):**
  - Call `src.spatial.spatially_balance(...)` after RANSAC or after matching.
  - Call `src.metrics.compute_reprojection_errors(...)` and `src.metrics.calculate_metrics(...)` at the end of the pipeline.
- **For Shreyash (Member 6 - UI / Demo):**
  - Use `result["metrics"]` directly for the Streamlit dashboard metrics cards.
  - Use `get_grid_visualization_boxes(...)` to render grid overlays on the before/after match plots.
