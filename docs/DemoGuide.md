# LunarMatch — Hackathon Jury Demonstration Guide

**Target:** Smart India Hackathon 2026 | **Problem Statement:** 26166 | **Team:** LunarMatch | **Organization:** ISRO

---

## 1. Quick Presentation Flow (5-Minute Walkthrough)

### Step 1: Mission Control Introduction (0:00 - 0:45)
- Open LunarMatch.
- Note the dark Space Research aesthetic designed for planetary mission operations.
- Point out the engine status indicator:
  - `FASTAPI ONLINE` when connected to live computer vision backend.
  - `LOCAL DEMO` when running offline with bundled assets.

### Step 2: Image Ingestion & Terminology (0:45 - 1:30)
- Navigate to **IMAGE REGISTRATION**.
- Load **Demo Pair A — Synthetic Lunar Prototype**:
  - Reference Image: Simulated OHRC Optical (Fixed Coordinate System).
  - Moving Image: Simulated TMC-2 Stereo (Image to Transform).
- Emphasize scientific honesty: explain that demo pairs are clearly labeled as synthetic prototypes with known ground-truth affine perturbations.
- Demonstrate the **SWAP** button, showing how terminology is preserved.

### Step 3: Pipeline Configuration (1:30 - 2:15)
- Click **CONFIGURE PIPELINE**.
- Show the distinction between **SIFT Baseline [IMPLEMENTED]** and advanced research models **RIFT [SIMULATED]** and **SuperPoint [SIMULATED]**.
- Enable **CLAHE Preprocessing** (essential for lunar shadows) and **Spatial Balancing (6 × 6 Grid)**.
- Choose **Homography (8-DOF)** geometric model.

### Step 4: Live 10-Stage Pipeline Execution (2:15 - 3:00)
- Click **RUN LUNARMATCH PIPELINE**.
- Watch the 10 sequential pipeline stages animate:
  `Input Validation` $\rightarrow$ `Preprocessing` $\rightarrow$ `Extraction` $\rightarrow$ `Matching` $\rightarrow$ `Ratio Filter` $\rightarrow$ `RANSAC` $\rightarrow$ `Spatial Balancing` $\rightarrow$ `Transformation` $\rightarrow$ `Registration` $\rightarrow$ `Metrics`.
- Notice the elapsed latency per stage.

### Step 5: Registration Result & Alpha Comparison (3:00 - 3:45)
- Inspect the **Results Dashboard**:
  - `REGISTRATION SUCCESSFUL` badge with high-confidence score.
  - Test the **Alpha Overlay Slider (0% to 100%)** blending Reference and Registered images.
  - Switch to **DIFF** to view the false-color difference map highlighting alignment precision.
  - Review measured quantitative metrics: Keypoints, Inliers, Inlier Ratio, Spatial Coverage, and Reprojection RMSE.

### Step 6: Correspondence & Spatial Coverage (3:45 - 4:15)
- Open **VIEW CORRESPONDENCES**:
  - Switch tabs: `CANDIDATES` $\rightarrow$ `FILTERED` $\rightarrow$ `RANSAC INLIERS` $\rightarrow$ `BALANCED`.
- Open **SPATIAL GRID**:
  - Toggle `BEFORE` vs `AFTER` balancing.
  - Explain how spatial balancing prevents over-clustering along sharp crater rims while supporting adjacent mare plains.

### Step 7: Robustness Lab & Fail-Safe Integrity (4:15 - 5:00)
- Open **ROBUSTNESS LAB**:
  - Select **Illumination** variation and click **RUN EXPERIMENT SWEEP**.
  - Show the degradation curve plotting inlier ratio and spatial coverage against illumination shift.
- Open **ENGINE CAPABILITIES**:
  - Walk the jury through the honest capabilities matrix showing `IMPLEMENTED`, `SIMULATED`, and `PLANNED` components.
  - Conclude: *"Working software > fancy claims. Evidence > assertions."*
