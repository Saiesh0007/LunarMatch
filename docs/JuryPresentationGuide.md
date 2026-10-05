# LunarMatch — Jury Presentation Guide
**Smart India Hackathon 2026** | **Problem Statement:** 26166 | **Organization:** ISRO
**Project:** LunarMatch — Multi-Modal Lunar Image Correspondence & Registration Engine
**Team:** Spectrum | **Domain:** Space Technology

---

## 1. Problem and Approach

Registering lunar orbital images across sensors and acquisitions is hard because:

1. **Illumination changes.** Shadows inside craters move, shrink or reverse
   between passes, so intensity-based descriptors disagree.
2. **Sensor and resolution gaps.** OHRC (0.25–0.3 m), TMC-2 (5 m) and IIRS (80 m,
   256 infrared bands) see the same ground very differently.
3. **Feature clustering.** High-contrast crater rims attract most keypoints and
   leave smooth mare plains unconstrained.
4. **Imperfect geolocation.** Label coordinates alone are not enough — on our
   real TMC-2 / IIRS pair they disagree by ~8 km.

LunarMatch answers with:
- **Illumination-tolerant features** — RIFT2 phase congruency (default), HOPC,
  plus SuperPoint / SuperGlue / LightGlue when their weights are installed.
- **Dense structural registration (CFOG)** for cross-sensor pairs where sparse
  features fail — automatically, as a fallback.
- **MAGSAC++**, thin-plate-spline correction, sub-pixel refinement and uniform
  spatial grid balancing.
- **Native Chandrayaan-2 PDS4 ingestion** — GSD, Sun angles and footprints from
  the ISRO labels; raw `.img` / `.qub` read directly.
- **Measured quality and a fail-safe** — every run is scored, and unreliable
  pairs are rejected as `NOT_RELIABLE` with the reasons.

---

## 2. 30-Second Pitch

> *"Registering Chandrayaan-2 images across OHRC, TMC-2 and IIRS means fighting
> moving shadows, 16-fold resolution gaps and labels that disagree by kilometres.
> LunarMatch combines illumination-tolerant phase-congruency features with a
> dense structural matcher that keeps working where feature matching breaks. On
> real TMC-2 and IIRS data from the same orbit it registers all six test windows
> to about one IIRS pixel in seven seconds each, rejects unrelated pairs, and
> reports exactly how good every result is — on a CPU, offline."*

---

## 3. Integrity Rules

| Rule | Principle | How it shows |
| :--- | :--- | :--- |
| **A** | Label what is simulated | Backend simulation runs are tagged `metric_mode: demo`, seed 26166; the web header says `FLIGHT SIMULATION` when offline; bundled reference charts say *Reference data · not your image*. |
| **B** | Metrics come from the run | Inliers, ratio, coverage and RMSE are computed from the run's matches. A rejected run reports RMSE as N/A. |
| **C** | Terminology | Reference image = fixed frame; moving image = transformed. |
| **D** | Fail-safe | `NOT_RELIABLE` when inliers < 8, inlier ratio < 10 %, coverage < 15 %, RMSE > 10 px or the matrix is unstable — with the reasons listed. |

---

## 4. Demonstration

### Web app (recommended)

Follow [DemoGuide.md §1](DemoGuide.md#1-web-demo--5-minutes). Key moments:

| Tab | Show | Say |
| :--- | :--- | :--- |
| Studio | Real TMC-2 → IIRS pair, Dense CFOG, sensors + GSD, run | *"Genuine Chandrayaan-2 data from two different instruments on the same orbit."* |
| Studio results | 98 / 100 verified matches, RMSE ≈ 0.7 px, 100 % overlap coverage, ACCEPTED | *"Every number here was computed from this run."* |
| Correspondences | Green inliers, red outliers, hover residuals | *"These are the actual matched coordinates."* |
| Studio (RIFT2) | Same pair with RIFT2 → automatic dense fallback | *"Sparse features find nothing here; the dense matcher recovers the pose."* |
| Robustness | Live sweep on your image; labelled reference charts | *"We separate live measurements from reference data."* |

<img src="screenshots/web_studio_result.png" width="100%"/>

### Mobile app

Home → Select images → Configure (feature method, matcher, geometry, grid,
preprocessing) → Execution (ten stages) → Result (banner, comparison, metrics,
matrix, report) → Spatial grid / Pipeline details → Robustness → Engine
capabilities. Without a backend it replays bundled demo results. Screen details:
[MobileApp.md](MobileApp.md).

---

## 5. Key Formulas

- **Lowe's ratio:** keep a match if $d_1 / d_2 < 0.75$.
- **Inlier ratio:** $N_{inliers} / N_{filtered} \times 100\%$.
- **Spatial coverage:** occupied cells of a 6 × 6 grid ÷ 36; the acceptance
  checklist counts only cells inside the moving image's footprint.
- **RMSE:** $\sqrt{\tfrac{1}{M}\sum_i \|\mathbf{x}^{ref}_i - \hat{\mathbf{x}}^{ref}_i\|^2}$ over verified inliers.
- **Quality index:** $S = 0.35\min(1, N/50) + 0.25\min(1, R/50\%) + 0.25\min(1, C/60\%) + 0.15\max(0, 1 - RMSE/5)$;
  HIGH needs $S \ge 0.70$, ≥ 25 inliers and RMSE ≤ 3.5 px; MEDIUM $S \ge 0.45$ and ≥ 14 inliers.

Full definitions: [Metrics.md](Metrics.md).

---

## 6. Jury Questions

### Q1: "Why not just use deep learning end to end?"
> *"We include it: SuperPoint, SuperGlue and LightGlue run on CPU with pretrained
> weights. But those models are trained on terrestrial photos; on lunar
> cross-sensor pairs they are not reliable, so they are options rather than the
> default. The default is RIFT2, designed for radiometric differences, and for the
> hardest cross-sensor cases a dense structural matcher. Everything degrades
> gracefully — missing weights fall back to RIFT2."*

### Q2: "What is your contribution beyond standard OpenCV?"
> *"Three things: a dense structural registration path that works on real
> Chandrayaan-2 cross-sensor data where feature matching fails; native PDS4
> ingestion with lunar-specific stages — polar-stereographic reprojection, GSD
> normalisation, SPICE footprint and illumination checks; and quality control
> that judges each result against its own geometry and refuses to return an
> unreliable transform."*

### Q3: "What happens with zero overlap or extreme shadow inversion?"
> *"The run ends `NOT_RELIABLE` with the failed criteria spelled out, and RMSE is
> reported as N/A. The dense matcher additionally refuses poses that a tighter
> refinement pass cannot confirm, so unrelated texture does not produce a false
> lock."*

### Q4: "Are your metrics hardcoded?"
> *"Run metrics are computed from each run and saved with every artifact under
> `backend/outputs/`. The only fixed numbers are the illustrative overview tiles
> and the robustness reference charts, which the UI labels as reference data."*

### Q5: "Have you tested on real Chandrayaan-2 data?"
> *"Yes. We read the raw ISSDC PDS4 products directly — TMC-2 at 4.9 m and the
> 256-band IIRS cube at 78 m from the same orbit — and built six co-located pairs
> along 900 km of strip. All six register, with a median error of about 1.4 IIRS
> pixels (roughly 100 m) after removing the label offset, and unrelated pairs are
> rejected. RIFT2 finds no usable matches there; the dense matcher does, in about
> 7 seconds per pair."*

### Q6: "Why not use the PDS4 label coordinates to co-locate the images?"
> *"Because the labels disagree. Registration shows the TMC-2 and IIRS label
> geolocations differ by a near-constant ~8 km along-track over the whole strip —
> six independent windows and two independent methods agree. Label-only
> co-location is off by kilometres; image registration recovers it."*

---

## 7. Five-Minute Schedule

```
┌─────────┬──────────────────────┬──────────────────────────────────────────────────┐
│ Time    │ Where                │ Action & point                                   │
├─────────┼──────────────────────┼──────────────────────────────────────────────────┤
│ 0:00    │ Overview             │ Problem, sensors, CPU-only                       │
│ 0:30    │ Studio               │ Load real TMC-2 / IIRS pair, Dense CFOG, GSDs    │
│ 1:45    │ Studio               │ Run; stages and log                              │
│ 2:15    │ Studio results       │ Metrics, split slider, difference map            │
│ 3:15    │ Correspondences      │ Green inliers, red outliers                      │
│ 3:45    │ Studio (RIFT2)       │ Automatic dense fallback on the same pair        │
│ 4:30    │ Fail-safe            │ Unrelated pair → NOT_RELIABLE with reasons       │
└─────────┴──────────────────────┴──────────────────────────────────────────────────┘
```

> **Closing:** *"LunarMatch registers real Chandrayaan-2 cross-sensor imagery on a
> CPU, measures every result, and refuses to hand over a transform it cannot
> stand behind. Thank you — we welcome your questions."*
