# LunarMatch — Master Jury Presentation Guide
**Smart India Hackathon 2026** | **Problem Statement:** 26166 | **Organization:** ISRO  
**Project:** LunarMatch — Multi-Modal Lunar Image Correspondence & Registration Engine  
**Team:** LunarMatch | **Domain:** Space Technology

---

## 1. Executive Summary & Problem Context

Lunar surface feature correspondence and registration between multi-modal, multi-temporal orbital sensors (e.g., Chandrayaan-2 OHRC high-resolution optical, TMC-2 stereo pairs, and IIRS hyperspectral datasets) face three fundamental photogrammetric and computational challenges:

1. **Drastic Multi-Temporal Illumination Shifts:** Changing solar azimuth and elevation angles cause shadows inside impact craters to migrate, invert, or vanish across acquisition passes. Conventional radiometric descriptors fail or produce inverted tie-points.
2. **Cross-Sensor Resolution & Scale Differentials:** Distinct ground sampling distances (GSD) and optical sensor bands prevent trivial correlation-based matching.
3. **Crater-Rim Feature Over-Clustering:** High-contrast crater edges dominate keypoint detectors (SIFT, ORB, Harris), consuming over 85% of detected tie-points while leaving adjacent planar terrains (*mare* basins) starved of constraints. This causes the computed projective transformation to fit only the local crater rim and catastrophically distort the rest of the image frame.

**LunarMatch** solves these challenges through:
* A verifiable **10-stage end-to-end computer vision pipeline** with automated **CLAHE** shadow normalization.
* Novel **Uniform Spatial Grid Balancing** to enforce spatially uniform tie-point distributions across the lunar scene.
* Real-time **reprojection RMSE and coverage metrics** computed directly from inlier coordinate transforms.
* An ISRO-grade **Fail-Safe mechanism** that formally rejects ill-conditioned or unconstrained image pairs (`NOT_RELIABLE`) rather than producing distorted scientific data.
* Transparent demarcation of **`IMPLEMENTED`** vs. **`SIMULATED`** research models to guarantee scientific honesty.

---

## 2. 30-Second Elevator Pitch for the Jury

> *"Respected Jury members, planetary image registration for lunar orbital datasets faces three severe challenges: drastic multi-temporal shadow shifts, cross-sensor radiometric differentials (such as Chandrayaan-2 OHRC vs. TMC-2 vs. IIRS), and crater-rim feature over-clustering that starves adjacent mare plains of tie-points.*
> 
> *Current tools either crash silently, generate catastrophically distorted warps, or rely on black-box deep learning that hallucinates coordinates. **LunarMatch** is an end-to-end, scientifically honest mission-control platform. It introduces **Uniform Spatial Grid Balancing**, a **10-stage verifiable OpenCV pipeline**, real-time **reprojection RMSE and coverage metrics**, and an automated **Fail-Safe mechanism** that formally rejects unreliable registrations rather than outputting false scientific data."*

---

## 3. The 4 Fundamental Scientific Rules

Always emphasize LunarMatch's commitment to **scientific honesty and ISRO-grade integrity**:

| Rule | Scientific Principle | Concrete Implementation & Proof |
| :--- | :--- | :--- |
| **Rule A** | **Scientific Honesty** | Transparently separates **`IMPLEMENTED`** (OpenCV SIFT, BF/FLANN, RANSAC, Spatial Grid) from **`SIMULATED`** (future research models like RIFT and SuperPoint). The UI, API, and logs explicitly badge simulations (Seed 26166). |
| **Rule B** | **Zero Fake Metrics** | Every RMSE, inlier count, ratio, and coverage figure is calculated live over verified inliers. If registration fails or is ill-conditioned, RMSE is reported strictly as **`N/A`**, never fabricated. |
| **Rule C** | **Terminology Preservation** | Strict adherence to planetary photogrammetry standards: **Reference Image** = Fixed coordinate system ($I_{\text{ref}}$); **Moving Image** = Image to transform ($I_{\text{mov}}$). |
| **Rule D** | **Fail-Safe Registration** | Rejects ill-conditioned pairs ($<8$ inliers, $<10\%$ inlier ratio, $<15\%$ spatial coverage, or unstable matrix determinants) as **`NOT_RELIABLE`**, preventing misleading warps from entering mission archives. |

---

## 4. Screen-by-Screen Deep Dive & Demonstration Guide

LunarMatch features 12 mission-control screens designed with an obsidian space-tech aesthetic (`#000000` dark background, high-contrast borders, and monospaced diagnostic readouts).

```
                      [ SPLASH SCREEN ]
                              │
                      [ HOME SCREEN ]
                       /      │      \
     ┌────────────────┘       │       └────────────────┐
     ▼                        ▼                        ▼
[ UPLOAD SCREEN ]    [ ROBUSTNESS LAB ]     [ ARCHITECTURE / ABOUT ]
     │                        │                        │
[ CONFIG SCREEN ]    (Sensitivity Sweeps)    (Capabilities & Rules)
     │
[ PROCESSING ] (10 Stages)
     │
[ RESULTS SCREEN ]
  ├── Interactive Visual Viewer (Ref / Registered / Overlay Alpha / Diff)
  ├── 8 Quantitative Metrics Cards
  ├── [ CORRESPONDENCE SCREEN ] (Tie-point vectors)
  └── [ SPATIAL COVERAGE SCREEN ] (Grid Balancing)
```

---

### Screen 1: Splash Screen (`splash_screen.dart`)
* **Purpose:** System boot, asset verification, and background connectivity handshaking.
* **Under the Hood:** Initializes Flutter reactive state providers (`PipelineProvider`, `LunarImageProvider`, `ExperimentProvider`) and queries the FastAPI backend health endpoint (`GET /health`) with timeout fallbacks.
* **What to Show the Jury:** Clean space-tech styling, fast load time (< 1.5s), and immediate background health probe.
* **Jury Talking Point:** *"LunarMatch boots directly into planetary mission mode, verifying backend API health in the background."*

---

### Screen 2: Mission Control Home Screen (`home_screen.dart`)
* **Purpose:** Primary command center displaying operational mode, engine health, quick demo pairs, and system navigation.
* **Under the Hood:** 
  * The top app bar features an **online heartbeat dot** and dynamic execution mode badge:
    * **`LIVE BASELINE`**: Live OpenCV FastAPI backend connected.
    * **`SIMULATED PIPELINE`**: Advanced research scenario generator (Seed 26166).
    * **`LOCAL DEMO`**: Zero-network offline fallback using bundled assets.
  * 3 quick-launch cards: **Register Lunar Images**, **Robustness Sweep Lab**, and **Architecture & Capabilities**.
* **What to Show the Jury:** Point out the `StatusBadge` in the top right. Show how the app dynamically reflects live backend connectivity.
* **Jury Talking Point:** *"Notice the engine status badge. We do not hide system state: when the backend is live, it confirms `LIVE BASELINE`; when operating standalone, it transparently declares `LOCAL DEMO`."*

---

### Screen 3: Image Selection & Ingestion (`upload_screen.dart`)
* **Purpose:** Ingestion of multi-modal lunar pairs (OHRC, TMC, TMC-2, IIRS, LRO NAC) with strict provenance tracking.
* **Under the Hood:**
  * Displays two pre-configured, procedurally synthesized lunar pairs:
    * **Demo Pair A (OHRC vs TMC-2):** Procedural crater basin with moderate rotation ($+3.5^\circ$), translation, and sensor contrast delta.
    * **Demo Pair B (LRO NAC vs IIRS):** High illumination stress pair with steep $60^\circ$ solar azimuth differential simulating multi-temporal shadow migration.
  * **"Upload Custom Images"**: Allows picking PNG, JPG, or TIFF files from disk, which are uploaded to the backend via `POST /api/v1/images/upload`.
  * **Swap Button (`⇄`)**: Inverts Reference and Moving images while strictly preserving coordinate frame semantics.
* **What to Show the Jury:** Tap **Demo Pair A**, then point to the **Provenance Card** disclosing that the images are verified synthetic prototypes with known ground-truth affine perturbations.
* **Jury Talking Point:** *"Scientific integrity starts at ingestion. We clearly disclose the synthetic provenance of our demo pairs rather than pretending they are uncalibrated raw telemetry."*

---

### Screen 4: Pipeline Configuration (`configure_screen.dart`)
* **Purpose:** Interactive parameter tuning for feature detection, matching, geometry, and preprocessing.
* **Under the Hood:**
  * **Feature Method Selection:** 
    * `SIFT Baseline [IMPLEMENTED]` — 128D scale-space extrema detector.
    * `RIFT [SIMULATED]` — Phase congruency maximum moments.
    * `SuperPoint [SIMULATED]` — Deep learned self-supervised interest points.
  * **Matcher:** Brute-Force (`BFMatcher` L2-norm) vs `FLANN` (Fast KD-Tree).
  * **Lowe's Ratio Threshold Slider:** Adjustable from $0.40$ to $0.95$ (default $0.75$).
  * **Geometric Model:** `Homography (8-DOF)` for perspective planar surfaces vs `Affine (6-DOF)` for weak perspective/orthographic approximations.
  * **Uniform Spatial Grid Balancing:** $N \times N$ grid partitioning toggle (default $6 \times 6$, max 5 features/cell).
  * **Preprocessing Toggles:** Contrast Normalization, **CLAHE** (essential for pulling features from dark crater shadows), and Gaussian Denoising.
  * **Fail-Safe Override:** Testing switch to demonstrate automated rejection.
* **What to Show the Jury:** Show the badge distinction between `[IMPLEMENTED]` and `[SIMULATED]`. Toggle CLAHE and Spatial Grid Balancing.
* **Jury Talking Point:** *"Our configuration allows mission operators to adjust sensitivity based on terrain. Notice that research algorithms like RIFT are explicitly badged as `SIMULATED`—we never claim a model ran unless it is fully compiled and executing."*

---

### Screen 5: 10-Stage Sequential Execution (`processing_screen.dart`)
* **Purpose:** Real-time visual progress through the 10 sequential pipeline stages.
* **Under the Hood:**
  * Each stage emits duration in milliseconds:
    1. `INPUT VALIDATION` (dimension, format, bit-depth verification)
    2. `PREPROCESSING` (CLAHE + min-max intensity normalization)
    3. `FEATURE EXTRACTION` (OpenCV SIFT scale-space octaves)
    4. `FEATURE MATCHING` (FLANN / BF 2-NN search)
    5. `RATIO FILTERING` (Lowe's distance ambiguity threshold: $d_1/d_2 < 0.75$)
    6. `GEOMETRIC VERIFICATION` (RANSAC consensus fitting & matrix stability check)
    7. `SPATIAL BALANCING` (Uniform grid cell sub-sampling)
    8. `TRANSFORMATION` (Planar warping matrix computation)
    9. `REGISTRATION` (Bilinear projective image re-sampling)
    10. `METRICS EVALUATION` (Reprojection RMSE & quality index computation)
* **What to Show the Jury:** Hit **Run Registration** and let the jury observe the stages completing sequentially with latency indicators.
* **Jury Talking Point:** *"Every step of the computer vision pipeline is exposed to the operator—from Lowe's ratio test to spatial grid balancing—providing complete diagnostic visibility."*

---

### Screen 6: Results & Quantitative Metrics (`results_screen.dart`)
* **Purpose:** Primary evaluation dashboard summarizing registration success, confidence, and mathematical metrics.
* **Under the Hood:**
  * Top banner shows **`REGISTRATION SUCCESSFUL`** (High Confidence) or **`REGISTRATION NOT RELIABLE`** (Fail-Safe Rejection).
  * Displays the **8-Card Quantitative Metric Grid**:
    1. **Keypoints:** Extracted reference and moving keypoints (e.g., $2001 / 2000$).
    2. **Candidate Matches:** Raw 2-NN correspondences.
    3. **Filtered Matches:** Correspondences passing Lowe's ratio test.
    4. **RANSAC Inliers:** Geometrically verified tie-points.
    5. **Inlier Ratio (%):** $(N_{\text{inliers}} / N_{\text{filtered}}) \times 100\%$.
    6. **Spatial Coverage (%):** Occupied grid cells divided by total cells.
    7. **Reprojection RMSE:** Pixel root-mean-square error ($\sqrt{\frac{1}{M}\sum \|\mathbf{x}_i^{\text{ref}} - T(\mathbf{x}_i^{\text{mov}})\|^2}$).
    8. **Runtime Latency:** High-resolution execution time in milliseconds.
* **What to Show the Jury:** Point out the **Reprojection RMSE** and the **Confidence Explanation**.
* **Jury Talking Point:** *"Every metric in this grid is computed over verified inliers. If registration fails or becomes ill-conditioned, RMSE reports as N/A rather than hallucinating an arbitrary decimal."*

---

### Screen 7: Interactive Visual Comparison (`image_comparison.dart`)
* **Purpose:** Visual validation of the registered warp against the reference target.
* **Under the Hood:**
  * Embedded directly in `results_screen.dart` with 4 interactive view modes:
    * **`REF`:** The fixed coordinate reference image.
    * **`REGISTERED`:** The moving image warped into the reference geometry via the calculated homography matrix $H$.
    * **`OVERLAY`:** Blended compositing with an interactive **Alpha Slider (0% to 100%)**. Dragging smoothly transitions between Reference and Registered images to inspect crater rim alignment.
    * **`DIFF`:** False-color absolute difference map ($|I_{\text{ref}} - I_{\text{registered}}|$). Perfectly registered regions appear uniformly dark; misalignments reveal stark bright edges.
  * Features full pan & zoom with interactive `TransformationController`.
* **What to Show the Jury:** Tap **OVERLAY** and drag the Alpha Slider back and forth. Then tap **DIFF** to show how crater rims align with zero displacement shadow.
* **Jury Talking Point:** *"Planetary scientists need qualitative visual proof alongside numbers. The Alpha Slider lets operators verify sub-pixel alignment along crater rims, while the DIFF map instantly exposes residual registration shifts."*

---

### Screen 8: Correspondence Visualization (`correspondence_screen.dart`)
* **Purpose:** Visual inspection of keypoint tie-point vectors connecting the two images.
* **Under the Hood:**
  * Uses a custom Flutter canvas painter (`MatchVisualizationWidget`) rendering a dual-pane view: Reference Image on the left, Moving Image on the right.
  * Inlier correspondence vectors are drawn as crisp connecting lines.
  * Allows filtering through 4 match stages:
    * `CANDIDATES` $\rightarrow$ `FILTERED` $\rightarrow$ `RANSAC INLIERS` $\rightarrow$ `BALANCED`.
* **What to Show the Jury:** Tap **View Correspondences**. Show the clean, parallel correspondence vectors across the lunar crater field.
* **Jury Talking Point:** *"This canvas renders the exact keypoint correspondences. Notice the absence of erratic diagonal crossover vectors—evidence of clean RANSAC consensus fitting."*

---

### Screen 9: Uniform Spatial Grid Balancing (`spatial_coverage_screen.dart`)
* **Purpose:** Explains and visualizes LunarMatch's solution to crater-rim feature clustering.
* **Under the Hood:**
  * **The Problem:** Standard feature detectors extract thousands of keypoints clustered tightly along sharp, high-contrast crater shadows, leaving flat mare plains completely empty. This causes the homography matrix to fit only the crater rim and warp the rest of the image incorrectly.
  * **The Solution:** The image is partitioned into an $N \times $N uniform grid (e.g., $6 \times 6 = 36$ cells). Each cell is capped at a maximum number of features (e.g., $k=5$), enforcing uniform spatial distribution across the entire frame.
  * Displays:
    * Grid occupancy overlay with occupied vs. vacant cells.
    * Spatial coverage percentage **Before** (e.g., 38.9%) vs **After** balancing (e.g., 77.8%).
    * Net **Coverage Gain** percentage.
* **What to Show the Jury:** Tap **Spatial Grid** from the Results screen. Show the grid overlay and explain the before/after coverage numbers.
* **Jury Talking Point:** *"This is one of our primary algorithmic contributions. Without spatial balancing, RANSAC over-fits to the high-contrast rim of one crater. By partitioning into uniform cells, we guarantee geometric constraints across the entire orbital scene."*

---

### Screen 10: Robustness Laboratory (`robustness_screen.dart`)
* **Purpose:** Automated stress-testing of the registration pipeline under controlled environmental degradation.
* **Under the Hood:**
  * Executes parameter sweeps across 5 environmental dimensions:
    1. **Illumination Shift** (simulates sun azimuth angle variations from $-50^\circ$ to $+50^\circ$).
    2. **Optical Scale** (simulates altitude/resolution differences from $0.7\times$ to $1.4\times$).
    3. **In-Plane Rotation** (simulates satellite yaw from $-30^\circ$ to $+30^\circ$).
    4. **Translation** (simulates ground track drift).
    5. **Composite Stress** (simultaneous multi-parameter variation).
  * Plots real-time degradation curves using `fl_chart`:
    * Curve 1: **Inlier Ratio Degradation (%)** vs Parameter Step.
    * Curve 2: **Spatial Coverage Retention (%)** vs Parameter Step.
* **What to Show the Jury:** Select **Illumination Variation**, hit **Run Experiment Sweep**, and show the resulting degradation curve.
* **Jury Talking Point:** *"Mission planners need to know operational limits. Our Robustness Lab runs automated sensitivity sweeps, showing the exact illumination delta threshold where feature matching degrades."*

---

### Screen 11: System Architecture (`architecture_screen.dart`)
* **Purpose:** Full technical architecture sitemap for systems engineers and technical evaluators.
* **Under the Hood:**
  * Features an interactive toggle between:
    * **Current Implemented Pipeline:** FastAPI REST backend, OpenCV SIFT engine, RANSAC, Spatial Balancer, and Flutter frontend.
    * **Target Multi-Modal Research Architecture:** Future roadmap incorporating RIFT phase congruency, deep learned SuperPoint/LoFTR features, and ISRO PDS4 archive ingestion.
* **What to Show the Jury:** Toggle between the Current Pipeline and Target Architecture.
* **Jury Talking Point:** *"We provide a clear architectural bridge between today's verified operational MVP and our planned deep-learning research extensions."*

---

### Screen 12: Engine Capabilities & Rules (`status_screen.dart` & `about_screen.dart`)
* **Purpose:** Verifiable capabilities matrix and backend network configuration.
* **Under the Hood:**
  * Tabular capabilities matrix categorizing every single subsystem as `IMPLEMENTED`, `SIMULATED`, or `PLANNED`.
  * **Backend API Configuration:** Allows setting custom API host URLs (e.g., `http://192.168.3.249:8000`) for testing physical Android APKs over local Wi-Fi.
  * Codifies the 4 Scientific Honesty rules.
* **What to Show the Jury:** Show the **Capabilities Matrix Table**. Point out that we honestly categorize what is implemented in code today versus research simulations.
* **Jury Talking Point:** *"In an engineering hackathon, integrity matters. We don't pretend a planned neural network is running if it isn't. Our capabilities matrix provides complete transparency to the evaluation committee."*

---

## 5. Mathematical Formulations of the Pipeline

### 1. Lowe's Distance Ratio Test
A candidate match pair $(p_i, q_j)$ is retained only if the distance to the nearest neighbor $d_1$ is unambiguously smaller than the distance to the second-nearest neighbor $d_2$:
$$\frac{d_1}{d_2} < \tau_{\text{ratio}} \quad (\tau_{\text{ratio}} \in [0.70, 0.80])$$

### 2. RANSAC Geometric Verification
For Homography (8-DOF), RANSAC randomly samples 4 non-collinear point pairs to estimate $H \in \mathbb{R}^{3 \times 3}$. Inliers satisfy:
$$\|\mathbf{x}_i^{\text{ref}} - \pi(H \mathbf{x}_i^{\text{mov}})\| \le \tau_{\text{ransac}} \quad (\tau_{\text{ransac}} = 3.0 \text{ px})$$
where $\pi([u, v, w]^T) = [u/w, v/w]^T$.

### 3. Inlier Ratio (%)
$$\text{Inlier Ratio} = \left( \frac{N_{\text{inliers}}}{N_{\text{filtered}}} \right) \times 100\%$$

### 4. Uniform Spatial Coverage (%)
The reference domain $\Omega$ is partitioned into an $N \times N$ grid ($N=6$, total 36 cells):
$$\text{Coverage} = \left( \frac{\sum_{c \in \text{Grid}} \mathbb{I}(|P_c| > 0)}{N^2} \right) \times 100\%$$

### 5. Reprojection Root Mean Square Error (RMSE)
Computed strictly over verified inliers $M$:
$$\text{RMSE} = \sqrt{ \frac{1}{M} \sum_{i=1}^M \|\mathbf{x}_i^{\text{ref}} - \hat{\mathbf{x}}_i^{\text{ref}}\|^2 }$$
*(If registration status is `NOT_RELIABLE`, RMSE reports strictly as `N/A`)*.

### 6. Prototype Quality Composite Index ($S_{\text{conf}}$)
$$S_{\text{conf}} = 0.35 \cdot \tilde{N}_{\text{inliers}} + 0.25 \cdot \tilde{R}_{\text{inlier}} + 0.25 \cdot \tilde{C}_{\text{spatial}} + 0.15 \cdot \tilde{E}_{\text{rmse}}$$
* **HIGH:** $S_{\text{conf}} \ge 0.70$, inliers $\ge 25$, $\text{RMSE} \le 3.5\text{ px}$.
* **MEDIUM:** $S_{\text{conf}} \ge 0.45$, inliers $\ge 14$, $\text{RMSE} \le 5.0\text{ px}$.
* **LOW:** Inliers $\ge 8$, inlier ratio $\ge 10\%$.
* **REJECTED (`NOT_RELIABLE`):** Inliers $< 8$, ratio $< 10\%$, coverage $< 15\%$, or singular matrix determinant.

---

## 6. Key Jury Questions & Defensible Answers

### Q1: "Why did you choose SIFT and Homography over end-to-end Deep Learning (like LoFTR or SuperGlue)?"
> **Answer:** *"Terrestrial deep matching models (LoFTR, SuperPoint) were trained on urban and indoor datasets. When applied to lunar orbital imagery, they frequently experience domain shift collapse—hallucinating tie-points across repetitive crater basins and getting fooled by inverted illumination shadows.  
> SIFT, enhanced with our CLAHE preprocessing and Uniform Spatial Grid Balancing, provides mathematically proven scale and rotation invariance with verifiable error bounds. Furthermore, our architecture is modular: we have already established the simulated interfaces to plug in fine-tuned lunar deep features once validated on ISRO ground-truth datasets."*

### Q2: "What is your novel contribution beyond standard OpenCV?"
> **Answer:** *"Three specific innovations:  
> 1. **Uniform Spatial Grid Balancing:** Solves the lunar crater-rim over-clustering dilemma where high-contrast edges consume 90% of inliers while adjacent mare plains remain unconstrained.  
> 2. **Multi-Criteria Fail-Safe Engine:** Automatically halts transformation and declares `REGISTRATION NOT RELIABLE` when tie-points are ill-conditioned, preventing distorted warps from corrupting planetary archives.  
> 3. **Automated Robustness Lab:** Programmatic sensitivity sweeps plotting degradation curves across illumination, scale, rotation, and translation, giving mission planners empirical operational bounds."*

### Q3: "What happens when an image pair has zero overlap or extreme shadow inversion?"
> **Answer:** *"LunarMatch triggers Rule D (Fail-Safe Rejection). Rather than forcing an ill-conditioned transformation matrix that distorts the image, the engine halts at Stage 6, marks the pair as `NOT_RELIABLE`, sets RMSE to `N/A`, and outputs clear diagnostic reasons (e.g., 'Insufficient RANSAC inliers: 3 < 8 minimum threshold; Inlier ratio below 10%')."*

### Q4: "Are your quantitative metrics hardcoded?"
> **Answer:** *"No. In live baseline execution, all metrics—keypoint counts, candidate matches, inliers, inlier ratio, spatial coverage percentage, and reprojection RMSE—are computed dynamically by OpenCV and NumPy from real pixel coordinate residuals. In research simulation mode, values are algorithmically derived from the empirical illumination differences between the images under seed 26166 and clearly badged as SIMULATED."*

---

## 7. Recommended 5-Minute Demonstration Schedule

```
┌─────────┬──────────────────────────┬────────────────────────────────────────────────────────┐
│ Time    │ Screen                   │ Action & Key Pitch Point                               │
├─────────┼──────────────────────────┼────────────────────────────────────────────────────────┤
│ 0:00    │ Home Screen              │ Problem Statement 26166 + 4 Scientific Honesty Rules   │
│ 0:45    │ Image Selection (Upload) │ Demo Pair A Provenance + Sensor Semantics (OHRC/TMC-2) │
│ 1:30    │ Configuration Screen     │ Feature Method [IMPLEMENTED] vs [SIMULATED] + CLAHE    │
│ 2:15    │ Processing Screen        │ Run 10-Stage Sequential Execution with Latency         │
│ 3:00    │ Results Screen           │ Results Badge + Reprojection RMSE + Alpha Slider / DIFF│
│ 3:45    │ Spatial Grid & Match     │ Uniform Spatial Grid Balancing + Inlier Vectors        │
│ 4:15    │ Robustness Lab & Status  │ Run Illumination Sweep + Show Capabilities Matrix      │
│ 4:50    │ Conclusion               │ "Working software > claims. Evidence > assertions."    │
└─────────┴──────────────────────────┴────────────────────────────────────────────────────────┘
```

> **Final Closing Statement:**  
> *"LunarMatch delivers working software over claims, verifiable evidence over assertions, and mission-ready integrity for planetary exploration. Thank you, and we welcome your questions."*
