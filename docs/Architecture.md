# LunarMatch — Architecture

**Target:** Smart India Hackathon 2026 | **Problem Statement:** 26166 | **Organization:** ISRO | **Domain:** Space Technology

---

## 1. System Overview

```
 ┌──────────────────────┐      ┌──────────────────────┐
 │  Web app (Next.js)   │      │ Mobile app (Flutter) │
 │  web/  :3000         │      │ mobile/              │
 └──────────┬───────────┘      └──────────┬───────────┘
            │      HTTP / JSON (REST)      │
            └──────────────┬───────────────┘
                           ▼
              ┌──────────────────────────┐
              │  FastAPI backend :8000   │
              │  backend/app             │
              │  ├─ api/        routes   │
              │  ├─ services/   pipeline │
              │  ├─ vision/     CV core  │
              │  ├─ io/         PDS4/TIF │
              │  └─ evaluation/ QA       │
              └────────────┬─────────────┘
                           ▼
        backend/outputs/run_<id>/   (per-run artifacts)
        backend/data/raw/           (uploaded images)
        backend/experiments/results (robustness sweeps)
```

- **Backend** — runs the registration pipeline on CPU and persists every run.
- **Web app** — Overview, Studio (run registrations), Correspondences, Robustness,
  Architecture. See [WebApp.md](WebApp.md).
- **Mobile app** — 13 screens covering the same workflow plus capabilities and
  backend settings, with an offline demo. See [MobileApp.md](MobileApp.md).

Terminology: the **reference image** is the fixed coordinate frame; the
**moving image** is transformed into it. All transforms map moving → reference.

---

## 2. Pipeline

`POST /api/v1/pipeline/run` (`app/services/pipeline_service.py`) executes the
stages below. The order is taken from a real run's `match_decisions.jsonl`; each
stage writes a log entry there. The API response groups them into ten coarse
stages (INPUT VALIDATION … METRICS) for display.

| # | Stage (log name) | Module | What it does |
| :- | :--- | :--- | :--- |
| 1 | `pds_meta` | `io/pds_reader.py` | Reads PDS4 labels (request paths or `<image>.xml`): instrument, GSD, Sun angles, corners. |
| 2 | `crs` | `services/lunar_crs.py` | For georeferenced rasters: reprojects both images to lunar polar stereographic (pole chosen from the scene's hemisphere). Plain PNG/JPG uploads skip this. |
| 3 | `input_quality` | `services/input_quality.py` | Rejects crops with too little valid data (see §4). |
| 4 | `gsd_norm` | `services/resolution.py` | Resamples georeferenced rasters to a common GSD. |
| 5 | `overlap` | `services/quality.py` | Footprint overlap estimate. |
| 6 | `spice_build`, `spice`, `footprint_validation` | `services/spice_kernel_build.py`, `spice_kernels.py`, `footprint_validation.py` | Synthesizes SPICE kernels and validates the orbital pair geometry / footprints. |
| 7 | `illumination` | `services/illumination.py` | Sun-angle compatibility of the pair (from SPICE or PDS metadata). |
| 8 | `radiometric_norm` | `services/radiometric_norm.py` | Cross-modal histogram matching. |
| 9 | `depth_optical` | `services/rift2.py` | Depth-aware preprocessing when the routing config pairs a depth product with optical imagery. |
| 10 | `shadow` | `services/shadow_mask.py` | Shadow mask. |
| 11 | `terrain_corr` | `services/terrain_correction.py` | Cosine terrain correction (uses a DEM when `LM_DEM_DIR` is set). |
| 12 | feature extraction (`rift2` / `superpoint` / …) | `vision/rift2.py`, `sift_extractor.py`, `hopc.py`, `superpoint_extractor.py` | Keypoints and descriptors for the selected `feature_method` (none for `dense`). |
| 13 | `scale_space` | `services/pyramid.py` | Keypoint telemetry over the phase-congruency octave pyramid (skipped for dense runs). |
| 14 | `hypnet` | `services/hypnet.py` | Descriptor modulation by global context. |
| 15 | `matching` | `vision/matcher.py`, `superglue_matcher.py`, `lightglue_matcher.py` | BF / FLANN 2-NN + Lowe's ratio test, or SuperGlue / LightGlue. |
| 16 | `scdf_gates` | `services/scdf_gates.py` | Self-calibrating gates that filter matches before estimation. |
| 17 | `magsac` | `vision/geometry.py` | MAGSAC++ (or RANSAC) homography / affine with matrix stability checks. |
| 18 | `dense_structural` | `vision/dense_structural.py` | Dense CFOG registration — explicit (`feature_method: dense`) or when sparse matching did not verify (see §3). |
| 19 | `tps` | `services/tps.py` | Thin-plate-spline residual correction. |
| 20 | `subpixel` | `refinement/subpixel.py` | Phase-correlation sub-pixel refinement (dense runs use NCC peak interpolation instead). |
| 21 | spatial balancing | `vision/spatial.py` | N × N grid (default 6 × 6), at most 5 matches per cell. |
| 22 | warp and outputs | `vision/registration.py` | Registered, overlay, difference and correspondence images. |
| 23 | metrics and decision | `vision/metrics.py`, `evaluation/quality.py` | Status, confidence and the acceptance checklist ([Metrics.md](Metrics.md)). |

Each sparse stage degrades instead of failing the run: missing learned-model
weights fall back to RIFT2, an unavailable CRS skips reprojection, and so on —
the fallback is recorded in the stage log.

### Feature methods and matchers

| `feature_method` | Extraction |
| :--- | :--- |
| `rift2` (default), `rift2_multiscale` | RIFT2 phase congruency, 216-D descriptors |
| `sift` | OpenCV SIFT, 128-D |
| `hopc`, `hopc_rift2_fusion` | HOPC structural descriptor (288-D), optionally fused with RIFT2 |
| `both` | RIFT2 primary, SIFT fallback |
| `superpoint` | SuperPoint (PyTorch, `weights/superpoint_v1.pth`) |
| `superglue` | SIFT keypoints (the learned SuperGlue matcher is selected with `matcher: superglue`) |
| `dense` | No keypoints — dense CFOG registration |

| `matcher` | Matching |
| :--- | :--- |
| `BF` (default), `FLANN` | 2-NN + Lowe's ratio test |
| `superglue` | SuperPoint + SuperGlue graph neural network (PyTorch, outdoor weights) |
| `lightglue` | SuperPoint + LightGlue (PyTorch) |

Learned weights are downloaded by `backend/scripts/download_weights.py`.

### Sensor routing

`services/router.py` detects each image's sensor from PDS4 metadata, or from the
sensors the request declares explicitly, and selects a per-pair configuration
(preprocessing, scale space, Hyp-Net, TPS, …). Undetected sensors use the
generic configuration.

---

## 3. Dense Structural Registration

Sparse descriptors return almost no correct matches when sensor, epoch, Sun
geometry and resolution all differ (measured on real Chandrayaan-2 TMC-2 / IIRS
pairs, [RealData.md](RealData.md)). The dense path (CFOG, Ye et al. TGRS 2019):

1. **Coarse search** over scale, rotation and translation on smoothed
   gradient-magnitude maps. A GSD prior (`gsd_moving / gsd_reference`) narrows
   the scale range; co-projected rasters fix scale 1 and rotation 0.
2. **Hypothesis ranking:** each coarse candidate is refined locally and scored by
   a quick 6 × 6 verification pass.
3. **Fine matching** on a 10 × 10 grid of CFOG patches (8 unsigned orientation
   channels, so reversed shading under a different Sun azimuth still matches),
   with sub-pixel peak interpolation and peak-distinctiveness gating.
4. **MAGSAC++ homography**, iterated with a shrinking search radius
   (wide → 8 px → 3 px). A pose is accepted only if a tighter pass confirms it —
   the wide first pass tolerates ~3.5 px and can agree by chance on unrelated
   texture.
5. **Checks:** at least 12 verified correspondences and a homography with
   bounded anisotropy.

`dense_fallback` (default `true`) triggers it when sparse matching yields no
stable matrix with at least 12 inliers.

---

## 4. Input Quality Gate

Missing pixels are split into **fill** — nodata connected to the raster border,
i.e. padding around a rotated or map-projected footprint — and **bad** pixels
inside the footprint. A crop is rejected when bad pixels exceed 20 % of the
footprint or the valid footprint covers less than 25 % of the raster.

- Sentinels: declared nodata, NaN, −9999, −32768, and 0 for uint16.
- 8-bit 0/255 count as padding only when every colour channel has that value and
  the region touches the border (interior 0/255 are shadow or glare).
- Alpha channels mark transparent pixels as missing and are never read as data.

---

## 5. Execution Modes

| Mode | Where | What runs |
| :--- | :--- | :--- |
| **Live** | backend | The full pipeline above (`metric_mode: measured`). |
| **Simulation** | backend, `simulation_mode: true` | `DeterministicSimulator` (seed 26166) synthesizes correspondences and metrics from image statistics instead of running feature matching; tagged `metric_mode: demo`, `simulation_seed: 26166`. |
| **Web offline** | web, backend unreachable | Header shows FLIGHT SIMULATION; the Studio animates the stages and shows the preset pair's sample values. |
| **Mobile local demo** | mobile, backend unreachable | `LocalDemoSimulator` serves bundled demo results. |

See [Simulation.md](Simulation.md).

---

## 6. Run Artifacts

Every run writes `backend/outputs/run_<id>/`:

| File | Content |
| :--- | :--- |
| `configuration.json`, `input_metadata.json`, `run_manifest.json` | Request, image metadata, manifest |
| `keypoints_reference.json`, `keypoints_moving.json` | Keypoints |
| `matches_candidate.json`, `matches_filtered.json`, `matches_inliers.json`, `matches_spatial.json` | Matches at each stage |
| `match_points.csv` | Inlier coordinates, pixel and metre residuals |
| `match_decisions.jsonl` | One log entry per stage (and per rejected match) |
| `metrics.json`, `quality_report.json`, `experiment_log.json` | Metrics, acceptance checklist, full run log |
| `registered.png`, `overlay.png`, `difference.png`, `correspondences.png` | Images |
| `ref_crs.tif`, `mov_crs.tif`, `ref_gsd.tif`, `mov_gsd.tif` | Reprojected / resampled rasters (georeferenced inputs only) |

JSON schemas for some artifacts are in `docs/schemas/`. A Markdown report is
served at `GET /api/v1/results/{run_id}/report`; `scripts/finale_run.py`
generates an HTML report (`report.html`).
