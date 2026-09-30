# LunarMatch — Design System & UI/UX Guidelines

## Space Research / Mission Control Aesthetic
LunarMatch is designed as a serious scientific instrument rather than a generic SaaS product.

### 1. Color Palette
- **Deep Space Cosmic Background:** `#0A0E17`
- **Surface Elevation 1 (Cards):** `#111827`
- **Surface Elevation 2 (Controls):** `#1E293B`
- **Primary Telemetry Accent:** `#00E5FF` (Cyan)
- **Secondary Orbital Accent:** `#38BDF8` (Blue)
- **Scientific Status:**
  - **Success / Validated:** `#10B981` (Emerald)
  - **Warning / Simulation / Degraded:** `#F59E0B` (Amber)
  - **Failure / Unreliable / Outlier:** `#EF4444` (Coral Red)
  - **Neutral / Borders:** `#2E3D52` / `#475569`

### 2. Typography
- **Headings & Badges:** Bold uppercase with deliberate letter spacing (0.8–1.5).
- **Body & Captions:** High readability clean sans-serif with comfortable line height (1.3–1.5).
- **Telemetry & Coordinates:** Technical monospaced typography (`Courier`, `monospace`) for keypoint counts, coordinates, inlier ratios, and RMSE figures.

### 3. Visual Information Hierarchy
1. **Registration Result Status:** Large, unambiguous badge (`REGISTRATION SUCCESSFUL` or `REGISTRATION NOT RELIABLE`).
2. **Interactive Registered Canvas:** Zoomable & pannable comparison viewer with instant toggles for Reference, Registered, Alpha Overlay (0–100% slider), and Difference Map.
3. **Quantitative Metrics Grid:** Clear cards for keypoints, candidates, filtered matches, RANSAC inliers, inlier ratio, spatial coverage, reprojection RMSE, and latency.
4. **Interactive Analytical Tools:** Dedicated screens for correspondence line inspection, spatial grid balancing before/after overlays, and synthetic parameter sweeps.

### 4. Responsiveness & QA Constraints
- All scrollable views wrap content inside `SingleChildScrollView` to eliminate RenderFlex overflow.
- Adaptive grids leverage `LayoutBuilder` and `Wrap` to scale seamlessly from 4.7" Android phones to tablets and Windows desktop windows.
