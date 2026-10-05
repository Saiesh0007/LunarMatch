# LunarMatch — Quantitative Metrics & Reliability Formulations

Every metric reported for a run is computed from that run — over its verified inliers in live mode, or by the seeded simulator in simulation mode (tagged `metric_mode: demo`). Fixed illustrative values appear only where noted: the web Overview tiles, the Robustness tab's charts marked *Reference data · not your image*, and the preset pairs' sample values shown during offline simulation.

---

## 1. Metric Definitions

### 1. Keypoint Counts
- **Keypoints (Reference):** Total feature interest points extracted from the fixed reference image ($N_{ref}$).
- **Keypoints (Moving):** Total feature interest points extracted from the moving image ($N_{mov}$).

### 2. Match Pipeline Counts
- **Candidate Matches:** Raw nearest-neighbour pairs in descriptor space (RIFT2 216-D, SIFT 128-D, HOPC 288-D, SuperPoint 256-D).
- **Filtered Matches:** Correspondences passing Lowe's ratio test:
  $$d_1 < \tau_{ratio} \cdot d_2 \quad (\text{typically } \tau_{ratio} = 0.75)$$
- **RANSAC Inliers:** Correspondences whose reprojection error satisfies the consensus threshold $\tau_{ransac}$:
  $$\|\mathbf{x}_i^{ref} - T(\mathbf{x}_i^{mov})\| \le \tau_{ransac}$$

### 3. Inlier Ratio (%)
Calculated strictly as:
$$\text{Inlier Ratio} = \left( \frac{N_{inliers}}{N_{filtered}} \right) \times 100\%$$

### 4. Spatial Coverage (%)
The reference image domain is partitioned into an $N \times N$ grid of uniform cells ($N = 6$ by default):
$$\text{Spatial Coverage} = \left( \frac{\text{Occupied Grid Cells}}{\text{Total Grid Cells}} \right) \times 100\%$$
- Reported both **Before** and **After** spatial balancing.
- **Coverage Gain (%):** $\text{Coverage}_{after} - \text{Coverage}_{before}$.
- **Footprint Coverage (%)** (`spatial_coverage_footprint`): the same count restricted
  to grid cells whose centres lie inside the moving image's footprint projected by
  the estimated transform:
  $$\text{Coverage}_{fp} = \frac{|\text{Occupied} \cap \text{Footprint}|}{|\text{Footprint}|} \times 100\%$$
  When a fine moving image covers only part of a coarse reference (e.g. a TMC-2
  crop inside an IIRS window), whole-grid coverage is capped by the footprint
  rather than by how well matches are spread; the footprint figure is the one
  the acceptance checklist uses and the web Studio shows.

### 5. Reprojection Root Mean Square Error (RMSE)
Computed over all verified inliers $M$:
$$\text{RMSE} = \sqrt{ \frac{1}{M} \sum_{i=1}^M \|\mathbf{x}_i^{ref} - \hat{\mathbf{x}}_i^{ref}\|^2 }$$
- **Rule B Compliance:** If registration is rejected as unreliable, RMSE is reported as **N/A** (never a fabricated number).

---

## 2. Status and Confidence (`vision/metrics.py`)

A run is **`NOT_RELIABLE`** (confidence `REJECTED`, score 0, RMSE reported as N/A)
if any of these hold:
- no transformation matrix, or the matrix fails the stability check (degenerate or mirrored determinant, ill-conditioning);
- RANSAC/MAGSAC inliers $< 8$;
- inlier ratio $< 10\%$;
- spatial coverage $< 15\%$;
- RMSE $> 10$ px.

Otherwise a **prototype quality index** (not an AI probability) is computed:
$$S_{conf} = 0.35 \cdot \min(1, \tfrac{N_{inliers}}{50}) + 0.25 \cdot \min(1, \tfrac{R_{inlier}}{50\%}) + 0.25 \cdot \min(1, \tfrac{C_{spatial}}{60\%}) + 0.15 \cdot \max(0, 1 - \tfrac{RMSE}{5\text{ px}})$$

| Result | Rule |
| :--- | :--- |
| `SUCCESSFUL`, confidence **HIGH** | $S_{conf} \ge 0.70$, inliers $\ge 25$, RMSE $\le 3.5$ px |
| `SUCCESSFUL`, confidence **MEDIUM** | $S_{conf} \ge 0.45$, inliers $\ge 14$ |
| `LOW_CONFIDENCE`, confidence **LOW** | everything else that was not rejected |

`FAILED` is used when the pipeline cannot run at all (e.g. an image cannot be read).
The API `status` comes from these rules; the separate acceptance checklist below is
written to `quality_report.json`.

---

## 3. Acceptance Checklist (`quality_report.json`)

Every run writes a per-criterion decision (`ACCEPTED` or `REGISTRATION_NOT_RELIABLE`):

| Criterion | Rule |
| :--- | :--- |
| Overlap ratio | ≥ 0.10 |
| Inlier count | ≥ 30 |
| Inlier ratio | ≥ 0.15 |
| Spatial coverage | ≥ 0.40, measured within the moving image's footprint |
| Reprojection RMSE | ≤ 2.0 px |
| Homography determinant | Expected scale $s$ known: $\det \in [0.5\,s^2,\ 2\,s^2]$. Unknown: $\det \in [0.02^2,\ 50^2]$, positive (no mirroring), singular-value anisotropy ≤ 3 |
| Condition number of H | ≤ 10⁶ |

The expected scale is 1 when both rasters were resampled to a common grid and
GSD, and $s = \text{GSD}_{moving} / \text{GSD}_{reference}$ when the request
supplies both GSDs for raw (non-georeferenced) images. Example: 19.6 m TMC-2 onto
78.32 m IIRS gives $s \approx 0.25$ and an expected determinant of ≈ 0.063.

## 4. Dense Structural Runs

When registration comes from the dense CFOG path:
- **Keypoints** are not detected (reported as 0 for an explicit dense run).
- **Candidates** are CFOG template matches on a 10 × 10 grid (up to 100).
- **Inliers** are template matches consistent with the MAGSAC++ homography.
- **Sub-pixel residuals** come from parabolic interpolation of the NCC peak.

## 5. Ground Residuals in Metres

`match_points.csv` reports `residual_meters = residual_pixels × GSD_reference`
when the reference GSD is known (from a PDS4 label, a georeferenced raster, or
`reference_gsd_m` for an image kept on its original grid); otherwise the column
is `NaN`.
