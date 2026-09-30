# LunarMatch — Quantitative Metrics & Reliability Formulations

Every metric displayed in LunarMatch originates from mathematical calculation over confirmed inliers or deterministic simulation. Hardcoded numbers are prohibited.

---

## 1. Metric Definitions

### 1. Keypoint Counts
- **Keypoints (Reference):** Total feature interest points extracted from the fixed reference image ($N_{ref}$).
- **Keypoints (Moving):** Total feature interest points extracted from the moving image ($N_{mov}$).

### 2. Match Pipeline Counts
- **Candidate Matches:** Raw nearest-neighbor pairs identified in 128D descriptor space.
- **Filtered Matches:** Correspondences passing Lowe's ratio test:
  $$d_1 < \tau_{ratio} \cdot d_2 \quad (\text{typically } \tau_{ratio} = 0.75)$$
- **RANSAC Inliers:** Correspondences whose reprojection error satisfies the consensus threshold $\tau_{ransac}$:
  $$\|\mathbf{x}_i^{ref} - T(\mathbf{x}_i^{mov})\| \le \tau_{ransac}$$

### 3. Inlier Ratio (%)
Calculated strictly as:
$$\text{Inlier Ratio} = \left( \frac{N_{inliers}}{N_{filtered}} \right) \times 100\%$$

### 4. Spatial Coverage (%)
The reference image domain is partitioned into an $N \times N$ grid of uniform cells:
$$\text{Spatial Coverage} = \left( \frac{\text{Occupied Grid Cells}}{\text{Total Grid Cells}} \right) \times 100\%$$
- Reported both **Before** and **After** spatial balancing.
- **Coverage Gain (%):** $\text{Coverage}_{after} - \text{Coverage}_{before}$.

### 5. Reprojection Root Mean Square Error (RMSE)
Computed over all verified inliers $M$:
$$\text{RMSE} = \sqrt{ \frac{1}{M} \sum_{i=1}^M \|\mathbf{x}_i^{ref} - \hat{\mathbf{x}}_i^{ref}\|^2 }$$
- **Rule B Compliance:** If registration is rejected as unreliable, RMSE is reported as **N/A** (never a fabricated number).

---

## 2. Confidence Indicator vs AI Probabilities
Registration confidence is a **prototype quality index** computed as a weighted composite score:
$$S_{conf} = 0.35 \cdot \tilde{N}_{inliers} + 0.25 \cdot \tilde{R}_{inlier} + 0.25 \cdot \tilde{C}_{spatial} + 0.15 \cdot \tilde{E}_{rmse}$$

- **HIGH:** $S_{conf} \ge 0.70$, inliers $\ge 25$, RMSE $\le 3.5\text{ px}$.
- **MEDIUM:** $S_{conf} \ge 0.45$, inliers $\ge 14$, RMSE $\le 5.0\text{ px}$.
- **LOW:** Inliers $\ge 8$, inlier ratio $\ge 10\%$.
- **REJECTED (`NOT_RELIABLE`):** Inliers $< 8$, ratio $< 10\%$, coverage $< 15\%$, or ill-conditioned transformation.
